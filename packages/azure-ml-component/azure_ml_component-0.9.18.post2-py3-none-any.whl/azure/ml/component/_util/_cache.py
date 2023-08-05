# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import re
import json
import time
import shutil
import zipfile
import requests
import subprocess
import tempfile
import hashlib
from io import BytesIO
from threading import Lock
from pathlib import Path
from abc import ABC, abstractmethod
from azureml.core import Datastore
from azure.ml.component._util._loggerfactory import _LoggerFactory
from azure.ml.component._util._utils import _sanitize_folder_name, hash_files_content
from azure.ml.component._version import VERSION
from azure.ml.component._restclients.designer import models
from azureml.exceptions import UserErrorException
from msrest import Deserializer

COMPONENT_CACHE_ENV_VARIABLE = "AZUREML_COMPONENT_ANONYMOUS_COMPONENT_CACHE"
COMPONENT_EXPIRE_ENV_VARIABLE = "AZUREML_COMPONENT_ANONYMOUS_COMPONENT_CACHE_EXPIRE_SECONDS"
_logger = _LoggerFactory.get_logger()


class _CachedItem:

    def __init__(self, item, expired_time_in_seconds=60):
        """CachedItem.

        :param item: The instance of cached object
        :type item: obj
        :param expired_time_in_seconds: expired time in seconds
        :type expired_time_in_seconds: int
        """
        self.item = item
        self.expired_time_in_seconds = expired_time_in_seconds
        self.cache_time = time.time()

    def is_expired(self):
        return time.time() - self.cache_time > self.expired_time_in_seconds


class _GeneralCache:
    """General cache for internal use."""
    _cache_dict = {}

    @classmethod
    def set_item(cls, key, item, expired_time_in_seconds=60):
        cls._cache_dict[key] = _CachedItem(item, expired_time_in_seconds)

    @classmethod
    def get_item(cls, key):
        cached = cls._cache_dict.get(key, None)

        if cached is None:
            return None

        if cached.is_expired():
            del cls._cache_dict[key]
            return None
        else:
            return cached

    @classmethod
    def delete_item(cls, key):
        if key in cls._cache_dict:
            del cls._cache_dict[key]


class DatastoreCache:
    """Datastore cache for internal use."""
    datastore_cache_expires_in_seconds = 3600
    # for None item, we only cache it for 1 minute
    datastore_cache_expires_in_seconds_for_none = 60

    @classmethod
    def _cache_key(cls, workspace, datastore_name):
        return 'datastore_{}_{}'.format(workspace._workspace_id, datastore_name)

    @classmethod
    def set_item(cls, workspace, datastore, datastore_name, expired_time_in_seconds=None):
        cache_key = cls._cache_key(workspace, datastore_name)
        if expired_time_in_seconds is None:
            if datastore is None:
                expired_time_in_seconds = cls.datastore_cache_expires_in_seconds_for_none
            else:
                expired_time_in_seconds = cls.datastore_cache_expires_in_seconds
        _GeneralCache.set_item(cache_key, datastore, expired_time_in_seconds)

    @classmethod
    def get_item(cls, workspace, datastore_name):
        cache_key = cls._cache_key(workspace, datastore_name)
        cached_item = _GeneralCache.get_item(cache_key)
        if cached_item is None:
            try:
                datastore = Datastore(workspace, datastore_name)
            except Exception:
                datastore = None
            cls.set_item(workspace, datastore, datastore_name)
            return datastore
        else:
            return cached_item.item


class ComputeTargetCache:
    """Compute target cache for internal use."""
    compute_cache_expires_in_seconds = 3600
    # for None item, we only cache it for 1 minute
    compute_cache_expires_in_seconds_for_none = 60

    @classmethod
    def _cache_key(cls, workspace, compute_name):
        return 'compute_{}_{}'.format(workspace._workspace_id, compute_name)

    @classmethod
    def set_item(cls, workspace, compute, compute_name, expired_time_in_seconds=None):
        cache_key = cls._cache_key(workspace, compute_name)
        if expired_time_in_seconds is None:
            if compute_name is None:
                expired_time_in_seconds = cls.compute_cache_expires_in_seconds_for_none
            else:
                expired_time_in_seconds = cls.compute_cache_expires_in_seconds
        _GeneralCache.set_item(cache_key, compute, expired_time_in_seconds)

    @classmethod
    def get_item(cls, workspace, compute_name):
        cache_key = cls._cache_key(workspace, compute_name)
        return _GeneralCache.get_item(cache_key)

    @classmethod
    def delete_item(cls, workspace, compute_name):
        cache_key = cls._cache_key(workspace, compute_name)
        _GeneralCache.delete_item(cache_key)

    @classmethod
    def get_cached_item_count(cls, workspace):
        prefix = cls._cache_key(workspace, '')
        return len([key for key in _GeneralCache._cache_dict.keys() if key.startswith(prefix)])


