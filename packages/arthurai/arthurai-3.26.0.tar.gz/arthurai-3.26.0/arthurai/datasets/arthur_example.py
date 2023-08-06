# arthur_example.py
from dataclasses import dataclass
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from typing import List, Union, Optional, Tuple
from arthurai.core.base import ArthurBaseJsonDataclass
from arthurai.core.models import ArthurModel
from arthurai.common.constants import Stage
from arthurai.common.exceptions import ArthurDownloadError
from arthurai.datasets.download import ArthurExampleDownloader, default_download_directory, load_downloaded_file


@dataclass
class ArthurExampleSchema(ArthurBaseJsonDataclass):
	"""
	Class for the schema of all the data used in an Arthur Example
	"""

	arthur_model: ArthurModel
	default_data_split_test_size: Optional[float] = 0.3
	default_random_state: int = 278487


class ArthurExample:
	"""
	Class for a user to interface with example data for model analysis and using Arthur
	"""

	def __init__(self, name: str, download_destination_folder: Optional[Path] = None):
		"""
		Constructs an ArthurExample

		:param name: str, the name of the example
		:param download_destination_folder: Path, the destination to save files to. Defaults to current directory if
			none is specified.
		"""
		if download_destination_folder is None:
			download_destination_folder = Path.cwd() / default_download_directory
		try:
			downloader = ArthurExampleDownloader(name, download_destination_folder)
		except ArthurDownloadError:
			raise ValueError(f"Cannot download data: {name} is not the name of a valid ArthurExample.") from None

		self.example_schema = ArthurExampleSchema.from_dict(downloader.download_metadata())
		self.dataset = load_downloaded_file(downloader.download_dataset())
		self.predictions = load_downloaded_file(downloader.download_pretrained_model_predictions())

	def get_dataset(self, split: bool = False, test_split_size: Optional[float] = None) \
		-> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
		"""
		Returns a dataframe of the model's inputs, predictions, ground truth labels, and non input data

		:param split: bool, whether to return the data split into train/test.
		:param test_split_size: the percentage of data to be split into the test set if splitting the data. If None,
			uses the default test split defined in the example schema.
		:return: dataframe of inputs, predictions, ground truth labels, and non input data
		"""
		if split:
			train_inputs, test_inputs = self.get_inputs(split=True, test_split_size=test_split_size)
			train_pred, test_pred = self.get_predictions(split=True, test_split_size=test_split_size)
			train_gt, test_gt = self.get_ground_truth_data(split=True, test_split_size=test_split_size)
			train_dataset = pd.concat([train_inputs, train_pred, train_gt], axis=1)
			test_dataset = pd.concat([test_inputs, test_pred, test_gt], axis=1)
			if len(self.non_input_attribute_names) > 0:
				train_non_input, test_non_input = self.get_non_input_data(split=True, test_split_size=test_split_size)
				train_dataset = pd.concat([train_dataset, train_non_input], axis=1)
				test_dataset = pd.concat([test_dataset, test_non_input], axis=1)
			return train_dataset, test_dataset
		else:
			dataset = pd.concat([self.get_inputs(), self.get_predictions(), self.get_ground_truth_data()], axis=1)
			if len(self.non_input_attribute_names) > 0:
				dataset = pd.concat([dataset, self.get_non_input_data()], axis=1)
			return dataset

	def get_inputs(self, split: bool = False, test_split_size: Optional[float] = None, random_state: Optional[int] = None) \
		-> Union[pd.DataFrame, pd.Series, Tuple[pd.DataFrame, pd.DataFrame], Tuple[pd.Series, pd.Series]]:
		"""
		Returns the model's input attribute feature values from self.dataset

		:param split: bool, whether to return the data split by reference/inference (AKA train/test),
			or whether to return a single dataframe
		:param test_split_size: the percentage of data to be split into the test set if splitting the data
		:param random_state: int, random state for optional split
		:return: dataframe of model input features
		"""
		X = self.dataset[self.input_attribute_names]
		if split:
			if test_split_size is None: test_split_size = self.example_schema.default_data_split_test_size
			if random_state is None: random_state = self.example_schema.default_random_state
			return train_test_split(X, test_size=test_split_size, random_state=random_state)
		return X

	def get_ground_truth_data(self, split: bool = False, test_split_size: Optional[float] = None, random_state: Optional[int] = None) \
		-> Union[pd.DataFrame, pd.Series, Tuple[pd.DataFrame, pd.DataFrame], Tuple[pd.Series, pd.Series]]:
		"""
		Returns the model's ground truth labels from self.dataset

		:param split: bool, whether to return the data split by reference/inference (AKA train/test),
			or whether to return a single dataframe
		:param test_split_size: the percentage of data to be split into the test set if splitting the data
		:param random_state: int, random state for optional split
		:return: dataframe of model ground truth values
		"""
		y = self.dataset[self.gt_attribute_names]
		if split:
			if test_split_size is None: test_split_size = self.example_schema.default_data_split_test_size
			if random_state is None: random_state = self.example_schema.default_random_state
			return train_test_split(y, test_size=test_split_size, random_state=random_state)
		return y

	def get_predictions(self, split: bool = False, test_split_size: Optional[float] = None, random_state: Optional[int] = None) \
		-> Union[pd.DataFrame, pd.Series, Tuple[pd.DataFrame, pd.DataFrame], Tuple[pd.Series, pd.Series]]:
		"""
		Returns the model's predicted values from self.predictions

		:param split: bool, whether to return the data split by reference/inference (AKA train/test),
			or whether to return a single dataframe
		:param test_split_size: the percentage of data to be split into the test set if splitting the data
		:param random_state: int, random state for optional split
		:return: dataframe of model prediction data
		"""
		y_pred = self.predictions[self.pred_attribute_names]
		if split:
			if test_split_size is None: test_split_size = self.example_schema.default_data_split_test_size
			if random_state is None: random_state = self.example_schema.default_random_state
			return train_test_split(y_pred, test_size=test_split_size, random_state=random_state)
		return y_pred

	def get_non_input_data(self, split: bool = False, test_split_size: Optional[float] = None, random_state: Optional[int] = None) \
		-> Union[pd.DataFrame, pd.Series, Tuple[pd.DataFrame, pd.DataFrame], Tuple[pd.Series, pd.Series]]:
		"""
		Returns the model's non input attributes from self.dataset

		:param split: bool, whether to return the data split by reference/inference (AKA train/test),
			or whether to return a single dataframe
		:param test_split_size: the percentage of data to be split into the test set if splitting the data
		:param random_state: int, random state for optional split
		:return: dataframe of model non-input attribute data
		"""
		if len(self.non_input_attribute_names) > 0:
			non_input_data = self.dataset[self.non_input_attribute_names]
			if split:
				if test_split_size is None: test_split_size = self.example_schema.default_data_split_test_size
				if random_state is None: random_state = self.example_schema.default_random_state
				return train_test_split(non_input_data, test_size=test_split_size, random_state=random_state)
			return non_input_data
		raise ValueError("This example has no non_input attributes.")

	@property
	def input_attribute_names(self) -> List[str]:
		"""
		The list of feature names which make up the model's input attributes

		:return: list of input attribute names
		"""
		return [attr.name for attr in self.example_schema.arthur_model.get_attributes(stage=Stage.ModelPipelineInput)]

	@property
	def gt_attribute_names(self) -> List[str]:
		"""
		The list of attribute names which make up the model's ground truth attributes
		Either GroundTruth or GroundTruthClass

		:return: list of ground truth attribute names
		"""
		gt_attrs = [attr.name for attr in self.example_schema.arthur_model.get_attributes(stage=Stage.GroundTruth)]
		if len(gt_attrs) > 0: return gt_attrs
		return [attr.name for attr in self.example_schema.arthur_model.get_attributes(stage=Stage.GroundTruthClass)]

	@property
	def pred_attribute_names(self) -> List[str]:
		"""
		The list of feature names which make up the model's predicted attributes

		:return: list of predicted attribute names
		"""
		return [attr.name for attr in self.example_schema.arthur_model.get_attributes(stage=Stage.PredictedValue)]

	@property
	def non_input_attribute_names(self) -> List[str]:
		"""
		The list of feature names which make up the model's non-input attributes

		:return: list of non-input attribute names
		"""
		return [attr.name for attr in self.example_schema.arthur_model.get_attributes(stage=Stage.NonInputData)]
