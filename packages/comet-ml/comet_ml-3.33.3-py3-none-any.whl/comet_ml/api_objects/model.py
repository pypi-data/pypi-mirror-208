# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at https://www.comet.com
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed
#  without the express permission of Comet ML Inc.
# *******************************************************

import functools
import io
import logging
import pathlib
import zipfile
from typing import List, Union

import comet_ml.config
import comet_ml.exceptions
import comet_ml.utils

from . import setup_client

LOGGER = logging.getLogger(__name__)


class Model:
    """
    Model is an API object implementing various methods to manipulate models in the model registry.
    """

    def __init__(self, workspace: str, model_name: str, *, api_key=None):
        self._workspace = workspace
        self._model_name = model_name
        self._api_key = api_key

    @classmethod
    def from_registry(cls, workspace: str, model_name: str, *, api_key: str = None):
        """
        Obtain a Model object from the model registry.

        Args:
            workspace: the name of the workspace
            model_name: name of the registered model
            api_key: optional. If not specified, api_key will be obtained from the comet configuration or environment variables.
        """
        model = Model(workspace, model_name, api_key=api_key)
        if not Model.__internal_api_compatible_backend__(model._client):
            actual_backend = model._client.get_api_backend_version()
            message = "{} API object only works if backend version is at least {} (actual backend version: {})".format(
                cls.__name__,
                comet_ml.utils.format_version_number(cls.minimal_backend()),
                comet_ml.utils.format_version_number(actual_backend),
            )
            raise comet_ml.exceptions.CometException(message)
        model._load_compact_details()
        return model

    @classmethod
    def minimal_backend(cls):
        config = comet_ml.config.get_config()
        return comet_ml.utils.parse_version_number(
            config["comet.novel_model_registry_api.minimum_backend_version"]
        )

    @property
    @functools.lru_cache()
    def _client(self):
        client = setup_client.setup(api_key=self._api_key, use_cache=False)
        return client

    @classmethod
    @functools.lru_cache()
    def __internal_api_compatible_backend__(cls, client):
        actual_backend = client.get_api_backend_version()
        if actual_backend is None:
            raise comet_ml.exceptions.CometException("could not parse backend version")
        return actual_backend >= cls.minimal_backend()

    def _load_compact_details(self):
        params = {"workspaceName": self._workspace, "modelName": self._model_name}
        data = self._client.get_from_endpoint("registry-model/compact-details", params)
        self._registry_model_id = data["registryModelId"]

    def tags(self, version: str):
        """
        returns the tags for a given version of the model.

        Args:
            version: the model version
        """
        details = self.get_details(version)
        return details["tags"]

    def status(self, version: str):
        """
        returns the status for a given version of the model, e.g. "Production"

        Args:
            version: the model version
        """
        details = self.get_details(version)
        return details["status"]

    def __repr__(self):
        return "Model(%s, %s)" % (repr(self._workspace), repr(self._model_name))

    def delete_tag(self, version: str, tag: str):
        """
        delete a tag from a given version of the model

        Args:
            version: the model version
            tag: the tag to delete
        """
        self._client.delete_registry_model_version_stage(
            self._workspace, self._model_name, version, stage=tag
        )

    def add_tag(self, version: str, tag: str):
        """
        add a tag to a given version of the model

        Args:
            version: the model version
            tag: the tag to add
        """
        self._enforce_type("version", version, str)
        self._enforce_type("tag", tag, str)
        self._client.add_registry_model_version_stage(
            self._workspace, self._model_name, version, stage=tag
        )

    def _enforce_type(self, name, thing, expected_type):
        actual_type = type(thing)
        if actual_type is not expected_type:
            raise TypeError(
                '"{name}" must be of type {expected_type}, not {actual_type}'.format(
                    name=name, expected_type=expected_type, actual_type=actual_type
                )
            )

    def set_status(self, version, status):
        """
        set the status of a given version of the model

        Args:
            version: the model version
            status: one of the allowed status values, e.g. "Production"

        see also: the model_registry_allowed_status_values() on the API class.
        """
        self._enforce_type("status", status, str)
        model_item_id = self.get_details(version)["registryModelItemId"]
        payload = {"status": status, "modelItemId": model_item_id}
        self._client.post_from_endpoint(
            "write/registry-model/item/status", payload=payload
        )

    @property
    def name(self):
        return self._model_name

    def find_versions(self, version_prefix="", status=None, tag=None):
        """
        return a list of versions for the model, sorted in descending order (latest version is first).

        Args:
            version_prefix: optional. If specified, return only those versions that start with version_prefix, e.g. "3" may find "3.2" but not "4.0", and "2.1" will find "2.1.0" and "2.1.1" but not "2.0.0" or "2.2.3".
            status: optional. If specified, return only versions with the given status.
            tag: optional. If specified, return only versions with the given tag.
        """
        response = self._client.get_from_endpoint(
            "registry-model/items",
            params={
                "workspaceName": self._workspace,
                "modelName": self._model_name,
                "tag": tag,
                "status": status,
                "versionPrefix": version_prefix,
            },
        )
        items = response["items"]
        return [item["version"] for item in items]

    def download(
        self, version: str, output_folder: Union[pathlib.Path, str], expand: bool = True
    ) -> None:
        """
        download the files for a given version of the model.

        Args:
            version: the model version
            output_folder: files will be saved in this folder
            expand: if True (the default), model files will be saved to the given folder. If False, a zip file named "{model_name}_{version}.zip" will be saved there instead.
        """
        binary = self._client.get_registry_model_zipfile(
            self._workspace, self._model_name, version, stage=None
        )
        if not binary:
            LOGGER.error(
                "bad binary data received for model {}: {}".format(
                    self._model_name, binary
                )
            )
            return
        self._save_locally(version, output_folder, expand, binary)

    def _save_locally(
        self,
        version: str,
        output_folder: Union[pathlib.Path, str],
        expand: bool,
        binary: bytes,
    ):
        if expand:
            with zipfile.ZipFile(io.BytesIO(binary)) as zip:
                zip.extractall(str(output_folder))

            return
        filename = "{model_name}_{version}.zip".format(
            model_name=self._model_name, version=version
        )
        path = pathlib.Path(output_folder) / filename
        with path.open("wb") as f:
            f.write(binary)

    @classmethod
    def __internal_api__register__(
        cls,
        experiment_id: str,
        model_name,
        version: str,
        workspace: str,
        registry_name: str,
        public: bool,
        description: str,
        comment: str,
        tags: List[str],
        status: str,
        *,
        api_key=None
    ):
        payload = {
            "experimentKey": experiment_id,
            "experimentModelName": model_name,
            "registryModelName": registry_name,
            "registryModelDescription": description,
            "version": version,
            "versionComment": comment,
            "tags": tags,
            "status": status,
            "publicModel": public,
        }
        model = Model(workspace, registry_name, api_key=api_key)
        model._client.post_from_endpoint(
            "write/registry-model/item/create", payload=payload
        )
        return model

    def get_details(self, version: str):
        """
        returns a dict with various details about the given model version.

        The exact details returned may vary by backend version, but they include e.g. experimentKey, comment, createdAt timestamp, updatedAt timestamp.

        Args:
            version: the model version
        """
        params = {
            "workspaceName": self._workspace,
            "modelName": self._model_name,
            "version": version,
        }
        response = self._client.get_from_endpoint(
            "registry-model/item/details", params=params
        )
        return response
