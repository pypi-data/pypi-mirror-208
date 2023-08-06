from typing import List, Union, Optional

from dataclasses import dataclass

from arthurai.common.constants import ValueType, Stage
from arthurai.common.exceptions import MissingParameterError, UserValueError
from arthurai.core.base import ArthurBaseJsonDataclass


MAX_CATEGORIES_TO_SHOW = 5


def get_attribute_order_stage(attribute_stage: Stage) -> int:
    if attribute_stage == Stage.ModelPipelineInput:
        return 0
    elif attribute_stage == Stage.NonInputData:
        return 1
    elif attribute_stage == Stage.PredictedValue:
        return 2
    elif attribute_stage == Stage.GroundTruth:
        return 3
    elif attribute_stage == Stage.GroundTruthClass:
        return 4
    else:
        return 5


@dataclass
class AttributeCategory(ArthurBaseJsonDataclass):
    """
    A list of the attribute's categories. An attribute will only have categories if it is marked as categorical.
    """
    value: str
    label: Optional[str] = None

    def __post_init__(self):
        self.value = str(self.value)
        if self.label is not None:
            self.label = str(self.label)

    def __str__(self):
        return str(self.value)


@dataclass
class AttributeBin(ArthurBaseJsonDataclass):
    """
    A list of the attribute's bins. An attribute will only have bins if it is not categorical. The bin start is
     exclusive and the end is inclusive, (continuous_start, continuous_end]. Use Null to represent an open end of a bin.
    """
    continuous_start: Optional[float] = None
    continuous_end: Optional[float] = None


