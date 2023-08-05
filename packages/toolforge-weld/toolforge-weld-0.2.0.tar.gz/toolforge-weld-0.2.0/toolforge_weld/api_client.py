from typing import Any, Dict

import requests
import urllib3

import toolforge_weld
from toolforge_weld.kubernetes_config import Kubeconfig


class ToolforgeClient:
    """Toolforge API client."""

    def __init__(
        self,
        *,
        server: str,
        kubeconfig: Kubeconfig,
        user_agent: str,
        timeout: int = 10,
    ):
        self.timeout = timeout
        self.server = server
        self.session = requests.Session()

        self.session.cert = (
            str(kubeconfig.client_cert_file),
            str(kubeconfig.client_key_file),
        )

        self.session.verify = False

        # T253412: Disable warnings about unverifed TLS certs when talking to the
        # Kubernetes API endpoint
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.session.headers[
            "User-Agent"
        ] = f"{user_agent} toolforge_weld/{toolforge_weld.__version__} python-requests/{requests.__version__}"

    def make_kwargs(self, url: str, **kwargs) -> Dict[str, Any]:
        """Setup kwargs for a Requests request."""
        kwargs["url"] = "{}/{}".format(self.server, url)

        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

        return kwargs

    def get(self, url, **kwargs) -> Dict[str, Any]:
        """GET request."""
        r = self.session.get(**self.make_kwargs(url, **kwargs))
        r.raise_for_status()
        return r.json()

    def post(self, url, **kwargs) -> int:
        """POST request."""
        r = self.session.post(**self.make_kwargs(url, **kwargs))
        r.raise_for_status()
        return r.status_code

    def put(self, url, **kwargs) -> int:
        """PUT request."""
        r = self.session.put(**self.make_kwargs(url, **kwargs))
        r.raise_for_status()
        return r.status_code

    def delete(self, url, **kwargs) -> int:
        """DELETE request."""
        r = self.session.delete(**self.make_kwargs(url, **kwargs))
        r.raise_for_status()
        return r.status_code
