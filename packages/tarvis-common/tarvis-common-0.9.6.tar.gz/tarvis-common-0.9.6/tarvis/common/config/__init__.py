from dependency_injector import providers
import logging
import json5
import os
from tarvis.common import environ
from tarvis.common.environ import PlatformType, DeploymentType


class Configuration(providers.Configuration):
    def __init__(self, path: str = ".") -> None:
        super().__init__()
        loaded = self._load_environmental_configs(path)
        if not loaded:
            logging.warning(f"No configuration found")

    def _load_environment_config(
        self,
        path: str,
        platform: PlatformType | None,
        deployment: DeploymentType | None,
    ) -> bool:
        file_name = "config"
        if platform is not None:
            file_name += "-" + PlatformType(platform).name.lower()
        if deployment is not None:
            file_name += "-" + DeploymentType(deployment).name.lower()
        file_name += ".json"
        file_name = os.path.join(path, file_name)
        if os.path.isfile(file_name):
            try:
                with open(file_name, "r") as json_file:
                    self.from_dict(json5.load(json_file))
                return True
            except:
                logging.critical(f'Invalid configuration file "{file_name}"')
                raise
        return False

    def _load_environmental_configs(self, path: str) -> bool:
        loaded = False
        loaded |= self._load_environment_config(path, None, None)
        loaded |= self._load_environment_config(path, environ.platform, None)
        loaded |= self._load_environment_config(path, None, environ.deployment)
        loaded |= self._load_environment_config(
            path, environ.platform, environ.deployment
        )
        return loaded
