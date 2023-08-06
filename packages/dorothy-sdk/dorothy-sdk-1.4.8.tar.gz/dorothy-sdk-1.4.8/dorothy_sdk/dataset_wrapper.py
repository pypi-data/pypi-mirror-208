"""
This module acts as a wrapper on top of DOROTHY sdk low level features.

It creates a cached environment and save files in a format more easily read
than reading image by image.
"""

import os
import pickle
import numpy as np
import pandas as pd
import dorothy_sdk as sdk
from PIL import Image, ImageOps
from typing import List, Tuple


class Dataset:
    """
    Base class.
    """
    def __init__(self, dataset):
        self.dataset = dataset
        self.client = sdk.Client()
        self.data_file_name = f'{self.dataset}-data.npy'
        self.metadata_file_name = f'{self.dataset}-metadata.parquet'
        self.cv_split_file_name = f'{self.dataset}-cv_split.parquet'
        self.cache_location = self._get_cache_location()
        self.image_width = 256
        self.image_height = 256
        self.image_grayscale = True

    def _get_cache_location(self):
        """Gets the cache location from dorothy sdk module."""
        # img_sample = self.client.dataset(self.dataset).list_images()[0]
        # return img_sample._cache_location
        return os.environ['DOROTYSDK_CACHE_LOCATION']

    def _cache_exists(self, data_name):
        return os.path.exists(os.path.join(self.cache_location, data_name))

    def load_metadata(self):
        """
        Returns the dataset metadata, which includes:
          - Image file names
          - Image target (y_true)
          - CV split info
        """
        if not self._cache_exists(self.metadata_file_name):
            self._assemble_dataset()
        return pd.read_parquet(os.path.join(self.cache_location, self.metadata_file_name))


    def load_cv_splits(self):
        """Returns a list of trn and tst indexes for each fold"""
        if not self._cache_exists(self.cv_split_file_name):
            self._assemble_cv_splits()
        return pd.read_parquet(os.path.join(self.cache_location, self.cv_split_file_name))

    
    def _assemble_dataset(self):
        """Download and create a local version of the dataset"""
        ds = self.client.dataset(self.dataset)
        metadata_list = []
        for img in ds.list_images():
            img.download_image(width=self.image_width, height=self.image_height, gray_scale=self.image_grayscale)
            image_local_path = os.path.join(self.cache_location, img._cached_image_name) if img._cache_enabled else None
            metadata_list.append({'image_url' : img.image_url, 'metadata' : img.metadata, 'image_local_path' : image_local_path})

        #Creating the metadata dataframe and saving it.
        df = self._assemble_metadata(metadata_list)
        df['y_true'] = 1
        df.loc[df.has_tb == False, 'y_true'] = 0
        meta_file_name = os.path.join(self.cache_location, self.metadata_file_name)
        df.to_parquet(meta_file_name)

    
    def _assemble_metadata(self, metadata_list):
        df = pd.DataFrame(columns=['url', 'image', 'gender', 'age', 'synthetic', 'date_exam', 'original_report', 'has_tb', 'additional_information', 'image_local_path'])
        for id, img in enumerate(metadata_list):
            image_name = img['image_url'][:-1] if img['image_url'][-1] == '/' else img['image_url']
            image_name = os.path.split(image_name)[1]
            df.loc[len(df)] = (img['image_url'],
                                image_name,
                                img['metadata']['gender'],
                                img['metadata']['age'],
                                img['metadata']['synthetic'],
                                img['metadata']['date_exam'],
                                img['metadata']['original_report'],
                                img['metadata']['has_tb'],
                                img['metadata']['additional_information'],
                                img['image_local_path'],
                                )

        #Saving metadata
        df.gender.replace(to_replace={'F' : 'female', 'M' : 'male'}, inplace=True)
        return df


    def _assemble_cv_splits(self):
        ds = self.client.dataset(self.dataset)
        file = ds.get_cross_validation_file()
        partition = pickle.loads(file)

        cols = ['partition', 'inner_split', 'set_type', 'image']
        df = pd.DataFrame(columns=cols)

        for i1, d1 in enumerate(partition):
            for i2, d2 in enumerate(d1):
                for i3, d3 in enumerate(d2):
                    for img_name in d3:
                        df.loc[len(df)] = i1, i2, i3, img_name
        
        set_map = {0 : 'train', 1 : 'validation', 2 : 'test'}
        df['set_type'] = df.set_type.map(set_map).astype(str)
        file_name = os.path.join(self.cache_location, self.cv_split_file_name)
        df.to_parquet(file_name)


    @staticmethod    
    def join_datasets(datasets, perform_cv_split=True) -> pd.DataFrame:
        """
        def join_datasets(datasets):
        
        Concatena os cv_splits de cada dataset especificado, e os enriquece com os metadados,
        gerando uma tabela completa com todas as infos disponíveis para o conjunto de datasets.

        Entrada: múltiplos nomes de datasets. i.e: join_datasets(['china', 'manaus']).

        Retorno: um dataframe com os cv splits enriquecidos com os metadados de cada imagem.
        """
        
        ds_list = []
        for ds_name in datasets:
            ds = Dataset(ds_name)
            meta = ds.load_metadata()
            meta['dataset'] = ds.dataset
            
            if perform_cv_split:
                cv_splitter = ds.load_cv_splits()
                meta = cv_splitter.merge(meta, how='inner', on='image')
            
            ds_list.append(meta)
        
        return pd.concat(ds_list, ignore_index=True)


    @staticmethod
    def train_test_split(cv_df :pd.DataFrame) -> List[ Tuple[pd.DataFrame, List[Tuple[pd.DataFrame, pd.DataFrame]]] ]:
        """    
        Cria uma lista de indices de validação cruzada no estilo do train_test_split do sklearn, porem usando
        a estrutura de CV do projeto. Isso significa que ela retorna todos as splits tst x treino onde treino
        é uma lista de splits trn x val.

        Entrada:
        - cv_df: um dataframe do tipo do retornado por ds.load_cv_splits()
        
        Retorno: uma lista de tuples onde cada tuple contém (inner_split_cv, tst_metadata), onde inner_split_cv
                é uma lista contendo tuples (trn_df, val_df).
        """
        
        ret = []
        for partition in cv_df.partition.drop_duplicates().sort_values():
            tst_df = cv_df.loc[(cv_df.partition==partition) & (cv_df.set_type == 'test')].drop_duplicates('image')
            
            inner_split_list = []
            for inner_split in cv_df.inner_split.drop_duplicates().sort_values():
                inner_df = cv_df.loc[(cv_df.partition==partition) & (cv_df.inner_split==inner_split)]
                val_df = inner_df.loc[inner_df.set_type == 'validation'].drop_duplicates('image')
                trn_df = inner_df.loc[inner_df.set_type == 'train'].drop_duplicates('image')
                inner_split_list.append( (trn_df, val_df) )

            ret.append( (inner_split_list, tst_df) )

        return ret

    @staticmethod
    def load_from_file(df: pd.DataFrame, path_col_name: str='image_local_path', label_col_name: str='y_true'):
        img_list = [Dataset.pre_process_image(Image.open(r[path_col_name])) for _,r in df.iterrows()]
        X = np.concatenate(img_list, axis=0)
        y_true = df[label_col_name].to_numpy()
        return X, y_true

    @staticmethod
    def pre_process_image(img :Image) -> np.ndarray:
        """Make a local image complient. You should use this method after
        loading an image either from DOROTHY or local path (cache)"""
        img = ImageOps.grayscale(img)
        #We must add a dimension here so concatenate will concatenate over it later.
        return np.expand_dims(np.array(img), axis=0)
