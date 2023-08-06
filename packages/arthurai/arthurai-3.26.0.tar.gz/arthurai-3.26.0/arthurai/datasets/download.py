# download.py
import boto3
from botocore import UNSIGNED, exceptions
from botocore.client import Config
from enum import Enum
import os.path
from os import path
import logging
from pathlib import Path
from typing import Dict, List
import zipfile
import pandas as pd
import yaml

from arthurai.common.exceptions import ArthurDownloadError

logger = logging.getLogger(__name__)

s3_bucket_name = "s3-bucket-arthur-public"
default_download_directory = Path("arthur-downloads/")


class ArthurDatasetSource(Enum):
    """
    Class to enumerate the sources of data that can be used for an ArthurExampleDownloader
    """
    S3 = "S3"


class ArthurExampleDownloader:
    """
    Class for downloading data for an Arthur Example
    """

    def __init__(self, example_name: str, target_base_dir: Path, source=ArthurDatasetSource.S3):
        self.example_name = example_name
        self.source = source
        if not os.path.isdir(target_base_dir):
            os.mkdir(target_base_dir)
        if not os.path.isdir(target_base_dir / example_name):
            os.mkdir(target_base_dir / example_name)
        self.target_path = target_base_dir / example_name

        # scan each sub-folder within sandbox/example_name/ :
        # metadata/, data/, predictions/, and models/
        if self.source == ArthurDatasetSource.S3:
            self.metadata_base_path = Path(f"sandbox/{self.example_name}/metadata/")
            self.dataset_base_path = Path(f"sandbox/{self.example_name}/data/")
            self.pred_base_path = Path(f"sandbox/{self.example_name}/predictions/")
            self.model_base_path = Path(f"sandbox/{self.example_name}/models/")

            metadata_files = get_file_keys_in_s3_folder(self.metadata_base_path)
            if len(metadata_files) == 1:
                self.metadata_file = metadata_files[0]
            else:
                raise ArthurDownloadError("Currently can only support downloading 1 metadata file from S3 (not 0 or >=2)")

            dataset_files = get_file_keys_in_s3_folder(self.dataset_base_path)
            if len(dataset_files) == 1:
                self.dataset_file = dataset_files[0]
            else:
                raise ArthurDownloadError("Currently can only support downloading 1 dataset file from S3 (not 0 or >=2)")

            pred_files = get_file_keys_in_s3_folder(self.pred_base_path)
            if len(pred_files) == 1:
                self.pred_file = pred_files[0]
            else:
                raise ArthurDownloadError("Currently can only support downloading 1 predictions file from S3 (not 0 or >=2)")

            model_files = get_file_keys_in_s3_folder(self.model_base_path)
            if len(model_files) == 0:
                self.model_file = None
            elif len(model_files) == 1:
                self.model_file = model_files[0]
            else:
                raise ArthurDownloadError("Currently can only support downloading <=1 model file from S3 (not >=2)")
        else:
            raise ValueError(f"Currently not able to support downloading from {source}")

    def download_metadata(self) -> Dict:
        """Gets metadata for an ArthurExample

        :return: metadata dictionary with parameters relating to file locations & ArthurModel model & attribute info
        """
        if self.source == ArthurDatasetSource.S3:
            try:
                s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
                s3_filepath = self.metadata_base_path / self.metadata_file
                response = s3_client.get_object(Bucket=s3_bucket_name, Key=str(s3_filepath))
                metadata = yaml.safe_load(response["Body"])
                return metadata
            except exceptions.ClientError:
                raise ArthurDownloadError(f"Could not get {self.example_name} metadata from S3. Check if a) you have "
                                          f"spelled the name correctly or b) {self.example_name} is in fact an example "
                                          f"with data in the Arthur public S3 bucket in the sandbox folder.")
        else:
            raise ValueError(f"Currently not able to support downloading from {self.source}")

    def download_dataset(self) -> Path:
        """Gets an example dataset for an ArthurExample

        :return: Path to the downloaded dataset
        """

        if not path.exists(self.target_path / self.dataset_file):
            download_from_s3(self.dataset_base_path / self.dataset_file, self.target_path / self.dataset_file)
        return self.target_path / self.dataset_file

    def download_pretrained_model(self) -> Path:
        """Gets a pretrained model for an ArthurExample

        :return: Path to the downloaded model
        """
        if self.model_file is not None:
            if not path.exists(self.target_path / self.model_file):
                download_from_s3(self.model_base_path / self.model_file, self.target_path / self.model_file)
            return self.target_path / self.model_file
        raise ValueError("There is no model to be downloaded for this example")

    def download_pretrained_model_predictions(self) -> Path:
        """Gets pretrained model predictions for an ArthurExample

        :return: Path to the downloaded predictions
        """
        if not path.exists(self.target_path / self.pred_file):
            download_from_s3(self.pred_base_path / self.pred_file, self.target_path / self.pred_file)
        return self.target_path / self.pred_file


def download_from_s3(s3_file_address: Path, local_file_destination: Path) -> None:
    """Downloads a file from S3 to be saved locally (and unzips if it is a zipped file)

    :param s3_file_address: Path, the full location filepath for the file in the Arthur public S3 bucket
    :param local_file_destination: Path, the directory to save the file to locally
    :return: None
    """
    s3_client = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
    try:
        local_file_destination_string = str(local_file_destination)
        s3_client.Object(str(s3_bucket_name), str(s3_file_address)).download_file(local_file_destination_string)
        if "zip" in local_file_destination_string:
            with zipfile.ZipFile(local_file_destination, 'r') as zip_ref:
                zip_ref.extractall()
    except exceptions.ClientError:
        raise ArthurDownloadError(f"Could not download {s3_file_address} from S3. Check if a) you have spelled the "
                                  f"filename correctly or b) {s3_file_address} is actually hosted on the Arthur public "
                                  f"S3 bucket in the sandbox folder.")


def get_file_keys_in_s3_folder(filepath: Path) -> List[str]:
    """
    Lists the files in the S3 directory

    :param filepath: Path, the path of the S3 directory to read files from
    """
    s3_client = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
    bucket = s3_client.Bucket(s3_bucket_name)
    return [o.key.split('/')[-1] for o in bucket.objects.filter(Prefix=str(filepath)) if o.key[-1] != "/"]


def load_downloaded_file(filepath: Path) -> pd.DataFrame:
    """Returns a file located at `filepath` to the user

    :param filepath: Path, the local path to load the file from
    """
    filepath_string = str(filepath)
    if "csv" in filepath_string:
        return pd.read_csv(filepath_string)
    elif "parquet" in filepath_string:
        return pd.read_parquet(filepath_string)
    else:
        raise TypeError(f"Currently not able to support returning the filetype in {filepath_string}")