class DiskCache(ABC):
    """
    Base disk cache class represents a disk and file backend cache.
    As a Cache, it supports a familiar Python mapping interface with additional cache
    """
    DEFAULT_DISK_CACHE_DIRECTORY = os.path.join(tempfile.gettempdir(), "azure-ml-component", VERSION)
    # Expired time in seconds
    EXPIRE = None
    # Max cached item in disk
    MAX_LIMIT = None
    _CACHE_ENV_VARIABLE = None
    _EXPIRE_ENV_VARIABLE = None
    _UNSPECIFIED = object()
    _instance_lock = Lock()
    _instance = None
    _cache_in_memory = {}

    def __new__(cls, *args, **kwargs):
        """Singleton creation disk cache"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, cache_directory=None):
        self._cache_directory = cache_directory or self.DEFAULT_DISK_CACHE_DIRECTORY
        Path(self._cache_directory).mkdir(exist_ok=True, parents=True)
        self._remove_expire()

    @property
    def cache_directory(self):
        """Cache directory path."""
        return self._cache_directory

    @property
    def expire(self):
        """Expire time in seconde."""
        if self._EXPIRE_ENV_VARIABLE and self._EXPIRE_ENV_VARIABLE in os.environ:
            expire = os.environ.get(self._EXPIRE_ENV_VARIABLE, None)
            try:
                expire = int(expire)
                return expire
            except Exception:
                _logger.debug("Failed to convert the environment variable {self._EXPIRE_ENV_VARIABLE} to int, {e}.")
                return self.EXPIRE
        else:
            return self.EXPIRE

    @classmethod
    def get_disk_cache(cls, cache_directory=None):
        if not cls._CACHE_ENV_VARIABLE or os.environ.get(cls._CACHE_ENV_VARIABLE, "true").lower() == "true":
            return cls(cache_directory=cache_directory)
        else:
            return None

    def _load_disk_cache(self, key):
        """Load disk cache to memory"""
        if key not in os.listdir(self.cache_directory):
            _logger.debug(f"Cannot find {key} in {self.cache_directory}.")
            return None

        with open(os.path.join(self.cache_directory, key), 'r') as f:
            try:
                self._cache_in_memory[key] = f.read()
                return self._cache_in_memory[key]
            except Exception as e:
                _logger.debug(f"When load the disk cache in {self.cache_directory} failed, {e}")
                return None

    def _dump_disk_cache(self, key, value):
        """Dump disk cache from memory"""
        try:
            with open(os.path.join(self.cache_directory, key), 'w') as f:
                f.write(value)
        except Exception as e:
            _logger.debug(f"Failed dump {key} to the disk cache, {e}")

    @abstractmethod
    def _serialize(self, data):
        """Serialize the object."""

    @abstractmethod
    def _deserialize(self, data):
        """Parse a str to object."""

    def set(self, key, value):
        """Set `key` and `value` item in cache."""
        cache_value = self._serialize(value)
        self._cache_in_memory[key] = cache_value
        self._dump_disk_cache(key, cache_value)
        return value

    def __setitem__(self, key, value):
        """Set corresponding `value` for `key` in disk cache."""
        return self.set(key, value)

    def get(self, key, default=None):
        """Retrieve value from cache. If `key` is missing, return `default`"""
        cache_item = self._cache_in_memory.get(key, None) or self._load_disk_cache(key)
        if cache_item:
            try:
                if self.expire and \
                        time.time() > os.path.getmtime(os.path.join(self.cache_directory, key)) + self.expire:
                    _logger.debug(
                        f"{key} in {self.__class__.__name__} is expired, return the default value {default}.")
                    return default
                _logger.debug(f"Use {key} in the {self.__class__.__name__}.")
                return self._deserialize(cache_item)
            except Exception as e:
                _logger.error(f"Failed using {key} in the {self.__class__.__name__}, {e}")
                self._cache_in_memory.pop(key, None)
                return default
        else:
            return default

    def __getitem__(self, key):
        """Return corresponding value for `key` from cache."""
        value = self.get(key, default=self._UNSPECIFIED)
        if value is self._UNSPECIFIED:
            raise KeyError(key)
        return value

    def _remove_cache_item(self, key):
        try:
            file_path = Path(self.cache_directory, key)
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
        except Exception as e:
            _logger.debug(f"Remove the cache item {key} failed, {e}")

    def _remove_expire(self):
        """Remove expired items from cache."""

        def get_file_modify_time(file_path):
            """Return modify time of file, if file not exist return None."""
            try:
                return os.path.getmtime(file_path)
            except Exception:
                # When file does not exist, os.path.getmtime raise error.
                return None

        if not self.expire and not self.MAX_LIMIT:
            return
        now = time.time()
        removed_cache_item = []
        file_mtime_mapping = {item: get_file_modify_time(os.path.join(self.cache_directory, item))
                              for item in os.listdir(self.cache_directory)}
        file_mtime_mapping = {k: v for k, v in file_mtime_mapping.items() if v is not None}
        ordered_cached_list = dict(sorted(file_mtime_mapping.items(), key=lambda kv: kv[1])).keys()
        if self.MAX_LIMIT and len(ordered_cached_list) > self.MAX_LIMIT:
            removed_cache_item = ordered_cached_list[self.MAX_LIMIT:]
            ordered_cached_list = ordered_cached_list[0: self.MAX_LIMIT]
        if self.expire:
            removed_cache_item.extend(
                [item for item in ordered_cached_list if file_mtime_mapping[item] + self.expire < now])
        for item in removed_cache_item:
            self._remove_cache_item(item)
            self._cache_in_memory.pop(item, None)

    def clean(self):
        """Remove all items from cache."""
        # Remove cache in memory
        self._cache_in_memory = {}
        # Remove cache in disk
        for item in os.listdir(self.cache_directory):
            self._remove_cache_item(item)


class RunsettingParametersDiskCache(DiskCache):
    """Disk cache of runsetting parameters. The expire time of the run settings parameters is 1 day."""
    DEFAULT_DISK_CACHE_DIRECTORY = os.path.join(DiskCache.DEFAULT_DISK_CACHE_DIRECTORY, "runsetting_parameters")
    KEY = "runsetting_parameters"
    EXPIRE = 60 * 60 * 24

    def _serialize(self, data):
        # The type of runsetting_parameters is dict{list[RunSettingParameter]}
        serialized = {}
        for k, v in data.items():
            serialized[k] = []
            for item in v:
                serialized[k].append(item.serialize())
        return json.dumps(serialized)

    def _deserialize(self, data):
        from azure.ml.component._restclients.designer.models._models_py3 import RunSettingParameter

        deserialized = {}
        for k, v in json.loads(data).items():
            deserialized[k] = []
            for item in v:
                deserialized[k].append(RunSettingParameter.deserialize(item))
        return deserialized

    def get(self):
        """Get run setting parameters from disk cache."""
        return super(RunsettingParametersDiskCache, self).get(key=self.KEY, default=None)

    def set(self, value):
        """Set run setting parameters to disk cache."""
        return super(RunsettingParametersDiskCache, self).set(key=self.KEY, value=value)


class RegisteredComponentDiskCache(DiskCache):
    """Disk cache of registered pipeline component dto. The expire time of the component dto is 1 week."""
    DEFAULT_DISK_CACHE_DIRECTORY = os.path.join(DiskCache.DEFAULT_DISK_CACHE_DIRECTORY, "registered_component")
    EXPIRE = 7 * 24 * 60 * 60
    _CACHE_ENV_VARIABLE = COMPONENT_CACHE_ENV_VARIABLE
    _EXPIRE_ENV_VARIABLE = COMPONENT_EXPIRE_ENV_VARIABLE

    @staticmethod
    def _convert_register_params_to_cache_key(register_params):
        return hashlib.sha1(json.dumps(register_params, sort_keys=True).encode("utf-8")).hexdigest()

    def _serialize(self, data):
        return json.dumps(data.serialize())

    def _deserialize(self, data):
        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        deserializer = Deserializer(client_models)
        return deserializer('ModuleDto', json.loads(data))

    def get(self, key, default=None):
        """Get registered component from disk cache."""
        key = self._convert_register_params_to_cache_key(key)
        return super(RegisteredComponentDiskCache, self).get(key=key, default=default)

    def set(self, key, value):
        """Set registered component to disk cache."""
        key = self._convert_register_params_to_cache_key(key)
        return super(RegisteredComponentDiskCache, self).set(key=key, value=value)


class RegisteredPipelineComponentDiskCache(DiskCache):
    """Disk cache of registered component dto. The expire time of the component dto is 1 week."""
    DEFAULT_DISK_CACHE_DIRECTORY = os.path.join(DiskCache.DEFAULT_DISK_CACHE_DIRECTORY,
                                                "registered_pipeline_component")
    EXPIRE = 7 * 24 * 60 * 60
    _CACHE_ENV_VARIABLE = COMPONENT_CACHE_ENV_VARIABLE
    _EXPIRE_ENV_VARIABLE = COMPONENT_EXPIRE_ENV_VARIABLE

    @staticmethod
    def _convert_register_params_to_cache_key(workspace, generate_request):
        cache_key = {
            "subscription_id": workspace._subscription_id,
            "resource_group_name": workspace._resource_group,
            "workspace_name": workspace.name,
            "generate_request": generate_request.serialize()
        }
        return hashlib.sha1(json.dumps(cache_key, sort_keys=True).encode("utf-8")).hexdigest()

    def _serialize(self, data):
        return json.dumps(data.serialize())

    def _deserialize(self, data):
        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        deserializer = Deserializer(client_models)
        return deserializer('ModuleDto', json.loads(data))

    def get(self, workspace, generate_request, default=None):
        """Get registered component from disk cache."""
        key = self._convert_register_params_to_cache_key(workspace, generate_request)
        return super(RegisteredPipelineComponentDiskCache, self).get(key=key, default=default)

    def set(self, workspace, generate_request, value):
        """Set registered component to disk cache."""
        key = self._convert_register_params_to_cache_key(workspace, generate_request)
        return super(RegisteredPipelineComponentDiskCache, self).set(key=key, value=value)


class ArtifactCache(DiskCache):
    """
    Disk cache of azure artifact packages. The key of the cache is path of artifact packages in local, like this
    azure-ml-component/artifacts/{organization}/{project}/{feed}/{package_name}/{version}.
    The value is the files/folders in this cache folder.
    """

    DEFAULT_DISK_CACHE_DIRECTORY = os.path.join(tempfile.gettempdir(), "azure-ml-component", "artifacts")
    POSTFIX_CHECKSUM = "checksum"

    def __init__(self, cache_directory=None):
        super(ArtifactCache, self).__init__(cache_directory=cache_directory)
        # check az extension azure-devops installed
        process = subprocess.Popen("az artifacts --help", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode != 0:
            subprocess.check_call("az extension add --name azure-devops", shell=True)
        self._artifacts_tool_path = None

    @staticmethod
    def _format_organization_name(organization):
        return _sanitize_folder_name(organization.strip("/"))

    @staticmethod
    def get_organization_project_by_git():
        """
        Get organization and project from git remote url.
        For example, the git remote url is
            "https://organization.visualstudio.com/xxx/project_name/_git/repositry_name" or
            "https://dev.azure.com/{organization}/project"

        :return organization_url, project: organization_url, project
        :rtype organization_url, project: str, str
        """
        process = subprocess.Popen("git config --get remote.origin.url", stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, encoding="utf-8", shell=True)
        outs, errs = process.communicate()
        if process.returncode != 0:
            # When organization and project cannot be retrieved from the origin url.
            raise UserErrorException(f'Get the git origin url failed, you must be in a local Git directory, '
                                     f'error message: {errs}')
        origin_url = outs.strip()

        # Organization URL has two format, https://dev.azure.com/{organization} and
        # https://{organization}.visualstudio.com
        # https://docs.microsoft.com/en-us/azure/devops/extend/develop/work-with-urls?view=azure-devops&tabs=http
        if "dev.azure.com" in origin_url:
            regex = r"^https:\/\/\w*@?dev\.azure\.com\/(\w*)\/(\w*)"
            results = re.findall(regex, origin_url)
            if results:
                organization, project = results[0]
                return f"https://dev.azure.com/{organization}", project
        elif "visualstudio.com" in origin_url:
            regex = r"https:\/\/(\w*)\.visualstudio\.com.*\/(\w*)\/_git"
            results = re.findall(regex, origin_url)
            if results:
                organization, project = results[0]
                return f"https://{organization}.visualstudio.com", project

        # When organization and project cannot be retrieved from the origin url.
        raise UserErrorException(f'Cannot get organization and project from git origin url "{origin_url}", '
                                 f'you must be in a local Git directory that has a "remote" referencing a '
                                 f'Azure DevOps or Azure DevOps Server repository.')

    def _deserialize(self, data):
        pass

    def _serialize(self, data):
        pass

    def _redirect_artifacts_tool_path(self, organization):
        """To avoid the transient issue when download artifacts,
        download the artifacts tool and redirect az artifact command to it."""
        from azureml.core.authentication import AzureCliAuthentication

        if not organization:
            organization, _ = self.get_organization_project_by_git()

        organization_pattern = r"https:\/\/(.*)\.visualstudio\.com"
        result = re.findall(pattern=organization_pattern, string=organization)
        if result:
            organization_name = result[0]
        else:
            organization_pattern = r"https:\/\/dev\.azure\.com\/(.*)"
            result = re.findall(pattern=organization_pattern, string=organization)
            if not result:
                raise UserErrorException("Cannot find artifact organization.")
            else:
                organization_name = result[0]

        if not self._artifacts_tool_path:
            os_name = "Windows" if os.name == "nt" else "Linux"
            auth = AzureCliAuthentication()
            header = auth.get_authentication_header()

            url = f"https://{organization_name}.vsblob.visualstudio.com/_apis/clienttools/ArtifactTool/release?" \
                  f"osName={os_name}&arch=AMD64"
            response = requests.get(url, headers=header)
            if response.status_code == 200:
                artifacts_tool_path = tempfile.mktemp()
                artifacts_tool_uri = response.json()["uri"]
                response = requests.get(artifacts_tool_uri)
                with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
                    zip_file.extractall(artifacts_tool_path)
                os.environ["AZURE_DEVOPS_EXT_ARTIFACTTOOL_OVERRIDE_PATH"] = str(artifacts_tool_path.resolve())
                self._artifacts_tool_path = artifacts_tool_path
            else:
                _logger.warning(f"Download artifact tool failed: {response.text}")

    def _download_artifacts(self, download_cmd, organization, name, version, feed, max_retries=3):
        """Download artifacts with retry."""
        retries = 0
        while retries <= max_retries:
            try:
                self._redirect_artifacts_tool_path(organization)
            except Exception as e:
                _logger.warning(f"Redirect artifacts tool path failed, details: {e}")

            retries += 1
            process = subprocess.Popen(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       shell=True, encoding='utf-8')
            outputs, errs = process.communicate()
            if process.returncode != 0:
                error_msg = f"Download package {name}:{version} from the feed {feed} failed {retries} times: {errs}"
                if retries < max_retries:
                    _logger.warning(error_msg)
                else:
                    from azureml.exceptions import AzureMLException

                    error_msg = error_msg + f"\nDownload artifact debug info: {outputs}"
                    raise AzureMLException(error_msg)
            else:
                return

    def _check_artifacts(self, artifact_package_path):
        """
        Check the artifact folder is legal.
        If the artifact folder or checksum file does not exist, return false.
        If the checksum file exists and does not equal to the hash of artifact folder, return False.
        If the checksum file equals to the hash of artifact folder, return true.
        """
        path = Path(artifact_package_path)
        if not path.exists():
            return False
        else:
            checksum_path = path.parent / f"{path.name}_{self.POSTFIX_CHECKSUM}"
            if checksum_path.exists():
                with open(checksum_path, "r") as f:
                    checksum = f.read()
                    file_list = [os.path.join(root, f) for root, _, files in os.walk(path) for f in files]
                    artifact_hash = hash_files_content(file_list)
                    return checksum == artifact_hash
            else:
                return False

    def get(self, feed, name, version, scope, organization=None, project=None, resolve=True):
        """
        Get the catch path of artifact package. Package path like this
        azure-ml-component/artifacts/{organization}/{project}/{feed}/{package_name}/{version}.
        If the path exits, it will return the package path.
        If the path not exist and resolve=True, it will download the artifact package and return package path.
        If the path not exist and resolve=False, it will return None.

        :param feed: Name or ID of the feed.
        :param name: Name of the package.
        :param version: Version of the package.
        :param scope: Scope of the feed: 'project' if the feed was created in a project, and 'organization' otherwise.
        :param organization: Azure DevOps organization URL.
        :param project: Name or ID of the project.
        :param resolve: Whether download package when package does not exist in local.
        :return artifact_package_path: Cache path of the artifact package
        """
        if not all([organization, project]):
            org_val, project_val = self.get_organization_project_by_git()
            organization = organization or org_val
            project = project or project_val
        artifact_package_path = Path(self.DEFAULT_DISK_CACHE_DIRECTORY) / self._format_organization_name(
            organization) / project / feed / name / version
        if self._check_artifacts(artifact_package_path):
            # When the cache folder of artifact package exists, it's sure that the package has been downloaded.
            return artifact_package_path.absolute().resolve()
        else:
            if resolve:
                if artifact_package_path.exists():
                    # Remove invalid artifact package to avoid affecting download artifact.
                    temp_folder = tempfile.mktemp()
                    os.rename(artifact_package_path, temp_folder)
                    shutil.rmtree(temp_folder)
                # Download artifact
                return self.set(feed=feed, name=name, version=version,
                                organization=organization, project=project, scope=scope)
            else:
                return None

    def set(self, feed, name, version, scope, organization=None, project=None):
        """
        Set the artifact package to the cache. The key of the cache is path of artifact packages in local.
        The value is the files/folders in this cache folder. If package path exists, directly return package path.

        :param feed: Name or ID of the feed.
        :param name: Name of the package.
        :param version: Version of the package.
        :param scope: Scope of the feed: 'project' if the feed was created in a project, and 'organization' otherwise.
        :param organization: Azure DevOps organization URL.
        :param project: Name or ID of the project.
        :return artifact_package_path: Cache path of the artifact package
        """
        tempdir = tempfile.mktemp()
        download_cmd = f"az artifacts universal download --feed {feed} --name {name} --version {version} " \
                       f"--scope {scope} --path {tempdir}"
        if organization:
            download_cmd = download_cmd + f" --org {organization}"
        if project:
            download_cmd = download_cmd + f" --project {project}"
        _logger.info(f"Start downloading artifacts {name}:{version} from {feed}.")
        process = subprocess.Popen(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, encoding='utf-8')
        # Avoid deadlock when setting stdout/stderr to PIPE.
        _, errs = process.communicate()
        if process.returncode != 0:
            artifacts_tool_not_find_error_pattern = "No such file or directory: .*artifacttool"
            if re.findall(artifacts_tool_not_find_error_pattern, errs):
                # When download artifacts tool failed retry download artifacts command
                _logger.warning(f"Download package {name}:{version} from the feed {feed} failed: {errs}")
                download_cmd = download_cmd + "--debug"
                self._download_artifacts(download_cmd, organization, name, version, feed)
            else:
                raise UserErrorException(
                    f"Download package {name}:{version} from the feed {feed} failed: {errs}")
        try:
            # Copy artifact package from temp folder to the cache path.
            if not all([organization, project]):
                org_val, project_val = self.get_organization_project_by_git()
                organization = organization or org_val
                project = project or project_val
            artifact_package_path = Path(self.DEFAULT_DISK_CACHE_DIRECTORY) / self._format_organization_name(
                organization) / project / feed / name / version
            artifact_package_path.parent.mkdir(exist_ok=True, parents=True)
            file_list = [os.path.join(root, f) for root, _, files in os.walk(tempdir) for f in files]
            artifact_hash = hash_files_content(file_list)
            os.rename(tempdir, artifact_package_path)
            temp_checksum_file = os.path.join(tempfile.mkdtemp(), f"{version}_{self.POSTFIX_CHECKSUM}")
            with open(temp_checksum_file, "w") as f:
                f.write(artifact_hash)
            os.rename(temp_checksum_file, artifact_package_path.parent / f"{version}_{self.POSTFIX_CHECKSUM}")
        except (FileExistsError, PermissionError, OSError):
            # On Windows, if dst exists a FileExistsError is always raised.
            # On Unix, if dst is a non-empty directory, an OSError is raised.
            # If dst is being used by another process will raise PermissionError.
            # https://docs.python.org/3/library/os.html#os.rename
            pass
        return artifact_package_path.absolute().resolve()
