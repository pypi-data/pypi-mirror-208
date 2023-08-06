import os
import time
import cpuinfo
import nvsmi
import psutil
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
import dorothy_sdk.dataset_wrapper as dw
import dorothy_sdk.mlflow as dmlf
from lpsds.inout import save, get_path

########### INSTRUÇÕES DE DESENVOLVIMENTO ############################
#
# Muitas das funções abaixo já foram implementadas de forma que não precisarão ser alteradas. Muito, MUITO provavelmente
# você só precisará alterar para os eu caso específico, o método "operate_model" (veja em operation_specific.py um exemplo)
#
# Caso vc REALMENTE precise mexer em alguns dos métodos já implementdos abaixo, faça através de uma nova classe que herde
# de ModelOperation, mexendo somente nos métodos necessários e respeitando sempre os requisitos de entrada e saída de
# cada método.
#

class ModelOperation:
    """
    Esta função define a os métodos necessários para a operação do seu modelo.

    Muito provavelmente você só precisará implementar o método operate_model.
    """

    def __init__(self, mlflow_module_flavor, device_type='cpu',
                    img_path_col_name='image_local_path', label_col_name='y_true'):
        """
        Construtor da classe.
        
        Parâmetros:
        - mlflow_module_flavor: flavor do mlflow do seu modelo. Opções
                                (entre outras), são mlflow.pytorch, mlflow.sklearn, mlflow.tensorflow.
        - device_type: se a execução do modelo se dará em 'cpu' ou 'gpu'.
        - img_path_col_name: nome da coluna no dataframe de metadados que contém o path local para as imagens.
        - label_col_name: nome da coluna no dataframe que contém os alvos do modelo (1 ou 0)
        """
        assert device_type in ['gpu', 'cpu'], 'device_type must be either "cpu" or "gpu"'
        self.mlflow_module_flavor = mlflow_module_flavor
        self.runs_path = 'output/runs'
        self.models_path = 'output/models'
        self.device_type = device_type
        self.img_path_col_name = img_path_col_name
        self.label_col_name = label_col_name
        self.device = self.get_device()
    

    def operate_model(self, model, X, decision_threshold: float=0.5):
        """
        Aqui você deve definir o código responsável por passar o conjunto de imagens pelo modelo.
        Esta função deve retornar 2 numpy.arrays:
            - y_proba: contendo o valor da saída do modelo para cada amostra em X.
            - y_pred: contendo a decisão do modelo para cada amostra em X

        VOCÊ DEVE ALTERAR ESTA FUNÇÃO PARA O SEU CASO ESPECÍFICO, ATENTANDO QUE ELA
        PRECISA MANTER INALTERADOS SEUS PARÂMETROS DE ENTRADA E SAÍDA.
        """
        raise NotImplemented


    def predict(self, model, X, decision_threshold: float=0.5) -> float:
        """
        Esta função deve prover a decisão do modelo para uma única imagem fornecida
        (não pode ser um conjunto de imagens).
        """
        raise NotImplemented


    def train_model(self, trn_df: pd.DataFrame , val_df: pd.DataFrame, **kwargs):
        """
        Esta função é responsável por treinar um modelo (sem CV) a partir de um dataframe de treino e um de validação.
        O modelo retornado deve ser capaz de ser passado para os métodos operate_model e predict.

        Input:
          - trn_df: dataframe contendo os dados de treinamento (path para as imagens e seus alvos)
          - val_df: dataframe contendo os dados de validação (path para as imagens e seus alvos)
          - **kwargs: qualquer hiperparâmetro necessário ao treinamento do modelo.

        Return: modelo treinado.
        """
        raise NotImplemented
    

    def _save_model(self, model, file_name: str) -> None:
        """
        Esta função deve definir a lógica necessária para salvar um modelo no path passado.
        Entrada:
          - model: uma instância de modelo treinada.
          - file_name: path onde salvar o modelo.
        """
        raise NotImplemented


    def _load_model(self, file_name: str):
        """
        Esta função deve definir a lógica necessária para carregar um modelo salvo em disco.
        O modelo retornado deve ser capaz de ser passado para os métodos operate_model e predict.

        Entrada:
          - file_name: path onde salvar o modelo.
        
        Retorno: a instância treinada salva no local especificado.
        """
        raise NotImplemented


    def get_device(self):
        """
        Deve retornar o identificador do dispositivo a ser usado ('/CPU:0', torch.device('cuda'), etc.)
        de acordo com o valor de self.device_type, que pode ser cpu ou gpu.
        """
        raise NotImplemented


    def get_dataset_images(self, validation_dataset_name):
        """
        Nesta função, vc deve colocar o código necessário para carregar as imagens de um dataset do DORTHY
        Esta função deve retornar:

            - um tensor X que possa ser passado diretamente ao método "predict" do modelo.
            - um pandas.DataFrame com os metadados deste dataset (id de cada imagem, sexo, idade, etc.)
        
        MUITO PROVAVELMENTE VOCÊ NÃO PRECISARÁ MEXER NESSA FUNÇÃO
        """
        dataset = dw.Dataset(validation_dataset_name)
        metadata = dataset.load_metadata()
        X,_ = dw.Dataset.load_from_file(metadata)
        return X, metadata


    def get_operation_model(self, mlflow_run_id):
        """
        Nesta função, vc deve implementar o código necessário para buscar no MLFlow server o SEU MODELO DE OEPRAÇÃO.
        A saída desta função deve ser um modelo pronto para ser operado através das suas funções predict e predict_proba.

        O MLFlow tem "sabores" específicos para vários frameworks (PyTorch, tensorflow, sklearn, etc.). Você deve usar
        o sabor correto (no exemplo abaixo, o modelo foi produzido pelo pytorch, logo o sabor correto aqui é o mlflow.pytorch).
        Veja detalhes aqui: https://mlflow.org/docs/1.8.0/python_api/index.html

        MUITO PROVAVELMENTE VOCÊ NÃO PRECISARÁ MEXER NESSA FUNÇÃO
        """
        run = dmlf.MLFlow(mlflow_run_id, flavor=self.mlflow_module_flavor)
        model = run.load_model()
        threshold = float(run.get_params().decision_threshold)
        return model, threshold
    

    def get_processing_stats(self, model, X) -> pd.DataFrame:
        """
        Esta função gera estatística de execução tais como tempo de processamento, memória consumida, etc.
        """

        #Pre-allocating the values storage space so it won´t
        #interfere with the memory usage calculation.
        elapsed_time = np.empty(X.shape[0])
        memory_used = np.empty(X.shape[0])
        process = psutil.Process(os.getpid())

        for i,x in enumerate(X):
            start_time = time.time()
            self.predict(model, x)
            elapsed_time[i] = time.time() - start_time
            memory_used[i] = process.memory_info().rss

        cpu = cpuinfo.get_cpu_info()
        gpu = tuple(nvsmi.get_gpus())[0]
        max_allowed_cpu = os.environ.get('NUM_ALLOWED_CPUS', None)
        #NUM_ALLOWED_CPUS may come as NUM_ALLOWED_CPUS=''
        if not max_allowed_cpu: max_allowed_cpu = cpu['count']

        ret = pd.DataFrame({'elapsed_time_sec' : elapsed_time, 'memory_used_bytes' : memory_used})
        ret['num_logical_cpu'] = cpu['count']
        ret['max_logical_cpu_allowed'] = max_allowed_cpu
        ret['cpu_type'] = cpu['brand_raw']
        ret['cpu_clock_mhz'] = psutil.cpu_freq(percpu=False).current
        ret['cpu_mem_gb'] = psutil.virtual_memory().total / (1024**3)
        ret['gpu_type'] = gpu.name
        ret['gpu_mem_gb'] = gpu.mem_total / 1024
        ret['device_used'] = self.device_type


        return ret


    def save_results(self, path, dataset_metadata, y_proba=None, y_pred=None):
        """
        Aqui os vetores de saídas são incorporados ao dataframe de metadados proveniente do DOROTHY e
        salvos na pasta correta para análise posterior.

        MUITO PROVAVELMENTE VOCÊ NÃO PRECISARÁ MEXER NESSA FUNÇÃO
        """

        if y_proba is not None: dataset_metadata['y_proba'] = y_proba
        if y_pred is not None: dataset_metadata['y_pred'] = y_pred
        dataset_metadata.to_parquet(path)


    def save_model(self, model, path, threshold :float=0.5):
        """
        Salva o modelo produzido.

        MUITO PROVAVELMENTE VOCÊ NÃO PRECISARÁ MEXER NESSA FUNÇÃO
        """
        self._save_model(model, path, threshold)
    

    def load_model(self, fname :str):
        """
        carrega um modelo salvo em disco. Precisa retornar uma tuple (model, threshold)
        """
        full_path = get_path(dir_name=self.models_path, fname=fname)
        return self._load_model(full_path)


