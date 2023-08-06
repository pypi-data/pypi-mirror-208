from google.cloud import bigquery, storage
from google.oauth2 import service_account
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit
from pathlib import Path
from scipy.special import softmax
from shutil import make_archive, unpack_archive
from simpletransformers.classification import (
    ClassificationModel,
    ClassificationArgs,
    MultiLabelClassificationModel,
    MultiLabelClassificationArgs
)
from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from typing import List, Optional
import glob
import joblib
import json
import numpy as np
import os
import pandas as pd
import shutil
import copy

os.environ["TOKENIZERS_PARALLELISM"] = "false"
import logging

logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)


def f1_multiclass(labels, preds):
    """
    Computes the F1 score of a multi-class classification problem.
    Args:
        labels (np.ndarray): ground-truth labels, shape (n_samples, n_classes).
        preds (np.ndarray): predicted labels, shape (n_samples, n_classes).
    Returns:
        float: the F1 score.
    """
    return (
        f1_score(labels, preds, average="macro")
        if len(np.unique(labels)) > 2
        else f1_score(labels, preds, average="binary")
    )

def precision_multiclass(labels, preds):
    """
    Computes the precision score of a multi-class classification problem.
    Args:
        labels (np.ndarray): ground-truth labels, shape (n_samples, n_classes).
        preds (np.ndarray): predicted labels, shape (n_samples, n_classes).
    Returns:
        float: the precision score.
    """
    return (
        precision_score(labels, preds, average="macro")
        if len(np.unique(labels)) > 2
        else precision_score(labels, preds, average="binary")
    )


def recall_multiclass(labels, preds):
    """
    Computes the recall score of a multi-class classification problem.
    Args:
        labels (np.ndarray): ground-truth labels, shape (n_samples, n_classes).
        preds (np.ndarray): predicted labels, shape (n_samples, n_classes).
    Returns:
        float: the recall score.
    """
    return (
        recall_score(labels, preds, average="macro")
        if len(np.unique(labels)) > 2
        else recall_score(labels, preds, average="binary")
    )

def precision_multilabel(labels, preds, threshold=0.5, average="macro"):
    """
    Computes the precision score of a multi-label classification problem.
    Args:
        labels (np.ndarray): ground-truth labels, shape (n_samples, n_classes).
        preds (np.ndarray): predicted labels, shape (n_samples, n_classes).
        threshold (float): probability threshold to consider a label as positive.
        average (str): averaging strategy to use, either "macro" or "micro".
    Returns:
        float: the precision score.
    """
    preds = (preds > threshold).astype(np.int32)
    return precision_score(labels, preds, average=average)

def recall_multilabel(labels, preds, threshold=0.5, average="macro"):
    """
    Computes the recall score of a multi-label classification problem.
    Args:
        labels (np.ndarray): ground-truth labels, shape (n_samples, n_classes).
        preds (np.ndarray): predicted labels, shape (n_samples, n_classes).
        threshold (float): probability threshold to consider a label as positive.
        average (str): averaging strategy to use, either "macro" or "micro".
    Returns:
        float: the recall score.
    """
    preds = (preds > threshold).astype(np.int32)
    return recall_score(labels, preds, average=average)

def accuracy_multilabel(labels, preds, threshold=0.5):
    """
    Computes the accuracy score of a multi-label classification problem.
    Args:
        labels (np.ndarray): ground-truth labels, shape (n_samples, n_classes).
        preds (np.ndarray): predicted labels, shape (n_samples, n_classes).
        threshold (float): probability threshold to consider a label as positive.
    Returns:
        float: the accuracy score.
    """
    preds = (preds > threshold).astype(np.int32)
    return accuracy_score(labels, preds)


def f1_multilabel(labels, preds, threshold=0.5, average="macro"):
    """
    Computes the F1 score of a multi-label classification problem.
    Args:
        labels (np.ndarray): ground-truth labels, shape (n_samples, n_classes).
        preds (np.ndarray): predicted labels, shape (n_samples, n_classes).
        threshold (float): probability threshold to consider a label as positive.
        average (str): averaging strategy to use, either "macro" or "micro".
    Returns:
        float: the F1 score.
    """
    preds = (preds > threshold).astype(np.int32)
    return f1_score(labels, preds, average=average)



