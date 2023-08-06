import pandas as pd
import pytest
from typing import List
from dataclasses import dataclass

from arthurai.core.attributes import ArthurAttribute
from arthurai.common.constants import ValueType, Stage
from arthurai.datasets import ArthurExample


@dataclass
class S3ExampleDataTestCase:
    example_name: str
    input_attrs: List[ArthurAttribute]
    gt_attrs: List[ArthurAttribute]
    pred_attrs: List[ArthurAttribute]
    non_input_attrs: List[ArthurAttribute]


NEW_CREDIT_CARD_DEFAULT_DRIFTY_INPUT_ATTRIBUTES = \
    [ArthurAttribute(name="LIMIT_BAL", value_type=ValueType.Integer, stage=Stage.ModelPipelineInput)] +\
    [ArthurAttribute(name=f"PAY_{i}", value_type=ValueType.Integer, stage=Stage.ModelPipelineInput) for i in
     [0, 2, 3, 4, 5, 6]] +\
    [ArthurAttribute(name=f"BILL_AMT{i}", value_type=ValueType.Integer, stage=Stage.ModelPipelineInput) for i in
     [1, 2, 3, 4, 5, 6]] +\
    [ArthurAttribute(name=f"PAY_AMT{i}", value_type=ValueType.Integer, stage=Stage.ModelPipelineInput) for i in
     [1, 2, 3, 4, 5, 6]]

NEW_CREDIT_CARD_DEFAULT_DRIFTY = S3ExampleDataTestCase(
    "new_credit_card_default_drifty",
    NEW_CREDIT_CARD_DEFAULT_DRIFTY_INPUT_ATTRIBUTES,
    [ArthurAttribute(name="ground_truth_credit_default", value_type=ValueType.Integer, stage=Stage.GroundTruthClass)],
    [ArthurAttribute(name="pred_proba_credit_default", value_type=ValueType.Float, stage=Stage.PredictedValue)],
    [ArthurAttribute(name=name, value_type=ValueType.Integer, stage=Stage.NonInputData) for name in ["ID", "MARRIAGE", "EDUCATION", "AGE", "SEX"]]
)

ELECTRICITY_INPUT_ATTRIBUTES = [
    ArthurAttribute(name=name, value_type=ValueType.Float, stage=Stage.ModelPipelineInput)
    for name in ["date", "period", "nswprice", "nswdemand", "vicprice", "vicdemand", "transfer"]] + [
    ArthurAttribute(name="day", value_type=ValueType.Integer, stage=Stage.ModelPipelineInput)
]

ELECTRICITY = S3ExampleDataTestCase(
    "electricity",
    ELECTRICITY_INPUT_ATTRIBUTES,
    [ArthurAttribute(name="price_increase", value_type=ValueType.Integer, stage=Stage.GroundTruthClass)],
    [ArthurAttribute(name="pred_price_increase", value_type=ValueType.Float, stage=Stage.PredictedValue)],
    []
)

BOSTON_HOUSING_INPUT_ATTRIBUTES = [
    ArthurAttribute(name=name, value_type=ValueType.Float, stage=Stage.ModelPipelineInput)
    for name in ["crim", "zn", "indus", "nox", "rm", "age", "dis", "ptratio", "bb", "lstat"]] + [
    ArthurAttribute(name=name, value_type=ValueType.Integer, stage=Stage.ModelPipelineInput)
    for name in ["chas", "rad", "tax"]
]

BOSTON_HOUSING = S3ExampleDataTestCase(
    "boston_housing",
    BOSTON_HOUSING_INPUT_ATTRIBUTES,
    [ArthurAttribute(name="medv", value_type=ValueType.Float, stage=Stage.GroundTruth)],
    [ArthurAttribute(name="pred_medv", value_type=ValueType.Float, stage=Stage.PredictedValue)],
    []
)

EXAMPLE_DATASETS = [
    NEW_CREDIT_CARD_DEFAULT_DRIFTY,
    ELECTRICITY,
    BOSTON_HOUSING
]