def get_fold_data(cv_model: dict, cv_splits: list, fold_idx: int) -> tuple:
     """"
     def get_fold_data(cv_model: dict, cv_splits: list, X: Union[pd.DataFrame, np.array], y_true: Union[pd.Series, np.array], fold_idx: int) -> tuple
     Returns the data corresponding to a given cross validation fold.
     Input parameters:
       - cv_model: a dictionary with structure equivalent to the one returned by sklearn.model_selection.cross_validate.
       - cv_splits: a list where each item is a tuple containing the indexes to be used for training and testing in
                    see dataset_wrapper.Dataset.train_test_split, for isntance, for details.
       - fold_idx: the index of the cv fold you want to collect the data.
    
     Returns:
       - tst_df: the target set used for testing in the desired fold as a dataframe.
       - model: the operation model yielded by the desired fold.
     """
     _, tst_df = cv_splits[fold_idx]
     model = cv_model['estimator'][fold_idx]
    
     return tst_df, model



def get_operation_model(cv_model: dict, cv_splits: list, metric:str='test_sp', less_is_better:bool=False) -> tuple:
    """"
    get_operation_model(cv_model: dict, cv_splits: list, X: Union[pd.DataFrame, np.array], y_true: Union[pd.Series, np.array], metric:str='test_sp', less_is_better:bool=False) -> tuple
    Returns the operation model and its corresponding data. For that, it finds
    the model yielding the best metric over its corresponding testing set.
    Input parameters:
      - cv_model: a dictionary with structure equivalent to the one returned by sklearn.model_selection.cross_validate.
      - cv_splits: a list where each item is a tuple containing the indexes to be used for training and testing in
                   see sklearn.model_selection.KFold, for isntance, for details.
      - metric: a key within cv_model containing the metric to use to compare cv folds.
      - less_is_better: if True, the best fold will be the one where the passed metric is the lowest (MSE, for instance). The highest
                        will be returned if this value is set to True (Accuracy, for instance).
    
    Returns:
      - best_fold: the id of the fold yielding the operation model.
       - tst_df: the target set used for testing in the desired fold as a dataframe.
       - model: the operation model yielded by the desired fold.
    """
    best_fold = cv_model[metric].argmin() if less_is_better else cv_model[metric].argmax()
    tst_df, model = get_fold_data(cv_model, cv_splits, best_fold)
    return best_fold, tst_df, model