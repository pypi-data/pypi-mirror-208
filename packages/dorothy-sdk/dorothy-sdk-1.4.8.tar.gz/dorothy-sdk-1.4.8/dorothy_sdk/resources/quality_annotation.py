from requests import Session
from dorothy_sdk.utils import url_join


class QualityAnnotation:
    resource = "annotation"
    project_id: str = None
    under_penetrated: bool = None
    over_penetrated: bool = None
    costophrenic_cropped: bool = None
    apices_cropped: bool = None
    reliable_radiography: bool = None
    minimum_interpretation_quality: bool = None

    def __init__(self, session: Session, host: str, *args, **kwargs):
        self._session: Session = Session()
        self._session.headers["Authorization"] = session.headers["Authorization"]
        self._service_host = host
        if kwargs.get("project_id"):
            self.project_id = kwargs.get("project_id")
        if kwargs.get("under_penetrated"):
            self.under_penetrated = kwargs.get("under_penetrated")
        if kwargs.get("over_penetrated"):
            self.over_penetrated = kwargs.get("over_penetrated")
        if kwargs.get("costophrenic_cropped"):
            self.costophrenic_cropped = kwargs.get("costophrenic_cropped")
        if kwargs.get("apices_cropped"):
            self.apices_cropped = kwargs.get("apices_cropped")
        if kwargs.get("reliable_radiography"):
            self.reliable_radiography = kwargs.get("reliable_radiography")
        if kwargs.get("minimum_interpretation_quality"):
            self.minimum_interpretation_quality = kwargs.get("minimum_interpretation_quality")

    def get(self, project_id: str = None):
        search_parameter = {}
        if project_id or self.project_id:
            search_parameter.update({"project_id": project_id or self.project_id})
        response = self._session.get(url_join(self._service_host, self.resource), params=search_parameter)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise ValueError("There are no annotations for this project_id")
        else:
            response.raise_for_status()

    def save(self, under_penetrated: bool = None,
             over_penetrated: bool = None,
             costophrenic_cropped: bool = None,
             apices_cropped: bool = None,
             reliable_radiography: bool = None,
             minimum_interpretation_quality: bool = None):
        if not self.project_id:
            raise ValueError("'project_id' is a mandatory key")
        data = {
            'project_id': self.project_id,
            'under_penetrated': self.under_penetrated or under_penetrated,
            'over_penetrated': self.over_penetrated or over_penetrated,
            'costophrenic_cropped': self.costophrenic_cropped or costophrenic_cropped,
            'apices_cropped': self.apices_cropped or apices_cropped,
            'reliable_radiography': self.reliable_radiography or reliable_radiography,
            'minimum_interpretation_quality': self.minimum_interpretation_quality or minimum_interpretation_quality
        }
        data = {key: value for key, value in data.items() if value is not None}
        response = self._session.post(
            url=url_join(self._service_host, self.resource) + '/',
            json=data
        )
        response.raise_for_status()
