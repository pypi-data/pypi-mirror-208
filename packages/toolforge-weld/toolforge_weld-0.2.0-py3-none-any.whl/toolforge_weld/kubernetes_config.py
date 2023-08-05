import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from toolforge_weld.errors import ToolforgeError


class ToolforgeKubernetesConfigError(ToolforgeError):
    """Base class for exceptions related to the Kubernetes config."""


class KubernetesConfigFileNotFoundException(ToolforgeKubernetesConfigError):
    """Raised when a Kubernetes client is attempted to be created but the configuration file does not exist."""


@dataclass(frozen=True)
class Kubeconfig:
    path: Path
    current_server: str
    client_cert_file: Path
    client_key_file: Path
    current_namespace: str

    @classmethod
    def from_path(cls, path: Path):
        data = yaml.safe_load(path.read_text())
        current_context = _find_cfg_obj(data, "contexts", data["current-context"])
        current_cluster = _find_cfg_obj(data, "clusters", current_context["cluster"])
        current_user = _find_cfg_obj(data, "users", current_context["user"])
        return cls(
            path=path,
            current_server=current_cluster["server"],
            # TODO: handle when the contents of the cert are embedded in the kubeconfig
            client_cert_file=_resolve_file_path(
                path.parent, current_user["client-certificate"]
            ),
            # TODO: handle when the contents of the key are embedded in the kubeconfig
            client_key_file=_resolve_file_path(path.parent, current_user["client-key"]),
            current_namespace=current_context["namespace"],
        )

    @classmethod
    def load(cls, path: Optional[Path] = None):
        """Load the kubeconfig file from the given path or environment and standard locations."""
        if path is None:
            path = locate_config_file()

        if not path.exists():
            raise KubernetesConfigFileNotFoundException(str(path.resolve()))

        return cls.from_path(path=path)


def locate_config_file() -> Path:
    """Attempt to locate the Kubernetes config file for this user.

    Don't use directly, only public for backwards compatibility.
    """
    return Path(os.getenv("KUBECONFIG", "~/.kube/config")).expanduser()


def _find_cfg_obj(config, kind, name):
    """Lookup a named object in a config."""
    for obj in config[kind]:
        if obj["name"] == name:
            return obj[kind[:-1]]
    raise ToolforgeKubernetesConfigError(
        "Key {} not found in {} section of config".format(name, kind)
    )


def _resolve_file_path(base: Path, input: str) -> Path:
    input_path = Path(input).expanduser()
    if input_path.is_absolute():
        return input_path
    return (base / input_path).resolve()
