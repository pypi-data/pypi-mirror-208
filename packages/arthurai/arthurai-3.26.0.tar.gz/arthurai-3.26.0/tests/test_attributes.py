import pytest
from tests.fixtures.models.multiclass import DOG_GROUND_TRUTH_ATTR, INT_INPUT_ATTR
from tests.fixtures.models.regression import PRED_ATTR


@pytest.mark.parametrize('attribute, expected_str', [
    (DOG_GROUND_TRUTH_ATTR, "GROUND_TRUTH[0]:dog_gt\n\tCategorical: [0, 1]\n\tLink: dog_pred"),
    (INT_INPUT_ATTR, "PIPELINE_INPUT[0]:int_input\n\tCategorical: [1, 2]"),
    (PRED_ATTR, "PREDICTED_VALUE[0]:pred\n\tRange: [23.0, 94.2]\n\tLink: ground_truth")
], ids=['categorical with link', 'categorical no link', 'range'])
def test__str__(attribute, expected_str):
    string_rep = str(attribute)
    assert string_rep == expected_str