def create_model_card(
    model_card_path="model_card.md",
    model_title="Model Title",
    model_summary="",
    team="",
    contact_persons="",
    project_name="",
    project_sheet_url="",
    model_date="",
    model_version="",
    model_type="",
    model_target_values="",
    useful_links="",
    primary_intended_uses="",
    primary_intended_users="",
    known_biases="",
    caveats_recommendations="",
    minimal_starter_code="",
    used_metrics="",
    train_data_path="",
    simulation_data_path="",
    features="",
    data_modifications="",
    train_data_summary="",
    sim_data_summary="",
    does_the_model_use_any_sensitive_data="",
    risk_mitigation_strategies="",
    model_usage_risks="",
    possible_fraught_use_cases="",
):
    """Create and save a markdown model card.

    Parameters
    ----------
    model_card_path : str, optional
        Path to save the model card, by default "model_card.md"
    model_title : str, optional
        title of the model card, by default "Model Title"
    model_summary : str, optional
        Model summary, by default ""
    team : str, optional
        Team name, by default ""
    contact_persons : str, optional
        Contact persons, by default ""
    project_name : str, optional
        Project name, by default ""
    project_sheet_url : str, optional
        Project sheet url, by default ""
    model_date : str, optional
        Model date, by default ""
    model_version : str, optional
        Model version, by default ""
    model_type : str, optional
        Type of the model. Pytorch, Tensorflow, onnx etc., by default ""
    model_target_values : str, optional
        Predicted class names of the model, by default ""
    useful_links : str, optional
        Useful links, by default ""
    primary_intended_uses : str, optional
        The main purposes for the model, by default ""
    primary_intended_users : str, optional
        The main stakehodlers that will use the model, by default ""
    known_biases : str, optional
        Any known biases, by default ""
    caveats_recommendations : str, optional
        Any information to know while using the model, by default ""
    minimal_starter_code : str, optional
        Minimal starter code, by default ""
    used_metrics : str, optional
        Used metrics while training and evaluating the code, by default ""
    train_data_path : str, optional
        Path to the train data, by default ""
    simulation_data_path : str, optional
        Path to the simulation data, by default ""
    features : str, optional
        Input features, by default ""
    data_modifications : str, optional
        Any modifications done on the training data, by default ""
    train_data_summary : str, optional
        Any information about the training data, by default ""
    sim_data_summary : str, optional
        Any information about the simulation data, by default ""
    does_the_model_use_any_sensitive_data : str, optional
        Does the model use any sensitive data, by default ""
    risk_mitigation_strategies : str, optional
        Risk mitigation strategies to cover up possible problems, by default ""
    model_usage_risks : str, optional
        Any risks while using the model, by default ""
    possible_fraught_use_cases : str, optional
        Any possible fraught use cases, by default ""
    """

    model_card = f"""
# {model_title}

## Model Details

| Attribute            | Value                                 |
|---------------------:|:--------------------------------------|
|  Team                | {team } |
|  Contact Persons     | {contact_persons } |
|  Project Title       | {project_name } |
|  Project Sheet Link  | {project_sheet_url } |
|  Model Date          | {model_date } |
|  Model Version       | {model_version } |
|  Model Type          | {model_type } |
|  Useful Links        | {useful_links } |

{model_summary}

## Intended Use
*Use cases that were envisioned during development.*

- **Primary intended uses: {primary_intended_uses} ** 
- **Primary intended users: {primary_intended_users} **

## Known Biases, Caveats and Recommendations
*Things to be aware of while using the model. Recommendations to the users.*

### Known Biases

{known_biases}

### Caveats and Recommendations

{caveats_recommendations}

## Minimal Starter Code

```
{minimal_starter_code}
```

## Metrics
*Performance metrics and decision thresholds used during the training and evaluation. Evaluation results can be shared here, or a reference to the project simulation sheet can be given.*

{used_metrics}

## Data Details
*Detailed information about the data.*

| | |
|----------------------:|-----|
|Train Data Path        |  {train_data_path}   |
|Simulation Data path   |  {simulation_data_path}  |


### Targets & Features & Data Modifications
*Explanation of the targets, used features and information about data modifications, if any.*

- **Targets:** {model_target_values}
- **Features:** {features}
- **Data Modifications:** {data_modifications}


### Train Data Information
*Additional information about the train data, if any.*

{train_data_summary}


### Simulation Data Information
*Additional information about the simulation data, if any.*

{sim_data_summary}


## Ethical Considerations
*Ethical considerations that went into model development.*

- **Does the model use any sensitive data?** {does_the_model_use_any_sensitive_data}
- **What risk mitigation strategies were used during model development?** {risk_mitigation_strategies}
- **What risks may be present in model usage?** {model_usage_risks}
- **Are there any known model use cases that are especially fraught?** {possible_fraught_use_cases}

"""

    with open(model_card_path, "w") as f:
        f.write(model_card)

    print(f"--- Model card is saved to {model_card_path} ---")


def display_markdown(markdown_path: str):
    """Render and display a markdown file given the markdown path.

    Parameters
    ----------
    markdown_path : str
        Path to the markdown file.
    """
    from IPython.display import display, Markdown

    with open(markdown_path, "r") as f:
        md = f.read()
        
    display(Markdown(md))