@dataclass
class ArthurAttribute(ArthurBaseJsonDataclass):
    """ArthurAttribute encapsulates data associated with a model attribute

    :param attribute_link: Only applicable for `GroundTruth` or `PredictedValue` staged attributes.
        If stage is equal to `GroundTruth`, this represents the associated `PredictedValue` attribute and vice versa
    :param is_positive_predicted_attribute: Only applicable for `PredictedValue` attributes on a Binary
        Classification model. Should be set to `True` on the positive predicted value attribute.
    :param is_unique: Boolean value used to signal if the values of this attribute are unique. To set an attribute to be
        unique, use :code:`arthur_model.get(name=attribute_name).set(is_unique=True)`.
    :param bins: List of bin cut-offs used to discretize continuous attributes. Use `None` as an open ended value.
        ``[None, 18, 65, None]`` represents the three following bins: ``value < 18, 18 < value < 65, value > 65``.
        To modify an attribute's bins, use :code:`arthur_model.get_attribute(name=attribute_name).set(bins=[None, cutoff_1, ..., cutoff_n, None])`.
    :param monitor_for_bias: boolean value set to `True` if the attribute should be monitored for bias. To modify an attributes's
        bias monitoring status, use :func:`arthurai.core.models.ArthurModel.set_attribute_as_sensitive()`.
    :param max_range: Max value for a continuous attribute. To modify an attribute's range, use :code:`arthur_model.get(name=attribute_name).set(range=[min_value, max_value])`.
    :param min_range: Min value for a continuous attribute. To modify an attribute's range, use :code:`arthur_model.get(name=attribute_name).set(range=[min_value, max_value])`.
    :param categorical: Boolean value set to `True` if the attribute has categorical values. To set an attribute to be
        categorical, use :code:`arthur_model.get_attribute(name=attribute_name).set(categorical=true)`.
    :param position: The array position of attribute within the stage. Required in the PREDICT_FUNCTION_INPUT stage.
    :param label: Label for attribute. If attribute has an encoded name, a more readable label can be set.
    :param stage: :class:`arthurai.common.constants.Stage` of this attribute in the model pipeline. To modify an attribute's
        stage, use :code:`arthur_model.get(name=attribute_name).set(stage=stage_value)`. See :class:`arthurai.common.constants.Stage`
        for the different stage values an attribute can have.
    :param value_type: :class:`arthurai.common.constants.ValueType` associated with this attributes values. Non-modifiable.
    :param name: Name of the attribute. Attribute names can only contain alpha-numeric characters and underscores
        and cannot start with a number. To modify an attribute's name, use :func:`arthurai.core.models.ArthurModel.rename_attribute()`.
    :param categories: [Only for Categorical Attributes] If the attribute is categorical, this will contain the
        attribute's categorical values and the labels for each value. It is required only if the categorical flag
        is set to true. To modify the category values, use :code:`arthur_model.get(name=attribute_name).set([{'value': value_1}, ..., {'value': value_n}])`.
        To mofidy the category labels, use :func:`arthurai.core.models.ArthurModel.set_attribute_labels()`.
    :param gt_class_link: Optional link for a predicted attribute to its corresponding value
        in a ground truth class attribute
    :param implicit: is the attribute implicitly created by the API
    """

    name: str
    value_type: ValueType
    stage: Stage
    id: Optional[str] = None
    label: Optional[str] = None
    position: Optional[int] = None
    categorical: Optional[bool] = False
    min_range: Optional[Union[int, float]] = None
    max_range: Optional[Union[int, float]] = None
    monitor_for_bias: bool = False
    categories: Optional[List[AttributeCategory]] = None
    bins: Optional[List[AttributeBin]] = None
    is_unique: bool = False
    is_positive_predicted_attribute: bool = False
    attribute_link: Optional[str] = None
    gt_class_link: Optional[str] = None
    token_attribute_link: Optional[str] = None
    implicit: bool = False

    def set(self, **kwargs):
        """Set one or many of the available properties of the ArthurAttribute class"""

        # do some basic validation on values to be set
        is_unique = kwargs.get("is_unique", self.categorical)
        categorical = kwargs.get("categorical", self.categorical)

        categories = [AttributeCategory(value=c) for c in kwargs.get("categories")] if "categories" in kwargs.keys() \
            else self.categories

        max_range = kwargs.get('max_range', self.max_range)
        min_range = kwargs.get('min_range', self.min_range)

        if categorical and not is_unique and categories is None:
            raise MissingParameterError("categories is required for non-unique categorical attributes")
        elif not categorical:
            if (min_range and max_range is None) or (min_range is None and max_range):
                raise MissingParameterError("Min and max range must both be set to either numerical values or none")
            elif min_range and max_range and min_range > max_range:
                raise UserValueError(f"Min range must be set to a value less then the max range, received the"
                                f" following (min, max) values: ({min_range}, {max_range})")
            elif categories:
                raise UserValueError("Categories are set for this attribute, they must be set to "
                                "None when categorical is False")

        # Check to make sure that the attributes which the user wants to set are valid
        for attribute_name, attribute_value in kwargs.items():
            if not ArthurAttribute.__annotations__.get(attribute_name):
                raise UserValueError(f"Attribute: '{attribute_name}' can not be set on an ArthurAttribute object")
            self.__setattr__(attribute_name, attribute_value)

            # format categories and bins appropriately
            if attribute_name == "categories":
                self.categories = categories
            if attribute_name == "bins":
                self.bins = [AttributeBin(kwargs.get("bins")[i], kwargs.get("bins")[i + 1])
                             for i in range(len(kwargs.get("bins")) - 1)] if "bins" in kwargs.keys() else self.bins

        return self

    def short_name(self):
        basename = f"{self.stage}[{self.position}]:{self.name}"
        label_suffix = f" ({self.label})" if self.label is not None else ""
        return basename + label_suffix

    def __str__(self):
        name = self.short_name()
        if self.categorical:
            name += f"\n\tCategorical: ["
            for cat in self.categories[:MAX_CATEGORIES_TO_SHOW]:
                name += f"{cat}, "
            name = name[:-2]
            if len(self.categories) > MAX_CATEGORIES_TO_SHOW:
                name += f"...and {len(self.categories) - MAX_CATEGORIES_TO_SHOW} more"
            name += "]"

        else:
            name += f"\n\tRange: [{self.min_range}, {self.max_range}]"

        if self.attribute_link:
            name += f"\n\tLink: {self.attribute_link}"

        if self.gt_class_link:
            name += f"\n\tLink: {self.gt_class_link}"
        return name
