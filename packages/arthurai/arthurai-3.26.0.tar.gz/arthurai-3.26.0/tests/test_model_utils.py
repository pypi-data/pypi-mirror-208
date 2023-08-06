import pytest
from pytest import approx
import numpy as np
from arthurai.core.model_utils import tensors_to_arthur_inference

VOCAB = {
    0: "this",
    1: "is",
    2: "test"
}


@pytest.mark.parametrize('num_probs,expected_formatted', [
    (1, [approx({"this": 0.7}), approx({"test": 0.99}), approx({"test": 0.3333})]),
    (2, [approx({"this": 0.7, "is": 0.2}), approx({"test": 0.99, "is": 0.005}), approx({"test": 0.3333, "is": 0.3333})]),
    (3, [approx({"this": 0.7, "is": 0.2, "test": 0.1}), approx({"test": 0.99, "is": 0.005, "this": 0.005}),
         approx({"this": 0.3333, "is": 0.3333, "test": 0.3333})])
])
def test_tensors_to_arthur_inference(num_probs, expected_formatted):
    log_tensor = np.array([[-0.35667494, -1.60943791, -2.30258509],
                           [-5.29831737, -5.29831737, -0.01005034],
                           [-1.09871229, -1.09871229, -1.09871229]])
    arthur_likelihoods = tensors_to_arthur_inference(log_tensor, VOCAB, num_probs)
    assert arthur_likelihoods == expected_formatted


@pytest.mark.parametrize('log_tensor,num_probs', [
    (np.array([[-0.35667494, -1.2039728, -2.30258509]]), 2),
    (np.array([[-0.35667494, -1.60943791, -2.30258509]]), 6),
    (np.array([[[1], [[2]], [[3]]]]), 2)
], ids=['invalid probs', 'num probs > 5', 'invalid shape'])
def test_tensors_to_arthur_inference_invalid(log_tensor, num_probs):
    with pytest.raises(ValueError):
        tensors_to_arthur_inference(log_tensor, VOCAB, num_probs)