class TextClassifier:
    def __init__(
        self,
        do_train: bool,
        model_dir: str,
        classification_type: Optional[str] = "single",
        model_type: Optional[str] = "roberta",
        model_version: Optional[str] = "ty_roberta",
        gpus_to_use: Optional[List[str]] = [],
        exp_args: Optional[dict] = {},
        do_lowercase: Optional[bool] = True,
        data_lang: Optional[str] = "tr",
        save_onnx_model: Optional[bool] = True,
        random_state: Optional[int] = 2022,
        train_only_final_layer: Optional[bool] = False,
        freeze_layers_dict: Optional[List] = None,
        gcloud_project_id: Optional[str] = None,
        gcloud_bucket_name: Optional[str] = None,
        gcloud_blob_name: Optional[str] = None,
        gcloud_credentials_path: Optional[str] = None,
        nlp_project_id: Optional[str] = None,
        nlp_bucket_name: Optional[str] = None,
        nlp_blob_name: Optional[str] = None,
        nlp_credentials_path: Optional[str] = None,
    ) -> None:

        """General text classification pipeline.
        Train and Evaluation data needs to be in a Pandas Dataframe containing at least two columns, a 'text' and a 'labels' column.
        The `labels` column must be string and seperated by comma values, if multilabel classification will be conducted.


        Parameters
        ----------
        do_train : bool
            Whether to train a model or take inference.

        model_dir : str
            Server model directory to be used during training or inference.

        classification_type : str, optional
            Type of classification task. Only 'single' or 'multi' is allowed.

        model_type : str, optional
            Model type to be used by Simple Transformers
            Please consider using 'bert' or 'roberta' for Turkish data and 'distilbert' for multilingual data.

        model_version : str, optional
            Model version to be used by Simple Transformers.
            Please consider using 'dbmdz/bert-base-turkish-cased', 'ty_bert', 'ty_roberta' for Turkish data
            and 'sentence-transformers/distiluse-base-multilingual-cased-v2' for multilingual data.

        gpus_to_use : list of str, optional
            Available GPU list for training & inference.

        exp_args: dict, optional
            Simple Transformers model arguments which can be used during training.

        do_lowercase: bool, optional
            Whether to convert text to lowercase or not.
        
        data_lang: str, optional
            Language of the data to be trained on.

        save_onnx_model : bool, optional
            Whether to upload only the ONNX model to GCS or not.

        random_state : int, optional
            Random seed for reproducibility

        train_only_last_layer: bool, optional
            Whether to train / finetune only the final layer (classification head) or full training (full training may result with overfitting, training only the last layer is recommended).

        freeze_layers_dict: list, optional
            Model layer config list to be freezed (not trained). Required when train_only_last_layer == True.

        gcloud_project_id : str, optional
            Name of the Google Cloud project.

        gcloud_bucket_name : str, optional
            Name of the GCS bucket.

        gcloud_blob_name : str, optional
            Path to GCS bucket for model saving.

        gcloud_credentials_path : str, optional
            Name of the Google Cloud credentials for the project. must be given if model_version is 'ty_bert' or 'ty_roberta'.

        nlp_project_id : str, optional
            Name of the Google Cloud project for NLP project. must be given if model_version is 'ty_bert' or 'ty_roberta'.

        nlp_bucket_name : str, optional
            Name of the Google Cloud bucket name for NLP project. must be given if model_version is 'ty_bert' or 'ty_roberta'.

        nlp_blob_name : str, optional
            Name of the Google Cloud blob name for NLP project. must be given if model_version is 'ty_bert' or 'ty_roberta'.

        nlp_credentials_path : str, optional
            Name of the Google Cloud credentials for NLP project. must be given if model_version is 'ty_bert' or 'ty_roberta'.


        Returns
        -------
        None

        """
        
        # session is starting...
        self.print_log_messages(0)

        self.gpus_to_use = gpus_to_use
        self.do_train = do_train
        self.model_dir = model_dir
        self.do_lowercase = do_lowercase
        self.train_only_final_layer = train_only_final_layer
        self.freeze_layers_dict = freeze_layers_dict
        self.data_lang = data_lang

        if self.train_only_final_layer:
            assert (
                self.freeze_layers_dict is not None
            ), "Please provide freeze_layers_dict to train only the final layer for the current model. You can use https://simpletransformers.ai/docs/tips-and-tricks/#custom-parameter-groups for customization."

        # setup GPUs if available
        if len(self.gpus_to_use):
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(self.gpus_to_use)

        # GCS params
        self.gcloud_project_id = gcloud_project_id
        self.gcloud_bucket_name = gcloud_bucket_name
        self.gcloud_blob_name = gcloud_blob_name
        self.gcloud_project_id = gcloud_project_id
        self.gcloud_credentials_path = gcloud_credentials_path

        if self.gcloud_project_id is not None:
            # setup credentials for big query & GCS
            assert os.path.exists(
                self.gcloud_credentials_path
            ), self.print_error_messages(0)

            # make GCS connection
            with open(self.gcloud_credentials_path) as json_file:
                connection_info_gcs = json.load(json_file)

            credentials = service_account.Credentials.from_service_account_info(
                connection_info_gcs
            )
            self.bigq_client = bigquery.Client(
                credentials=credentials, project=self.gcloud_project_id
            )

            self.storage_client = storage.Client(
                credentials=credentials, project=self.gcloud_project_id
            )

            # setup credentials
            self.print_log_messages(1)

        if self.do_train:
            # create model arguments
            assert classification_type in [
                "single",
                "multi",
            ], self.print_error_messages(1)
            self.classification_type = classification_type
            self.random_state = random_state
            
            if self.classification_type == "single":
                self.classification_model_obj = ClassificationModel
                self.classification_args_obj = ClassificationArgs

            elif self.classification_type == "multi":
                self.classification_model_obj = MultiLabelClassificationModel
                self.classification_args_obj = MultiLabelClassificationArgs

            self.model_args = {
                "do_lower_case": self.do_lowercase if self.data_lang != "tr" else False,
                "use_early_stopping": True,
                "early_stopping_consider_epochs": False,
                "early_stopping_delta": 0.001,
                "early_stopping_metric": "eval_loss",
                "early_stopping_metric_minimize": True,
                "early_stopping_patience": 5,
                "eval_batch_size": 16,
                "train_batch_size": 16,
                "n_gpu": len(self.gpus_to_use),
                "evaluate_during_training": True,
                "evaluate_during_training_silent": False,
                "fp16": True,
                "num_train_epochs": 3,
                "reprocess_input_data": True,
                "output_dir": os.path.join(self.model_dir, "outputs/"),
                "best_model_dir": os.path.join(self.model_dir, "best_model/"),
                "cache_dir": os.path.join(self.model_dir, "cache_dir/"),
                "overwrite_output_dir": True,
                "use_multiprocessing": False,
                "use_multiprocessing_for_evaluation": False,
                "manual_seed": self.random_state,
                "save_model_every_epoch": False,
                "save_eval_checkpoints": False,
                "save_steps": -1,
                "save_best_model": True
            }

            self.model_args = {**self.model_args, **exp_args}
            self.model_type = model_type
            self.model_version = model_version
            self.save_onnx_model = save_onnx_model
            self.split_size = 0.2

            # create BigQ directories
            if self.model_version in ["ty_bert", "ty_roberta"]:
                assert nlp_credentials_path is not None, self.print_error_messages(2)
                assert os.path.exists(nlp_credentials_path), self.print_error_messages(
                    3
                )
                assert nlp_project_id is not None, self.print_error_messages(14)
                assert nlp_bucket_name is not None, self.print_error_messages(15)
                assert nlp_blob_name is not None, self.print_error_messages(16)

                # setup credentials for internal ty-bert model
                with open(nlp_credentials_path) as json_file:
                    connection_info_nlp = json.load(json_file)

                credentials = service_account.Credentials.from_service_account_info(
                    connection_info_nlp
                )
                storage_client = storage.Client(
                    credentials=credentials, project=nlp_project_id
                )

                self.model_version_raw = self.model_version

                # download the ty-bert model
                self.model_version = os.path.join(self.model_dir, self.model_version_raw)

                self.download_from_gcs(
                    storage_client,
                    os.path.join(self.model_dir, self.model_version_raw, "best_model.tar.gz"),
                    nlp_bucket_name,
                    nlp_blob_name,
                )

                unpack_archive(
                    os.path.join(self.model_dir, self.model_version_raw, "best_model.tar.gz"),
                    extract_dir=self.model_version,
                    format="gztar",
                )

            # arrange directory parameters
            self.model_dir_splitted = os.path.split(self.model_dir)

            self.label_encoder_dir = os.path.join(
                self.model_dir_splitted[0],
                self.model_dir_splitted[-1],
                "best_model",
                "label_encoder.joblib",
            )

            self.model_metadata_dir = os.path.join(
                self.model_dir_splitted[0],
                self.model_dir_splitted[-1],
                "best_model",
                "model_metadata.joblib",
            )

            if gcloud_blob_name is not None:
                self.model_bigq_dir = os.path.join(
                    gcloud_blob_name,
                    "best_model.tar.gz",
                )

            if save_onnx_model:
                self.onnx_model_dir = os.path.join(
                    self.model_dir_splitted[0],
                    self.model_dir_splitted[-1],
                    "onnx_model",
                )

                self.label_encoder_onnx_dir = os.path.join(
                    self.model_dir_splitted[0],
                    self.model_dir_splitted[-1],
                    "onnx_model",
                    "label_encoder.joblib",
                )

                self.model_metadata_onnx_dir = os.path.join(
                    self.model_dir_splitted[0],
                    self.model_dir_splitted[-1],
                    "onnx_model",
                    "model_metadata.joblib",
                )

                if gcloud_blob_name is not None:
                    self.onnx_model_bigq_dir = os.path.join(
                        gcloud_blob_name, "onnx_model.tar.gz"
                    )

            self.print_log_messages(2)

        else:
            if gcloud_bucket_name is not None:
                # download model from GCS
                self.download_from_gcs(
                    self.storage_client,
                    os.path.join(
                        self.model_dir, os.path.split(self.gcloud_blob_name)[-1]
                    ),
                    self.gcloud_bucket_name,
                    self.gcloud_blob_name,
                )

            extract_path = (
                os.path.join(self.model_dir, os.path.split(self.gcloud_blob_name)[-1])
                if self.gcloud_blob_name is not None
                else self.model_dir
            )

            # extract model files
            if not os.path.isdir(extract_path):
                unpack_archive(extract_path, extract_dir=self.model_dir, format="gztar")

            # read model files
            self.model_metadata = joblib.load(
                os.path.join(self.model_dir, "model_metadata.joblib")
            )

            self.label_encoder = joblib.load(
                os.path.join(self.model_dir, "label_encoder.joblib")
            )

            self.classification_type = self.model_metadata["task_type"]

            if self.classification_type == "single":
                self.model = ClassificationModel(
                    self.model_metadata["model_type"],
                    self.model_dir,
                    use_cuda=True if len(self.gpus_to_use) else False,
                )
            else:
                self.model = MultiLabelClassificationModel(
                    self.model_metadata["model_type"],
                    self.model_dir,
                    use_cuda=True if len(self.gpus_to_use) else False,
                )

            self.print_log_messages(10)

    @staticmethod
    def upload_to_gcs(
        storage_client, local_path: str, dest_bucket_name: str, dest_blob_name: str
    ):
        """Helper for uploading files to GCS.

        Parameters
        ----------
        storage_client : storage.Client
            GCS client object

        local_path : str
            Path for files in the server

        dest_bucket_name : str
            GCS bucket name

        dest_blob_name : str
            GCS file path


        Returns
        -------
        None

        """
        bucket = storage_client.get_bucket(dest_bucket_name)
        if os.path.isfile(local_path):
            blob = bucket.blob(dest_blob_name)
            blob.upload_from_filename(local_path)
        else:
            rel_paths = [p for p in glob.glob(local_path + "/**", recursive=True)]
            for local_file in rel_paths:
                remote_path = os.path.join(
                    dest_blob_name, local_file.replace(local_path + "/", "")
                )
                if os.path.isfile(local_file):
                    blob = bucket.blob(remote_path)
                    blob.upload_from_filename(local_file)

    @staticmethod
    def download_from_gcs(
        storage_client, dest_path: str, bucket_name: str, blob_name: str, overwrite=True
    ):
        """Helper for downloading files from GCS.

        Parameters
        ----------
        storage_client : storage.Client
            GCS client object

        dest_path : str
            Path for downloading files to the server

        bucket_name : str
            GCS bucket name

        blob_name : str
            GCS file path

        overwrite : bool
            Whether to overwrite files in the path or not.


        Returns
        -------
        None

        """
        bucket = storage_client.get_bucket(bucket_name)
        if not os.path.exists(dest_path) or overwrite:
            blobs = bucket.list_blobs(prefix=blob_name)  # Get list of files
            for blob in blobs:
                if blob.name.endswith("/"):
                    continue
                file_split = [
                    s for s in blob.name.replace(blob_name, "").split("/") if len(s) > 0
                ]
                if len(file_split) > 0:
                    directory = "/".join([dest_path, "/".join(file_split)])
                else:
                    directory = dest_path
                if len(file_split) > 0:
                    Path(directory[: -len(file_split[-1])]).mkdir(
                        parents=True, exist_ok=True
                    )
                else:
                    Path(directory).parent.absolute().mkdir(parents=True, exist_ok=True)
                blob.download_to_filename(directory)
        else:
            print(
                "The destination path already exists. If you want to overwrite, give overwrite parameter as True."
            )

    @staticmethod
    def print_log_messages(log_code: int):
        """Helper for printing log messages.

        Parameters
        ----------
        log_code : int
            Log message code.

        Returns
        -------
        None

        """

        log_message_dict = {
            0: "--- Session is started. ---",
            1: "--- Connected to GCP. ---",
            2: "--- Model parameters are ready for training. ---",
            3: "--- Splitting data into train / val sets for training... ---",
            4: "--- Encoding labels... ---",
            6: "--- Model training is started. ---",
            7: "--- Model training is done. Uploading model files to GCS... ---",
            8: "--- Removing existing ONNX model located at onnx_model_server_save_path... ---",
            9: "--- Model fitting is completed. ---",
            10: "--- Model files are downloaded & extracted from GCS. ---",
            11: "--- Model prediction is started. ---",
            12: "--- Ground truth labels are found in the data, printing classification report... ---\n",
            13: "--- Overwriting prediction results to the given table... ---",
            14: "--- Prediction results are saved to the result_save_path. ---",
            15: "--- Model prediction is completed. You can get the results with TextClassifier(...).test_data. ---",
            16: "--- You can also get the classification report result object with TextClassifier(...).cls_report. ---",
        }

        print(log_message_dict[log_code])

    @staticmethod
    def print_error_messages(error_code: int):
        """Helper for printing error messages.

        Parameters
        ----------
        error_code : int
            Error message code.

        Returns
        -------
        None

        """

        error_message_dict = {
            0: "Credentials path does not exist, check the path.",
            1: "Given classification_type is not supported. Only 'single' or 'multi' is allowed.",
            2: "nlp_credentials_path must be given if model_version is 'ty_bert' or 'ty_roberta'",
            3: "nlp_credentials_path does not exist, check the path.",
            4: "Bigquery train data table is empty, check the table.",
            5: "'text' column does not exist in the train table. Check the columns.",
            6: "'labels' column does not exist in the train table. Check the columns.",
            7: "Null rows exist in the 'text' column, check the data in train table.",
            8: "Null rows exist in the 'labels' column, check the data in train table.",
            9: "Either test_table_name or test_data must be given.",
            10: "test_table_name must be str, check the parameter.",
            11: "test_data must be pd.DataFrame, check the parameter.",
            12: "Either train_table_name or train_data must be given.",
            13: "BigQuery credentials path does not exist, check the path.",
            14: "nlp_project_id must be given if model_version is 'ty_bert' or 'ty_roberta'",
            15: "nlp_bucket_name must be given if model_version is 'ty_bert' or 'ty_roberta'",
            16: "nlp_blob_name must be given if model_version is 'ty_bert' or 'ty_roberta'",
            17: "gcloud_project_id must be given during class initialization if you want to use a BigQuery table during model training.",
            18: "gcloud_bucket_name must be given during class initialization if you want to use a BigQuery table during model training.",
            19: "gcloud_blob_name must be given during class initialization if you want to use a BigQuery table during model training.",
            20: "gcloud_credentials_path must be given during class initialization if you want to use a BigQuery table during model training.",
            21: "Bigquery validation data table is empty, check the table.",
            22: "'text' column does not exist in the validation table. Check the columns.",
            23: "'labels' column does not exist in the validation table. Check the columns.",
            24: "Null rows exist in the 'text' column, check the data in validation table.",
            25: "Null rows exist in the 'labels' column, check the data in validation table.",
        }

        return error_message_dict[error_code]

    @staticmethod
    def lowercase_turkish(text: str) -> str:
        """Helper for lowercasing Turkish text.

        Parameters
        ----------
        text : str
            Any text

        Returns
        -------
        str
            Lowercased text

        """

        return text.translate(str.maketrans("ĞIİÖÜŞÇ", "ğıiöüşç")).lower()

    def encode_labels(self, train_data=None, val_data=None):
        """Helper for encoding text labels.

        Parameters
        ----------
        train_data : pd.DataFrame
            Training data which labels are to be encoded.

        val_data : pd.DataFrame
            Validation data which labels are to be encoded.

        Returns
        -------
        None

        """

        if self.do_train:
            train_data["labels_original"] = train_data["labels"].tolist()

            if val_data is not None:
                val_data["labels_original"] = val_data["labels"].tolist()

            if self.classification_type == "single":
                label_encoder = LabelEncoder()

            else:
                label_encoder = MultiLabelBinarizer()
                train_data["labels"] = train_data["labels"].apply(
                    lambda x: [elem.strip() for elem in x.split(";")]
                )

                if val_data is not None:
                    val_data["labels"] = val_data["labels"].apply(
                        lambda x: [elem.strip() for elem in x.split(";")]
                    )

            train_data["labels"] = label_encoder.fit_transform(
                train_data["labels"].tolist()
            ).tolist()

            if val_data is not None:
                val_data["labels"] = label_encoder.transform(
                    val_data["labels"].tolist()
                ).tolist()

            return [train_data, val_data, label_encoder]

        else:
            val_data["labels_original"] = val_data["labels"].tolist()

            if self.classification_type == "multi":
                val_data["labels"] = val_data["labels"].apply(
                    lambda x: [elem.strip() for elem in x.split(";")]
                )

            val_data["labels"] = self.label_encoder.transform(
                val_data["labels"].tolist()
            ).tolist()
            return val_data

    def prepare_training_data(self) -> None:
        """Helper for creating training data.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # training data is valid, moving to model fitting procedure...
        self.train_data["text"] = self.train_data["text"].astype(str)

        if self.do_lowercase and self.data_lang == "tr":
            self.train_data["text"] = self.train_data["text"].apply(
                self.lowercase_turkish
            )

        if self.val_data is not None:
            self.val_data["text"] = self.val_data["text"].astype(str)

            if self.do_lowercase and self.data_lang == "tr":
                self.val_data["text"] = self.val_data["text"].apply(
                    self.lowercase_turkish
                )

        if self.do_train and self.val_data is None:
            self.print_log_messages(3)

            if self.classification_type == "single":
                try:
                    x_train, x_val, y_train, y_val = train_test_split(
                        self.train_data["text"],
                        self.train_data["labels"],
                        test_size=self.split_size,
                        random_state=self.random_state,
                        stratify=self.train_data["labels"],
                    )
                except:
                    x_train, x_val, y_train, y_val = train_test_split(
                        self.train_data["text"],
                        self.train_data["labels"],
                        test_size=self.split_size,
                        random_state=self.random_state,
                    )

                self.model_train_data = pd.DataFrame(
                    {"text": x_train.values, "labels": y_train.values}
                )

                self.model_val_data = pd.DataFrame(
                    {"text": x_val.values, "labels": y_val.values}
                )

                self.print_log_messages(4)
                (
                    self.model_train_data,
                    self.model_val_data,
                    self.label_encoder,
                ) = self.encode_labels(self.model_train_data, self.model_val_data)

            else:
                # Train and Evaluation data needs to be in a Pandas Dataframe containing at least two columns, a 'text' and a 'labels' column. The `labels` column should contain multi-hot encoded lists.
                self.print_log_messages(4)
                self.train_data, self.val_data, self.label_encoder = self.encode_labels(
                    self.train_data
                )

                try:
                    msss = MultilabelStratifiedShuffleSplit(
                        n_splits=1,
                        test_size=self.split_size,
                        random_state=self.random_state,
                    )

                    X = self.train_data["text"].values
                    y = np.vstack(self.train_data["labels"].values[:])
                    msss.get_n_splits(X, y)

                    x_train_dfs = []
                    x_test_dfs = []

                    for train_index, test_index in msss.split(X, y):
                        X_train, X_test = X[train_index], X[test_index]
                        y_train, y_test = y[train_index], y[test_index]

                        x_train_dfs.append(
                            pd.DataFrame(
                                {"text": X_train.tolist(), "labels": y_train.tolist()}
                            )
                        )

                        x_test_dfs.append(
                            pd.DataFrame(
                                {"text": X_test.tolist(), "labels": y_test.tolist()}
                            )
                        )

                    self.model_train_data = pd.concat(x_train_dfs, ignore_index=True)
                    self.model_val_data = pd.concat(x_test_dfs, ignore_index=True)

                except:
                    x_train, x_val, y_train, y_val = train_test_split(
                        self.train_data["text"],
                        self.train_data["labels"],
                        test_size=self.split_size,
                        random_state=self.random_state,
                    )

                    self.model_train_data = pd.DataFrame(
                        {"text": x_train.values, "labels": y_train.values}
                    )

                    self.model_val_data = pd.DataFrame(
                        {"text": x_val.values, "labels": y_val.values}
                    )

        else:
            (
                self.model_train_data,
                self.model_val_data,
                self.label_encoder,
            ) = self.encode_labels(self.train_data, self.val_data)

    def fit(
        self,
        train_table_name: Optional[str] = None,
        train_data: Optional[pd.DataFrame] = None,
        val_table_name: Optional[str] = None,
        val_data: Optional[pd.DataFrame] = None,
        print_model_card: Optional[bool] = True,
        **kwargs,
    ) -> None:
        """Function to fit the model. If the model is multilabel, data must be a dataframe with two columns:
        | text    | labels                      |
         ---------  ----------------------------
        | <text>  | <label_1>;<label_2>;...     |

        Parameters
        ----------
        train_table_name : str, optional
            Name of the BigQ table for training data

        train_data : pd.DataFrame, optional
            Training dataframe object

        val_table_name : str, optional
            Name of the BigQ table for validation data

        val_data : pd.DataFrame, optional
            Validation dataframe object


        Returns
        -------
        None

        """
        # prepare training data
        assert (
            train_table_name is not None or train_data is not None
        ), self.print_error_messages(12)

        # training essential checks
        if train_table_name is not None:
            assert self.gcloud_project_id is not None, self.print_error_messages(17)
            assert self.gcloud_bucket_name is not None, self.print_error_messages(18)
            assert self.gcloud_blob_name is not None, self.print_error_messages(19)
            assert self.gcloud_credentials_path is not None, self.print_error_messages(
                20
            )

            self.train_table_name = train_table_name

            QUERY = f"""
                   SELECT * FROM {self.train_table_name} LIMIT 1
                   """
            train_data = self.bigq_client.query(QUERY).to_dataframe()
            assert len(train_data), self.print_error_messages(4)
            assert "text" in train_data.columns.tolist(), self.print_error_messages(5)
            assert "labels" in train_data.columns.tolist(), self.print_error_messages(6)

            QUERY = f"""
                   SELECT * FROM {self.train_table_name}
                   """
            train_data = self.bigq_client.query(QUERY).to_dataframe()
            assert train_data["text"].isnull().sum() == 0, self.print_error_messages(7)
            assert train_data["labels"].isnull().sum() == 0, self.print_error_messages(
                8
            )

            # validation essential checks
            if val_table_name is not None:
                self.val_table_name = val_table_name

                QUERY = f"""
                       SELECT * FROM {self.val_table_name} LIMIT 1
                       """
                val_data = self.bigq_client.query(QUERY).to_dataframe()
                assert len(val_data), self.print_error_messages(21)
                assert "text" in val_data.columns.tolist(), self.print_error_messages(
                    22
                )
                assert "labels" in val_data.columns.tolist(), self.print_error_messages(
                    23
                )

                QUERY = f"""
                   SELECT * FROM {self.val_table_name}
                   """
                val_data = self.bigq_client.query(QUERY).to_dataframe()
                assert val_data["text"].isnull().sum() == 0, self.print_error_messages(
                    24
                )
                assert (
                    val_data["labels"].isnull().sum() == 0
                ), self.print_error_messages(25)

        if train_data is not None:
            assert len(train_data), self.print_error_messages(4)
            assert "text" in train_data.columns.tolist(), self.print_error_messages(5)
            assert "labels" in train_data.columns.tolist(), self.print_error_messages(6)
            assert train_data["text"].isnull().sum() == 0, self.print_error_messages(7)
            assert train_data["labels"].isnull().sum() == 0, self.print_error_messages(
                8
            )

        if val_data is not None:
            assert len(val_data), self.print_error_messages(21)
            assert "text" in val_data.columns.tolist(), self.print_error_messages(22)
            assert "labels" in val_data.columns.tolist(), self.print_error_messages(23)
            assert val_data["text"].isnull().sum() == 0, self.print_error_messages(24)
            assert val_data["labels"].isnull().sum() == 0, self.print_error_messages(25)

        self.train_data = train_data
        self.val_data = val_data
        self.prepare_training_data()
        self.print_log_messages(6)

        # Following Andrew Ng's advice on selecting mini-batch size
        # https://cs230.stanford.edu/files/C2M2.pdf
        if len(self.model_train_data) <= 2000 and "train_batch_size" not in self.model_args:
            self.model_args["train_batch_size"] = 1

        self.model_args["evaluate_during_training"] = self.model_val_data is not None
        eval_df = (
            self.model_val_data[["text", "labels"]]
            if self.model_val_data is not None
            else None
        )

        # build model
        if self.classification_type == "single":
            self.model_args = ClassificationArgs(**self.model_args)

            # only final layer (classification layer) finetuning may prevent overfitting
            if self.train_only_final_layer:
                self.model_args.custom_parameter_groups = self.freeze_layers_dict

            self.model = ClassificationModel(
                self.model_type,
                self.model_version,
                use_cuda=True if len(self.gpus_to_use) else False,
                args=self.model_args,
                num_labels=len(list(self.label_encoder.classes_)),
            )

            # train model

            _, self.training_details = self.model.train_model(
                self.model_train_data[["text", "labels"]],
                eval_df=eval_df,
                f1=f1_multiclass,
                acc=accuracy_score,
                prec=precision_multiclass,
                recall=recall_multiclass,
            )

        else:
            self.model_args = MultiLabelClassificationArgs(**self.model_args)

            # only final layer (classification layer) finetuning may prevent overfitting
            if self.train_only_final_layer:
                self.model_args.custom_parameter_groups = self.freeze_layers_dict

            self.model = MultiLabelClassificationModel(
                self.model_type,
                self.model_version,
                use_cuda=True if len(self.gpus_to_use) else False,
                args=self.model_args,
                num_labels=len(list(self.label_encoder.classes_)),
            )

            _, self.training_details = self.model.train_model(
                self.model_train_data[["text", "labels"]], 
                eval_df=eval_df,
                f1=f1_multilabel,
                acc=accuracy_multilabel,
                precision=precision_multilabel,
                recall=recall_multilabel
            )

        # save model metadata & label encoder
        self.model_metadata = {
            "model_type": self.model_type,
            "task_type": self.classification_type,
            "do_eval": eval_df is not None,
            "do_lowercase": self.do_lowercase,
            "data_lang": self.data_lang
        }

        joblib.dump(self.label_encoder, self.label_encoder_dir)
        joblib.dump(self.model_metadata, self.model_metadata_dir)

        # save original model
        model_save_path = (
            os.path.join(self.model_dir, "best_model")
            if self.model_metadata["do_eval"]
            else os.path.join(self.model_dir, "outputs")
        )
        kwargs["model_card_path"] = (
            os.path.join(model_save_path, "model_card.md")
            if "model_card_path" not in kwargs
            else kwargs["model_card_path"]
        )

        if self.model_metadata["do_eval"]:
            shutil.copyfile(
                os.path.join(self.model_dir, "outputs", "training_progress_scores.csv"),
                os.path.join(
                    self.model_dir, "best_model", "training_progress_scores.csv"
                ),
            )

        if print_model_card:
            create_model_card(**kwargs)

            try:
                self.upload_to_gcs(
                    self.storage_client,
                    kwargs["model_card_path"],
                    self.gcloud_bucket_name,
                    os.path.join(
                        os.path.split(self.model_bigq_dir)[0],
                        os.path.split(kwargs["model_card_path"])[-1],
                    ),
                )
            except:
                pass

        make_archive(model_save_path, "gztar", root_dir=model_save_path)

        if self.gcloud_bucket_name is not None:
            self.print_log_messages(7)
            
            self.upload_to_gcs(
                self.storage_client,
                model_save_path + ".tar.gz",
                self.gcloud_bucket_name,
                self.model_bigq_dir,
            )

        # save onnx model
        if self.save_onnx_model:
            if os.path.exists(self.onnx_model_dir):
                self.print_log_messages(8)
                shutil.rmtree(self.onnx_model_dir)

            copy.deepcopy(self.model).convert_to_onnx(self.onnx_model_dir)
            make_archive(self.onnx_model_dir, "gztar", root_dir=self.onnx_model_dir)

            if self.gcloud_bucket_name is not None:
                self.upload_to_gcs(
                    self.storage_client,
                    self.onnx_model_dir + ".tar.gz",
                    self.gcloud_bucket_name,
                    self.onnx_model_bigq_dir,
                )

        self.print_log_messages(9)

    def predict(
        self,
        test_table_name: Optional[str] = None,
        test_data: Optional[pd.DataFrame] = None,
        result_save_path: Optional[str] = None,
    ) -> str:
        """Function to get predictions from the model.
        If the model is multilabel, data must be a dataframe with two columns:
        | text    | labels                      |
         ---------  ----------------------------
        | <text>  | <label_1>;<label_2>;...     |

        Parameters
        ----------
        test_table_name : str
            Name of the BigQ table for test data

        test_data : pd.DataFrame
            Test dataframe for prediction.

        result_save_path : str
            .csv path for saving results after prediction

        Returns
        -------
        None

        """
        assert (
            test_data is not None or test_table_name is not None
        ), self.print_error_messages(9)

        if test_table_name is not None:
            assert self.gcloud_project_id is not None, self.print_error_messages(17)
            assert self.gcloud_bucket_name is not None, self.print_error_messages(18)
            assert self.gcloud_blob_name is not None, self.print_error_messages(19)
            assert self.gcloud_credentials_path is not None, self.print_error_messages(
                20
            )

            self.test_table_name = test_table_name

            QUERY = f"""
               SELECT * FROM {self.test_table_name} LIMIT 1
               """
            test_data = self.bigq_client.query(QUERY).to_dataframe()
            assert len(test_data), self.print_error_messages(4)
            assert "text" in test_data.columns.tolist(), self.print_error_messages(5)

            QUERY = f"""
                   SELECT * FROM {self.test_table_name}
                   """

            test_data = self.bigq_client.query(QUERY).to_dataframe()
            assert test_data["text"].isnull().sum() == 0, self.print_error_messages(7)

            if "labels" in test_data.columns.tolist():
                assert (
                    test_data["labels"].isnull().sum() == 0
                ), self.print_error_messages(8)

        if test_data is not None:
            assert isinstance(test_data, pd.DataFrame), self.print_error_messages(11)
            assert len(test_data), self.print_error_messages(4)
            assert "text" in test_data.columns.tolist(), self.print_error_messages(5)
            assert test_data["text"].isnull().sum() == 0, self.print_error_messages(7)

            if "labels" in test_data.columns.tolist():
                assert (
                    test_data["labels"].isnull().sum() == 0
                ), self.print_error_messages(8)

        # test data is valid, moving to prediction routine...
        self.print_log_messages(11)
        self.result_save_path = result_save_path
        self.do_train = False
        self.test_data = test_data
        self.test_data["text"] = self.test_data["text"].astype(str)

        if self.model_metadata["do_lowercase"] and self.model_metadata["data_lang"] == "tr":
            self.test_data["text"] = self.test_data["text"].apply(self.lowercase_turkish)

        self.predictions, self.raw_outputs = self.model.predict(
            self.test_data["text"].tolist()
        )

        if self.model_metadata["task_type"] == "single":
            confidence_scores = softmax(self.raw_outputs, axis=1)
            self.test_data["predictions_encoded"] = self.predictions
            self.test_data["predictions"] = self.label_encoder.inverse_transform(
                np.array(self.predictions)
            )
            self.test_data["predictions_confidence_scores"] = confidence_scores.max(
                axis=1
            )

            confidence_score_df = pd.DataFrame(
                confidence_scores, columns=self.label_encoder.classes_.tolist()
            )
        else:
            predictions_raw = []
            confidence_scores = []

            for i in range(len(self.raw_outputs)):
                predictions_raw.append(
                    ", ".join(
                        self.label_encoder.inverse_transform(
                            np.array(self.predictions[i]).reshape(1, -1)
                        )[0]
                    )
                )
                confidence_scores.append(
                    self.raw_outputs[i][np.nonzero(self.predictions[i])[0]]
                )

            self.test_data["predictions_encoded"] = self.predictions
            self.test_data["predictions"] = predictions_raw
            self.test_data["predictions_confidence_scores"] = confidence_scores

            confidence_score_df = pd.DataFrame(
                self.raw_outputs, columns=self.label_encoder.classes_.tolist()
            )

        self.test_data = pd.concat([self.test_data, confidence_score_df], axis=1)

        if "labels" in self.test_data.columns.tolist():
            self.print_log_messages(12)

            self.test_data = self.encode_labels(val_data=self.test_data)
            print(
                classification_report(
                    self.test_data["labels"].tolist(),
                    self.test_data["predictions_encoded"].tolist(),
                    digits=4,
                    target_names=[
                        str(elem) for elem in self.label_encoder.classes_.tolist()
                    ],
                )
            )

            self.cls_report = classification_report(
                self.test_data["labels"].tolist(),
                self.test_data["predictions_encoded"].tolist(),
                target_names=[
                    str(elem) for elem in self.label_encoder.classes_.tolist()
                ],
                digits=4,
                output_dict=True,
            )

            self.cls_report = pd.DataFrame(self.cls_report).T
            
            if self.do_train:
                self.cls_report_path = (
                    os.path.join(self.model_dir, "best_model", "cls_report.csv")
                    if self.model_metadata["do_eval"]
                    else os.path.join(self.model_dir, "outputs", "cls_report.csv")
                )
                self.cls_report.to_csv(self.cls_report_path)

            self.print_log_messages(16)

            reindex_cols = ["text", "labels_original"] + [
                elem
                for elem in self.test_data.columns.tolist()
                if elem not in ["text", "labels_original"]
            ]
            self.test_data = self.test_data[reindex_cols]

        if result_save_path is not None:
            self.test_data.to_csv(result_save_path, index=False)
            self.print_log_messages(14)

        self.print_log_messages(15)

            