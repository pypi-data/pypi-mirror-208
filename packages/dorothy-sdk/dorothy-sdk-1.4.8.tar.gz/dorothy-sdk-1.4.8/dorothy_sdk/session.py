import os
from requests_cache import CachedSession
from datetime import timedelta
from requests.adapters import HTTPAdapter, Retry

DEFAULT_TIMEOUT = 60  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)
        self.max_retries = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
        )

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class SessionManager:
    _token = None
    _token_file = os.path.join(os.getcwd(), "dorotysdk", "credentials.txt")
    _environment_variable_name = "DOROTYSDK_ACCESS_TOKEN"

    def __init__(self, token: str = None, **options):
        super().__init__()
        if not token:
            self._fetch_token(**options)
        else:
            self._token = token

    def build_session(self):
        session = CachedSession(
            'dorothy_sdk',
            use_cache_dir=True,  # Save files in the default user cache dir
            cache_control=True,  # Use Cache-Control headers for expiration, if available
            expire_after=timedelta(hours=6),  # Otherwise expire responses after one day
            allowable_methods=['GET', 'POST'],  # Cache POST requests to avoid sending the same data twice
            allowable_codes=[200, 400],  # Cache 400 responses as a solemn reminder of your failures
            match_headers=True,  # Match all request headers
            stale_if_error=True,  # In case of request errors, use stale cache data if possible
        )
        session.headers.update({"Authorization": f"Token {self._token}"})
        adapter = TimeoutHTTPAdapter()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _fetch_token(self, **options):
        if options.get('path', ''):
            if os.path.exists(options.get('path')):
                self._token_file = options.get('path')
            else:
                FileNotFoundError("Credentials file passed as parameter not found.")

        token = os.environ.get(self._environment_variable_name, '')
        if not token:
            if os.path.exists(self._token_file):
                with open(self._token_file, mode='r', encoding='utf-8') as credentials_file:
                    self._token = credentials_file.read().replace('\n', '').replace('\t', '').replace('\r', '').strip()
            else:
                raise RuntimeError("Access credential not found. The credential can be entered either as a parameter "
                                   "or via a credentials file or environment variable")
        else:
            self._token = token
