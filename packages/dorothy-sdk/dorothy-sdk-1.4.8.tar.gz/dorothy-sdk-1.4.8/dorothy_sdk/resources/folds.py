import os
import pickle
from csv import DictWriter
from dataclasses import dataclass, field
from io import BytesIO
from os import mkdir
from os.path import exists, isdir
from typing import Dict, Any, Iterable, List

import pandas as pd
from PIL import Image as PILImage
from requests import Session

from dorothy_sdk.utils import url_join


class ImageFoldInstance:

    def __init__(self, session,
                 dataset_name: str,
                 image_url: str,
                 project_id: str,
                 image_path: str,
                 has_tb: int):
        self._session = session
        self.dataset_name = dataset_name
        self._image_url = image_url
        self.project_id = project_id
        self._image_path = image_path
        self.has_tb = has_tb

    @property
    def pillow(self) -> PILImage:
        buffer = BytesIO()
        if self._image_path is None:
            self._image_path = f"./{self.dataset_name}/{self.project_id}"
        if exists(self._image_path):
            with open(self._image_path, mode='rb') as file:
                buffer.write(file.read())
            buffer.seek(0)
            return PILImage.open(buffer)
        else:
            if not isdir(f"./{self.dataset_name}"):
                mkdir(f"./{self.dataset_name}")
            request = self._session.get(self._image_url)
            request.raise_for_status()
            buffer.write(request.content)
            buffer.seek(0)
            with open(f"./{self.dataset_name}/{self.project_id}.png", mode='wb') as file:
                file.write(request.content)
            return PILImage.open(buffer)


@dataclass()
class Fold:
    name: str = field()
    train: List[ImageFoldInstance] = field(default_factory=list)
    test: List[ImageFoldInstance] = field(default_factory=list)
    validation: List[ImageFoldInstance] = field(default_factory=list)


class CrossValidationFold:
    resource = "dataset/{name}/folds/"
    dataset: str = None
    cluster_id: str = None
    file_url: str = None

    def __init__(self, session: Session, host: str, **kwargs):
        self._session: Session = session
        self._service_host = host
        self._images_folds_object = None
        if kwargs.get("datasets"):
            self.datasets = kwargs.get("datasets")
            if isinstance(self.datasets, str):
                self.datasets = [self.datasets]
            if not isinstance(self.datasets, list):
                raise ValueError("'datasets' must bu a list-like object")

    def _fetch_api_data(self, dataset) -> List[Dict[str, Any]]:
        results = []
        url = url_join(self._service_host, self.resource.format_map({"name": dataset}))
        request = self._session.get(url)
        request.raise_for_status()
        if request.status_code == 200:
            response = request.json()
            while response.get("next", None) is not None:
                for data in response.get("results"):
                    results.append(data)
                request = self._session.get(response.get("next"))
                response = request.json()
            if response.get("next", None) is None and len(response.get("results", [])) > 0:
                for data in response.get("results"):
                    results.append(data)
        return results

    def _generate_fold_aggregation(self):
        if not self._images_folds_object:
            agg = {f"fold_{x}_{y}": Fold(name=f"fold_{x}_{y}") for x in range(10) for y in range(9)}
            for dataset in self.datasets:
                results = self._fetch_api_data(dataset)
                for element in results:
                    image_instance = ImageFoldInstance(self._session,
                                                       dataset_name=dataset,
                                                       image_url=element.get("image_url"),
                                                       project_id=element.get("image_project_id"),
                                                       image_path=element.get("image_path"),
                                                       has_tb=element.get("has_tb")
                                                       )
                    fold = agg[element.get("fold_name")]
                    role = element.get("role")
                    if role.upper() == "TRAIN":
                        fold.train.append(image_instance)
                    elif role.upper() == "TEST":
                        fold.test.append(image_instance)
                    else:
                        fold.validation.append(image_instance)
            self._images_folds_object = agg
            return agg
        else:
            return self._images_folds_object

    def get_folds(self, fold_name: str = None) -> Iterable[Fold]:
        fold_images: Dict[str, Any] = self._generate_fold_aggregation()
        if fold_name:
            yield fold_images[fold_name]
        else:
            for _, value in sorted(fold_images.items()):
                yield value

    def _get_folds_as_json(self) -> Iterable[Dict[str, Any]]:
        results = list(self.get_folds())
        for result in results:
            row = {
                "fold_name": result.name,
                "test": result.name.replace("fold_", "").split("_")[0],
                "sort": result.name.replace("fold_", "").split("_")[1],
                "project_id": None,
                "target": None,
                "dataset_name": None,
                "role": None
            }
            for image in result.train:
                row["project_id"] = image.project_id
                row["target"] = image.has_tb
                row["role"] = "TRAIN"
                row["dataset_name"] = image.dataset_name
                yield row
            for image in result.test:
                row["project_id"] = image.project_id
                row["target"] = image.has_tb
                row["role"] = "TEST"
                row["dataset_name"] = image.dataset_name
                yield row
            for image in result.validation:
                row["project_id"] = image.project_id
                row["target"] = image.has_tb
                row["role"] = "VAL"
                row["dataset_name"] = image.dataset_name
                yield row

    def get_pandas_dataframe(self):
        return pd.DataFrame([row.copy() for row in self._get_folds_as_json()])

    def download_picke(self, path: str = None) -> str:
        results = list(self.get_folds())
        matrix = [[[] for x in range(9)] for i in range(10)]
        for result in results:
            test = int(result.name.replace("fold_", "").split("_")[0])
            sort = int(result.name.replace("fold_", "").split("_")[1])
            matrix[test][sort] = [
                [train_image.project_id for train_image in result.train],
                [test_image.project_id for test_image in result.test],
                [val_image.project_id for val_image in result.validation]
            ]
        if path is None:
            path = os.path.join(os.getcwd(), "folds.pkl")
        with open(path, mode="wb") as file:
            pickle.dump(matrix, file)
        return path

    def download_csv(self, path: str = None) -> str:
        if path is None:
            path = os.path.join(os.getcwd(), "folds.csv")
        with open(path, mode="w") as file:
            fieldnames = ["fold_name", "test", "sort", "project_id", "target", "dataset_name", "role"]
            writer = DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in self._get_folds_as_json():
                writer.writerow(row)
        return path