@pytest.mark.parametrize("example_dataset", EXAMPLE_DATASETS)
def test_s3_example(example_dataset: S3ExampleDataTestCase):
    example_name = example_dataset.example_name
    input_attributes = example_dataset.input_attrs
    gt_attributes = example_dataset.gt_attrs
    pred_attributes = example_dataset.pred_attrs
    non_input_attributes = example_dataset.non_input_attrs
    arthur_example = ArthurExample(example_name)
    attributes = input_attributes + gt_attributes + pred_attributes + non_input_attributes

    # assert feature name properties are correct
    assert set(arthur_example.input_attribute_names) == set([attr.name for attr in input_attributes])
    assert set(arthur_example.gt_attribute_names) == set([attr.name for attr in gt_attributes])
    assert set(arthur_example.pred_attribute_names) == set([attr.name for attr in pred_attributes])
    assert set(arthur_example.non_input_attribute_names) == set([attr.name for attr in non_input_attributes])

    # validate that the ArthurExample methods split data correctly by stage, by train-test split, and by datatype
    validate_arthur_example_method(arthur_example, arthur_example.get_dataset, attributes)
    validate_arthur_example_method(arthur_example, arthur_example.get_inputs, input_attributes)
    validate_arthur_example_method(arthur_example, arthur_example.get_ground_truth_data, gt_attributes)
    validate_arthur_example_method(arthur_example, arthur_example.get_predictions, pred_attributes)
    validate_arthur_example_method(arthur_example, arthur_example.get_non_input_data, non_input_attributes)


# run tests on a method of an ArthurExample object
# each method returns a dataframe which should correspond to the expected_attrs
def validate_arthur_example_method(arthur_example, arthur_example_method, expected_attrs: List[ArthurAttribute]):
    if not expected_attrs:
        with pytest.raises(ValueError):
            arthur_example_method()
    else:
        df = arthur_example_method()
        ref_df, inf_df = arthur_example_method(split=True)
        ref_df_even, inf_df_even = arthur_example_method(split=True, test_split_size=0.5)
        assert set(df.columns) == set([attr.name for attr in expected_attrs])
        assert not df.isnull().values.any()
        type_check_arthur_example_method_result(df, expected_attrs)
        split_check_arthur_example_method_result(arthur_example, df, ref_df, inf_df, ref_df_even, inf_df_even)


# assert that the result of the arthur_example method type-checks according to the attributes
def type_check_arthur_example_method_result(result_data: pd.DataFrame, attributes: List[ArthurAttribute]):
    for c in result_data.columns:
        attrs = [attr for attr in attributes if attr.name == c]
        assert len(attrs) == 1
        attr = attrs[0]
        if attr.value_type == ValueType.Integer:
            assert result_data[c].dtype == int
        elif attr.value_type == ValueType.Float:
            assert result_data[c].dtype == float
        elif attr.value_type == ValueType.Boolean:
            assert result_data[c].dtype == bool
        elif attr.value_type in [ValueType.String, ValueType.Unstructured_Text, ValueType.Image]:
            assert result_data[c].dtype == str


# assert that the result of the arthur_example method is train/test split correctly
def split_check_arthur_example_method_result(
        arthur_example: ArthurExample,
        result_data: pd.DataFrame,
        ref: pd.DataFrame,
        inf: pd.DataFrame,
        ref_even: pd.DataFrame,
        inf_even: pd.DataFrame
):
    default_num_ref = int((1 - arthur_example.example_schema.default_data_split_test_size) * len(result_data))
    default_num_inf = int(arthur_example.example_schema.default_data_split_test_size * len(result_data))
    assert default_num_ref - 1 <= len(ref) <= default_num_ref + 1
    assert default_num_inf - 1 <= len(inf) <= default_num_inf + 1
    assert len(result_data) // 2 - 1 <= len(ref_even) <= len(result_data) // 2 + 1
    assert len(result_data) // 2 - 1 <= len(inf_even) <= len(result_data) // 2 + 1


def test_bad_example_name():
    with pytest.raises(ValueError):
        ArthurExample("asdfjasdgkfj")
