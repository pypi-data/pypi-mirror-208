import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import attrs
import pandas

from tecton_athena import pipeline_helper
from tecton_core import feature_set_config
from tecton_core.data_types import BoolType
from tecton_core.data_types import Float32Type
from tecton_core.data_types import Float64Type
from tecton_core.data_types import Int32Type
from tecton_core.data_types import Int64Type
from tecton_core.data_types import StringType
from tecton_core.data_types import TimestampType
from tecton_core.errors import TectonValidationError
from tecton_core.feature_definition_wrapper import FeatureDefinitionWrapper
from tecton_core.query.pandas.node import PandasExecNode
from tecton_core.query.pandas.node import SqlExecNode
from tecton_proto.args.transformation_pb2 import TransformationMode

logger = logging.getLogger(__name__)

# Maps a tecton datatype to the correct pandas datatype which is to be used when an output schema is defined by the user
PRIMITIVE_TECTON_DATA_TYPE_TO_PANDAS_DATA_TYPE = {
    Int32Type(): "int32",
    Int64Type(): "int64",
    Float32Type(): "float32",
    Float64Type(): "float64",
    StringType(): "string",
    BoolType(): "bool",
    TimestampType(): "datetime64[ns]",
}


@attrs.frozen
class PandasOdfvPipelineNode(PandasExecNode):
    input_node: Union[PandasExecNode, SqlExecNode]
    feature_definition_wrapper: FeatureDefinitionWrapper
    namespace: str
    columns: List[str]

    def _to_dataframe(self) -> pandas.DataFrame:
        input_df = self.input_node._to_dataframe()
        odfv_result_df = self._run_odfv(input_df, self.feature_definition_wrapper)
        rename_map = {}
        datatypes = {}
        output_schema = self.feature_definition_wrapper.view_schema.column_name_and_data_types()
        for column_name, datatype in output_schema:
            mapped_name = f"{self.namespace}{self.feature_definition_wrapper.namespace_separator}{column_name}"
            rename_map[column_name] = mapped_name
            if datatype in PRIMITIVE_TECTON_DATA_TYPE_TO_PANDAS_DATA_TYPE:
                datatypes[mapped_name] = PRIMITIVE_TECTON_DATA_TYPE_TO_PANDAS_DATA_TYPE[datatype]
        odfv_result_df = odfv_result_df.rename(columns=rename_map)[[*rename_map.values()]].astype(datatypes)
        data_df = input_df.merge(odfv_result_df, left_index=True, right_index=True)
        return data_df

    def _run_odfv(self, data_df: pandas.DataFrame, odfv: FeatureDefinitionWrapper) -> pandas.DataFrame:
        transformation_mode = odfv.transformations[0].transformation_mode

        odfv_pipeline = pipeline_helper.build_odfv_execution_pipeline(
            pipeline=odfv.pipeline, transformations=odfv.transformations, name=odfv.name
        )

        if transformation_mode == TransformationMode.TRANSFORMATION_MODE_PANDAS:
            odfv_inputs = self._extract_inputs_for_odfv_from_data(data_df, odfv)
            odfv_result_df = odfv_pipeline.execute_with_inputs(odfv_inputs)
            return odfv_result_df
        elif transformation_mode == TransformationMode.TRANSFORMATION_MODE_PYTHON:
            odfv_inputs = self._extract_inputs_for_odfv_from_data(data_df, odfv)

            # The inputs are currently a mapping of input_name to pandas DF
            # We need turn the ODFV inputs from a pandas DF to a list of dictionaries
            # Then we need to iterate through all rows of the input data set, pass the input dicts into the ODFV
            # And finally convert the resulting list of dicts into a pandas DF
            for input_name in odfv_inputs.keys():
                # Map pandas DFs to List of dicts (one dict per row)
                odfv_inputs[input_name] = odfv_inputs[input_name].to_dict("records")

            odfv_result_list = []

            num_rows = len(data_df)
            if num_rows > 100:
                logger.warn(
                    f"Executing ODFV {odfv.name} for {len(data_df)} rows. The ODFV will be executed row by row and may take a while to complete..."
                )

            for row_index in range(num_rows):
                # Iterate through all rows of the data and invoke the ODFV
                row_odfv_inputs = {}
                for input_name in odfv_inputs.keys():
                    row_odfv_inputs[input_name] = odfv_inputs[input_name][row_index]

                odfv_result_dict = odfv_pipeline.execute_with_inputs(row_odfv_inputs)
                odfv_result_list.append(odfv_result_dict)
            return pandas.DataFrame.from_dict(odfv_result_list)
        else:
            msg = f"ODFV {odfv.name} has an unexpected transformation mode: {transformation_mode}"
            raise TectonValidationError(msg)

    def _extract_inputs_for_odfv_from_data(
        self, data_df: pandas.DataFrame, odfv: FeatureDefinitionWrapper
    ) -> Dict[str, pandas.DataFrame]:
        odfv_invocation_inputs = {}

        odfv_transformation_node = odfv.pipeline.root.transformation_node

        for input in odfv_transformation_node.inputs:
            input_name = input.arg_name
            input_df = None

            if input.node.HasField("request_data_source_node"):
                request_context_schema = input.node.request_data_source_node.request_context.tecton_schema
                request_context_fields = [c.name for c in request_context_schema.columns]

                for f in request_context_fields:
                    if f not in data_df.columns:
                        msg = f"ODFV {odfv.name} has a dependency on the Request Data Source named '{input_name}'. Field {f} of this Request Data Source is not found in the spine. Available columns: {list(data_df.columns)}"
                        raise TectonValidationError(msg)

                input_df = data_df[request_context_fields]
            elif input.node.HasField("feature_view_node"):
                fv_features = feature_set_config.find_dependent_feature_set_items(
                    odfv.fco_container, input.node, {}, odfv.id
                )[0]
                select_columns_and_rename_map = {}
                for f in fv_features.features:
                    column_name = f"{fv_features.namespace}__{f}"
                    mapped_name = f
                    select_columns_and_rename_map[column_name] = mapped_name
                for f in select_columns_and_rename_map.keys():
                    if f not in data_df.columns:
                        msg = f"ODFV {odfv.name} has a dependency on the Feature View '{input_name}'. Feature {f} of this Feature View is not found in the retrieved historical data. Available columns: {list(data_df.columns)}"
                        raise TectonValidationError(msg)
                # Let's select all of the features of the input FV from data_df
                input_df = data_df.rename(columns=select_columns_and_rename_map)[
                    [*select_columns_and_rename_map.values()]
                ]
            else:
                msg = f"Unexpected input found ({input_name}) on ODFV {odfv.name}"
                raise Exception(msg)

            odfv_invocation_inputs[input_name] = input_df
        return odfv_invocation_inputs


@attrs.frozen
class PandasRenameColsNode(PandasExecNode):
    input_node: Union[PandasExecNode, SqlExecNode]
    mapping: Optional[Dict[str, str]]
    drop: Optional[List[str]]
    columns: List[str]

    def _to_dataframe(self) -> pandas.DataFrame:
        input_df = self.input_node._to_dataframe()
        if self.drop:
            output_df = input_df.drop(columns=self.drop)
        if self.mapping:
            output_df = input_df.rename(self.mapping)
        return output_df
