from typing import List, Iterable
from requests import Session
from dorothy_sdk.utils import url_join
from dorothy_sdk.resources.image import Image
from dorothy_sdk.resources.folders import CrossValidationFolders
from dorothy_sdk.resources.folds import CrossValidationFold


class Dataset:
    resource = "datasets"

    def __init__(self, name: str, image_formats: str, number_images: int, session: Session, host: str, *args, **kwargs):
        self.number_images = number_images
        self.name = name
        self.image_formats = image_formats
        self._session = session
        self._service_host = host

    @property
    def folds(self):
        return CrossValidationFold(datasets=[self.name], session=self._session, host=self._service_host)

    def list_images(self, enable_pagination=False):
        if enable_pagination:
            request = self._session.get(url_join(self._service_host, 'dataset', self.name, 'images'))
            request.raise_for_status()
            if request.status_code == 200:
                response = request.json()
                while response.get("next", None) is not None:
                    for data in response.get("results"):
                        yield Image(session=self._session, host=self._service_host, **data)
                    request = self._session.get(response.get("next"))
                    response = request.json()
                if response.get("next", None) is None and len(response.get("results", [])) > 0:
                    for data in response.get("results"):
                        yield Image(session=self._session, host=self._service_host, **data)
            else:
                raise RuntimeError("Unable to list available images")
        else:
            request = self._session.get(url_join(self._service_host, Image.resource), params={"search": self.name})
            request.raise_for_status()
            if request.status_code == 200:
                for element in request.json():
                    yield Image(session=self._session, host=self._service_host, **element)
            else:
                raise RuntimeError("Unable to list available images")

    def get_image(self, image_id: str) -> Image:
        request = self._session.get(url_join(self._service_host, Image.resource), params={"search": f"{self.name},{image_id}"})
        if request.status_code == 200:
            return Image(session=self._session, host=self._service_host, **request.json())
        elif request.status_code == 404:
            return None
        else:
            raise RuntimeError("Unable to fetch image")

    def get_cross_validation_file(self, download_to: str = None):
        fold = CrossValidationFolders(self._session, host=self._service_host, dataset=self.name)
        return fold.download(download_to)
