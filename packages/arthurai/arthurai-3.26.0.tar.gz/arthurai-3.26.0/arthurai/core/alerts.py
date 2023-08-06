from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from arthurai.common.constants import ListableStrEnum
from arthurai.common.exceptions import ArthurUserError
from arthurai.core.base import ArthurBaseJsonDataclass, NumberType


class AlertRuleBound(ListableStrEnum):
    Upper = "upper"
    Lower = "lower"


class AlertRuleSeverity(ListableStrEnum):
    Warning = "warning"
    Critical = "critical"


class AlertStatus(ListableStrEnum):
    Resolved = "resolved"
    Acknowledged = "acknowledged"


@dataclass
class AlertRule(ArthurBaseJsonDataclass):
    bound: AlertRuleBound
    threshold: NumberType
    metric_id: str
    severity: AlertRuleSeverity
    name: Optional[str] = None
    lookback_period: Optional[NumberType] = None
    subsequent_alert_wait_time: Optional[NumberType] = None
    enabled: bool = True
    id: Optional[str] = None
    metric_name: Optional[str] = None
    metric_parameters: Optional[Dict[str, Any]] = None
    filters: Optional[List[Dict[str, Any]]] = None


@dataclass
class Alert(ArthurBaseJsonDataclass):
    id: str
    timestamp: str
    metric_value: float
    message: str
    model_id: str
    status: str
    alert_rule: AlertRule
    window_start: Optional[str] = None
    window_end: Optional[str] = None
    batch_id: Optional[str] = None


class MetricType(ListableStrEnum):
    ModelOutputMetric = "model_output_metric"
    ModelInputDataMetric = "model_input_data_metric"
    ModelPerformanceMetric = "model_performance_metric"
    ModelDataDriftMetric = "model_data_drift_metric"


@dataclass
class Metric(ArthurBaseJsonDataclass):
    id: str
    name: str
    query: Dict[str, Any]
    is_default: bool
    type: Optional[MetricType] = None
    attribute: Optional[str] = None


def validate_parameters_for_alert(metric_parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Check that the supplied parameter values for an alert rule only contain one value per parameter.

    :param metric_parameters: mapping from metric parameter name to desired value
    :raises ArthurUserError: invalid parameter values supplied by user
    """
    validated_params = {}
    if metric_parameters is None:
        return validated_params

    for param, val in metric_parameters.items():
        if isinstance(val, list) or isinstance(val, tuple):
            if len(val) > 1:
                raise ArthurUserError(f"Invalid value for metric parameter {param}. "
                                      f"Parameter may have only one value but {len(val)} were requested.")
            elif len(val) == 1:
                validated_params[param] = val[0]
        elif isinstance(val, dict):
            raise ArthurUserError(f"Invalid value for metric parameter {param}. Parameter may have only one value.")
        else:
            validated_params[param] = val
    return validated_params
