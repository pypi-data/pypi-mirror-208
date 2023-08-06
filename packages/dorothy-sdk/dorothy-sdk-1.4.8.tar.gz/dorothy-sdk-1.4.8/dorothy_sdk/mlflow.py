"""
Módulo de apoio ao uso do MLFlow
"""

import mlflow
import json
import lpsds.mlflow
from dorothy_sdk.dataset_wrapper import Dataset


class MLFlow(lpsds.mlflow.MLFlow):

    def __init__(self, run_id=None, flavor=mlflow.sklearn):
        """
        Class constructor.

        Input:
          - run_id. The MLFlow run ID you want to manipulate. If None, then a new run is created.
          - flavor: the model flavor (mlflow.sklearn, mlflow.tensoflow, etc.) to be use to manage trained models.
        """
        super().__init__(run_id)
        self.flavor = flavor


    def _get_model_path(self, partition :int=None, split :int=None) -> str:
        """
        Defines the path from where to collect the trained module.

        Input:
          - partition: the CV fold (0-9) from which the model was obtained. If None, then
                       saves as the operation model.
          - split: which split to index (0-8) to id the model. If None, then
                       saves as the operation model.
        
          Only one value set to None suffices to return the operation model path.
        Returns: the folder name where the model can be found.
        """
        if partition is None or split is None:
          return 'operation_model'
        return f'model_part_{partition}_split_{split}'


    def load_model(self, partition :int=None, split :int=None, **kwargs):
        """
        Gets the operating model or the model from a specific fold.

        Input:
          - partition: the CV fold (0-9) from which the model was obtained. If None, then
                       saves as the operation model.
          - split: which split to index (0-8) to id the model. If None, then
                       saves as the operation model.
          - **kwargs: passed to mlflow.load_model
        
          Only one value set to None suffices to return the operation model path.          

        Returns: an instance to the trained object.
        """
        fold = self._get_model_path(partition, split)
        return self.flavor.load_model(self.run.info.artifact_uri + '/' + fold, **kwargs)
  

    def log_model(self, model, partition :int=None, split :int=None, **kwargs):
        """

        Saves the operating model or the model from a specific fold.

        Input parameters:
          - model: the trained module to be saved.
          - partition: the CV fold (0-9) from which the model was obtained. If None, then
                       saves as the operation model.
          - split: which split to index (0-8) to id the model. If None, then
                       saves as the operation model.
          - **kwargs: passed to mlflow.log_model
        
        Only one value set to None suffices to return the operation model path.
        """
        fold = self._get_model_path(partition, split)
        self.flavor.log_model(model, fold, registered_model_name="ImageClassifier", **kwargs)


    def load_dataset(self, dataset_name, perform_cv_split=False):
      dataset_list = json.loads(self.run.data.params[dataset_name])
      return Dataset.join_datasets(dataset_list, perform_cv_split=perform_cv_split)
