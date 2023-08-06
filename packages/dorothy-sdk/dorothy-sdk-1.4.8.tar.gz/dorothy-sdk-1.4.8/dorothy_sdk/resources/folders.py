import re
import warnings

from requests import Session

from dorothy_sdk.utils import url_join


class CrossValidationFolders:
    resource = "dataset/cross_validation/"
    dataset: str = None
    cluster_id: str = None
    file_url: str = None

    def __init__(self, session: Session, host: str, **kwargs):
        self._session: Session = session
        self._service_host = host
        if kwargs.get("dataset"):
            self.dataset = kwargs.get("dataset")

    def get(self, cluster_id: str = None, dataset: str = None, file_path: str = None):
        warnings.warn("Deprecated method 'get'", DeprecationWarning)
        return self.download(file_path)

    def download(self, file_path: str = None):
        url = url_join(self._service_host, self.resource, self.dataset)
        if url.endswith("/"):
            url = url[:-1]
        with self._session.get(url, stream=True) as request:
            request.raise_for_status()
            if file_path is None:
                file_path = re.findall("filename=(.+)", request.headers.get("Content-Disposition"))[0]
            with open(file_path, 'wb') as f:
                for chunk in request.iter_content(chunk_size=8192):
                    f.write(chunk)
        return file_path

    def download_file(self, path: str = None):
        warnings.warn("Deprecated method 'download_file'", DeprecationWarning)
        self.download(path)
