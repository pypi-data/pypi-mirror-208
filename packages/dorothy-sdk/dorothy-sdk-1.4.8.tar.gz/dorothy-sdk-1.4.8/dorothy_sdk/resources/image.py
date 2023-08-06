import os
import tempfile
from requests import Session
from PIL import Image as PILImage
from io import BytesIO

CACHE_LOCATION = os.environ.get('DOROTYSDK_CACHE_LOCATION', os.path.join(tempfile.gettempdir(), "image_service", "images"))
CACHE_ENABLED = os.environ.get('DOROTYSDK_CACHE_ENABLED', 'false').lower() == 'true'


class Image:
    resource = "images"

    def __init__(self, dataset_name: str, image_url: str, project_id: str,
                 insertion_date: str, metadata: dict, date_acquisition: str, number_reports: int,
                 session: Session, host: str, dataset_id: str = None, *args, **kwargs):
        self.dataset_name = dataset_name
        self.image_url = image_url
        self.project_id = project_id
        self.insertion_date = insertion_date
        self.metadata = metadata
        self.date_acquisition = date_acquisition
        self.number_reports = number_reports
        self.dataset_id = dataset_id
        self._session: Session = session
        self._service_host = host
        self.image_object: PILImage = None
        self.image_format = None
        self.download_parameters = None
        self._cache_location = CACHE_LOCATION
        self._cached_image_name = f"{self.dataset_name}_{self.project_id}.{self.image_format}"
        self._cache_enabled = CACHE_ENABLED

    def _check_cache(self) -> [PILImage, None]:
        if self._cache_enabled:
            file_name = f"{self.dataset_name}_{self.project_id}.{self.image_format}"
            image_cached_path = os.path.join(self._cache_location, file_name)
            if not os.path.exists(image_cached_path):
                return None
            return PILImage.open(image_cached_path, formats=self.image_format)
        return None

    def _update_cache(self, image_content: bytes):
        if self._cache_enabled:
            if not os.path.exists(self._cache_location):
                os.makedirs(self._cache_location, exist_ok=True)
            with open(os.path.join(self._cache_location, self._cached_image_name), mode="wb") as file:
                file.write(image_content)
        return None

    def set_cache_location(self, path: str) -> None:
        if self._cache_enabled:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            self._cache_location = path

    def download_image(self, width: int = None, height: int = None, gray_scale: bool = False) -> PILImage:
        cached_image = self._check_cache()
        if not cached_image:
            parameters = {}
            if width:
                parameters["width"] = width
            if height:
                parameters["height"] = height
            parameters["grayscale"] = gray_scale
            self.download_parameters = parameters
            request = self._session.get(self.image_url, params=parameters)
            request.raise_for_status()
            self.image_format = request.headers.get("Content-Type", "image/png").split("/")[-1]
            self._update_cache(request.content)
            if request.status_code == 200:
                buffer = BytesIO()
                buffer.write(request.content)
                buffer.seek(0)
                image_object = PILImage.open(buffer)
                self.image_object = image_object
                return image_object
            else:
                raise RuntimeError("Could not download image")
        return cached_image

    def save(self, image_path: str = None, quality: int = 100) -> None:
        if not self.image_object:
            self.download_image()
        if image_path:
            self.image_object.save(image_path, quality=quality)
            return
        else:
            self.image_object.save(f"{self.dataset_name}_{self.project_id}.{self.image_format}", quality=quality)
            return

    def crop(self, initial_position: tuple, incremental_size: int) -> PILImage:
        image_width, image_height = self.image_object.size
        if incremental_size > image_width or incremental_size > image_height:
            raise ValueError("The crop range exceeds the maximum image size. Reduce 'incremental_size' to solve it")
        final_position = tuple(map(lambda x: x + incremental_size, initial_position))
        box = initial_position + final_position
        return self.image_object.crop(box)

    def flip(self):
        return self.image_object.transpose(PILImage.FLIP_LEFT_RIGHT)

    def scale_width(self, target_size: int, crop_size: int, method=PILImage.BICUBIC) -> PILImage:
        image_width, image_height = self.image_object.size
        if image_width == target_size and image_height >= crop_size:
            return self.image_object
        new_width = target_size
        new_height = int(max(target_size * image_height / image_width, crop_size))
        return self.image_object.resize((new_width, new_height), method)

    def make_power_2(self, base, method=PILImage.BICUBIC) -> PILImage:
        image_width, image_height = self.image_object.size
        new_height = int(round(image_height / base) * base)
        new_width = int(round(image_width / base) * base)

        if new_height == image_height and new_width == image_width:
            return self.image_object

        return self.image_object.resize((new_width, new_height), method)
