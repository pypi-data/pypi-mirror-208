"""Library to initiate backend RIME service requests."""
import atexit
import json
import logging
import re
from collections import Counter
from datetime import date, datetime
from http import HTTPStatus
from inspect import getmembers
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Iterator, List, Optional, Tuple, Union
from uuid import uuid4

import importlib_metadata
import pandas as pd
from urllib3.util import Retry

from rime_sdk.firewall import Firewall
from rime_sdk.image_builder import ImageBuilder
from rime_sdk.internal.config_parser import _get_uuid
from rime_sdk.internal.file_upload import FileUploadModule
from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.internal.security_config_parser import (
    convert_model_info_to_dict,
    model_info_from_dict,
)
from rime_sdk.internal.throttle_queue import ThrottleQueue
from rime_sdk.job import BaseJob, ContinuousTestJob, FileScanJob, ImageBuilderJob, Job
from rime_sdk.project import Project
from rime_sdk.swagger import swagger_client
from rime_sdk.swagger.swagger_client import ApiClient
from rime_sdk.swagger.swagger_client.models import (
    ConfigvalidatorConfigTypeBody,
    ListImagesRequestPipLibraryFilter,
    ManagedImagePackageRequirement,
    ManagedImagePackageType,
    ManagedImagePipRequirement,
    ProjectCreateProjectRequest,
    RimeActorRole,
    RimeCreateImageRequest,
    RimeJobMetadata,
    RimeJobType,
    RimeLicenseLimit,
    RimeLimitStatusStatus,
    RimeListImagesRequest,
    RimeManagedImage,
    RimeManagedImageStatus,
    RimeModelTask,
    RimeParentRoleSubjectRolePair,
    RimeStartFileScanRequest,
    RoleWorkspaceBody,
    RuntimeinfoCustomImage,
    RuntimeinfoCustomImageType,
    RuntimeinfoRunTimeInfo,
    StresstestsProjectIdUuidBody,
)
from rime_sdk.swagger.swagger_client.rest import ApiException
from rime_sdk.test_run import TestRun

logger = logging.getLogger()


VALID_MODEL_TASKS = [
    model_task
    for _, model_task in getmembers(RimeModelTask)
    if isinstance(model_task, str) and "MODEL_TASK_" in model_task
]


class Client:
    """A Client object provides an interface to RIME's \
        services for creating Projects, starting Stress Test Jobs,\
        and querying the backend for current Stress Test Jobs.

    To initialize the Client, provide the address of your RIME instance.


    Args:
        domain: str
            The base domain/address of the RIME service.
        api_key: str
            The API key used to authenticate to RIME services.
        channel_timeout: Optional[float]
            The amount of time in seconds to wait for responses from the cluster.
        disable_tls: Optional[bool]
            A Boolean that enables TLS when set to FALSE. By default, this
            value is set to FALSE.
        ssl_ca_cert: Optional[Union[Path, str]]
            Specifies the path to the certificate file used to verify the peer.
        cert_file: Optional[Union[Path, str]]
            Path to the Client certificate file.
        key_file: Optional[Union[Path, str]]
            Path to the Client key file.
        assert_hostname: Optional[bool]
            Enable/disable SSL hostname verification.

    Raises:
        ValueError
            This error is generated when a connection to the RIME cluster cannot be
            established before the interval specified in `timeout` expires.

    Example:
        .. code-block:: python

            rime_client = Client("my_vpc.rime.com", "api-key")
    """

    # A throttler that limits the number of model tests to roughly 20 every 5 minutes.
    # This is a static variable for Client.
    _throttler = ThrottleQueue(desired_events_per_epoch=20, epoch_duration_sec=300)

    # If the api client receives one of these recoverable status codes, it will retry the request.
    RETRY_HTTP_STATUS = [
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.GATEWAY_TIMEOUT,
    ]

    def __init__(
        self,
        domain: str,
        api_key: str = "",
        channel_timeout: float = 180.0,
        disable_tls: bool = False,
        ssl_ca_cert: Optional[Union[Path, str]] = None,
        cert_file: Optional[Union[Path, str]] = None,
        key_file: Optional[Union[Path, str]] = None,
        assert_hostname: Optional[bool] = None,
    ) -> None:
        """Create a new Client connected to the services available at `domain`."""
        self._domain = domain
        if disable_tls:
            print(
                "WARNING: disabling tls is not recommended."
                " Please ensure you are on a secure connection to your servers."
            )
        self._channel_timeout = channel_timeout
        configuration = swagger_client.Configuration()
        configuration.api_key["rime-api-key"] = api_key
        if domain.endswith("/"):
            domain = domain[:-1]
        configuration.host = domain
        configuration.verify_ssl = not disable_tls
        # Set this to customize the certificate file to verify the peer.
        configuration.ssl_ca_cert = ssl_ca_cert
        # client certificate file
        configuration.cert_file = cert_file
        # client key file
        configuration.key_file = key_file
        # Set this to True/False to enable/disable SSL hostname verification.
        configuration.assert_hostname = assert_hostname
        self._api_client = ApiClient(configuration)
        # Prevent race condition in pool.close() triggered by swagger generated code
        atexit.register(self._api_client.pool.close)
        # Sets the timeout and hardcoded retries parameter for the api client.
        self._api_client.rest_client.pool_manager.connection_pool_kw[
            "timeout"
        ] = channel_timeout
        self._api_client.rest_client.pool_manager.connection_pool_kw["retries"] = Retry(
            total=3, status_forcelist=self.RETRY_HTTP_STATUS
        )
        self.customer_name = self._check_version()
        self._check_expiration()

    def __repr__(self) -> str:
        """Return the string representation of the Client."""
        return f"Client(domain={self._domain})"

    def _check_expiration(self) -> None:
        """Check RIME Expiration Date."""
        api = swagger_client.FeatureFlagApi(self._api_client)
        with RESTErrorHandler():
            feature_flag_response = api.feature_flag_get_limit_status(
                customer_name=self.customer_name, limit=RimeLicenseLimit.EXPIRATION
            )

        # Get Expiration Date
        rime_info_api = swagger_client.RIMEInfoApi(self._api_client)
        with RESTErrorHandler():
            rime_info_response = rime_info_api.r_ime_info_get_rime_info()
        expiration_date = datetime.fromtimestamp(
            rime_info_response.expiration_time.timestamp()
        ).date()

        limit_status = feature_flag_response.limit_status.limit_status
        if limit_status == RimeLimitStatusStatus.WARN:
            print(
                f"Your license expires on {expiration_date}."
                f" Contact the Robust Intelligence team to"
                f" upgrade your license."
            )
        elif limit_status == RimeLimitStatusStatus.ERROR:
            message = (
                "Your license has expired. Contact the Robust "
                "Intelligence team to upgrade your license."
            )
            grace_period_end = datetime.fromtimestamp(
                rime_info_response.grace_period_end_time.seconds
            ).date()
            if date.today() > grace_period_end:
                # if grace period has ended throw an error
                raise ValueError(message)
            else:
                print(message)
        elif limit_status == RimeLimitStatusStatus.OK:
            pass
        else:
            raise ValueError(f"Unexpected status value: '{limit_status}'")

    def _check_stress_test_limit(self) -> None:
        """Check if creating another Stress Test would be within license limits.

        Raises:
            ValueError
                This error is generated when a Stress Test cannot be created as
                it would exceed license limits.
        """
        api = swagger_client.FeatureFlagApi(self._api_client)
        with RESTErrorHandler():
            feature_flag_response = api.feature_flag_get_limit_status(
                customer_name=self.customer_name,
                limit=RimeLicenseLimit.STRESS_TEST_RUNS,
            )

        limit_status = feature_flag_response.limit_status.limit_status
        limit_value = feature_flag_response.limit_status.limit_value
        if limit_status == RimeLimitStatusStatus.WARN:
            curr_value = int(feature_flag_response.limit_status.current_value)
            print(
                f"You are approaching the limit ({curr_value + 1}"
                f"/{limit_value}) of Stress Test runs. Contact the"
                f" Robust Intelligence team to upgrade your license."
            )
        elif limit_status == RimeLimitStatusStatus.ERROR:
            # could be either within grace period or exceeded grace period
            # if the latter, let the create Stress Test call raise the
            # error
            print(
                "You have reached the limit of Stress Test runs."
                " Contact the Robust Intelligence team to"
                " upgrade your license."
            )
        elif limit_status == RimeLimitStatusStatus.OK:
            pass
        else:
            raise ValueError(f"Unexpected status value: '{limit_status}'")

    def _check_version(self) -> str:
        """Check current RIME version and return client name."""
        api = swagger_client.RIMEInfoApi(self._api_client)
        with RESTErrorHandler():
            rime_info_response = api.r_ime_info_get_rime_info()
        server_version = rime_info_response.cluster_info_version
        client_version = importlib_metadata.version("rime_sdk")
        if client_version != server_version:
            logger.warning(
                "Python SDK package and server are on different versions. "
                f"The Python SDK package is on version {client_version}, "
                f"while the server is on version {server_version}. "
                f"In order to make them be on the same version, please "
                f"install the correct version of the Python SDK package with "
                f"`pip install rime_sdk=={server_version}`"
            )
        return rime_info_response.customer_name

    def __str__(self) -> str:
        """Pretty-print the object."""
        return f"RIME Client [{self._domain}]"

    # TODO(QuantumWombat): do this check server-side
    def _project_exists(self, project_id: str) -> bool:
        """Check if `project_id` exists.

        Args:
            project_id: the id of the Project to be checked.

        Returns:
            bool:
                Whether project_id is a valid Project.

        Raises:
            ValueError
                This error is generated when the request to the Project service
                fails.
        """
        api = swagger_client.ProjectServiceApi(self._api_client)
        try:
            api.project_service_get_project(project_id)
            return True
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return False
            raise ValueError(e.reason)

    def create_project(
        self,
        name: str,
        description: str,
        model_task: str,
        use_case: Optional[str] = None,
        ethical_consideration: Optional[str] = None,
        profiling_config: Optional[dict] = None,
        general_access_role: Optional[str] = "ACTOR_ROLE_NONE",
    ) -> Project:
        """Create a new RIME Project.

        Projects enable you to organize Stress Test runs.
        A natural way to organize Stress Test runs is to create a Project for each
        specific ML task, such as predicting whether a transaction is fraudulent.

        Args:
            name: str
                Name of the new Project.
            description: str
                Description of the new Project.
            model_task: str
                Machine Learning task associated with the Project. Must be one of
                "MODEL_TASK_REGRESSION", "MODEL_TASK_BINARY_CLASSIFICATION",
                "MODEL_TASK_MULTICLASS_CLASSIFICATION",
                "MODEL_TASK_NAMED_ENTITY_RECOGNITION", "MODEL_TASK_RANKING",
                "MODEL_TASK_OBJECT_DETECTION", "MODEL_TASK_NATURAL_LANGUAGE_INFERENCE",
                "MODEL_TASK_FILL_MASK".
            use_case: Optional[str]
                Description of the use case of the Project.
            ethical_consideration: Optional[str]
                Description of ethical considerations for this Project.
            profiling_config: Optional[dict]
                Configuration for the data and model profiling across all test
                runs.
            general_access_role: Optional[str],
                Project roles assigned to the workspace members.
                Allowed Values: ACTOR_ROLE_USER, ACTOR_ROLE_VIEWER, ACTOR_ROLE_NONE.

        Returns:
            Project:

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.

        Example:
            .. code-block:: python

               project = rime_client.create_project(
                   name="foo", description="bar", model_task="Binary Classification"
               )
        """
        api = swagger_client.ProjectServiceApi(self._api_client)

        valid_general_access_roles = [
            "ACTOR_ROLE_USER",
            "ACTOR_ROLE_VIEWER",
            "ACTOR_ROLE_NONE",
        ]
        if general_access_role not in valid_general_access_roles:
            raise ValueError(
                f"Invalid general access role: '{general_access_role}'. "
                f"Expected one of: {valid_general_access_roles}"
            )
        if model_task not in VALID_MODEL_TASKS:
            raise ValueError(
                f"Invalid model task: '{model_task}'. "
                f"Expected one of: {VALID_MODEL_TASKS}"
            )
        with RESTErrorHandler():
            if profiling_config:
                with RESTErrorHandler():
                    cv_api = swagger_client.ConfigValidatorApi(self._api_client)
                    validate_body = ConfigvalidatorConfigTypeBody(
                        config_json=json.dumps(profiling_config),
                    )
                    cv_api.config_validator_validate_test_config(
                        config_type="CONFIG_TYPE_PROFILING", body=validate_body
                    )
            body = ProjectCreateProjectRequest(
                name=name,
                description=description,
                model_task=model_task,
                use_case=use_case,
                ethical_consideration=ethical_consideration,
                profiling_config=profiling_config,
            )
            response = api.project_service_create_project(body=body)

            if general_access_role != "ACTOR_ROLE_NONE":
                role_pairs = [
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.ADMIN,
                        subject_role=general_access_role,
                    ),
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.VP, subject_role=general_access_role,
                    ),
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.USER,
                        subject_role=general_access_role,
                    ),
                    # Workspace viewers can receive only a viewer role through
                    # general access as per the RBAC spec.
                    RimeParentRoleSubjectRolePair(
                        parent_role=RimeActorRole.VIEWER,
                        subject_role=RimeActorRole.VIEWER,
                    ),
                ]
                workspace_role_body = RoleWorkspaceBody(role_pairs=role_pairs)
                api.project_service_update_workspace_roles_for_project(
                    project_id_uuid=response.project.id.uuid, body=workspace_role_body,
                )
            return Project(self._api_client, response.project.id.uuid)

    def get_project(self, project_id: str) -> Project:
        """Get Project by ID.

        Args:
            project_id: str
                ID of the Project to return.

        Returns:
            Project:

        Example:
            .. code-block:: python

               project = rime_client.get_project("123-456-789")
        """
        api = swagger_client.ProjectServiceApi(self._api_client)
        try:
            response = api.project_service_get_project(project_id)
            return Project(self._api_client, response.project.project.id.uuid)
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"Project with this id {project_id} does not exist")
            raise ValueError(e.reason)

    def delete_project(self, project_id: str, force: Optional[bool] = False) -> None:
        """Delete a Project by ID.

        Args:
            project_id: str
                ID of the Project to delete.
            force: Optional[bool] = False
                When set to True, the Project will be deleted immediately. By default,
                a confirmation is required.

        Example:
            .. code-block:: python

               project = rime_client.delete_project("123-456-789", True)
        """
        project = self.get_project(project_id)
        project.delete(force=force)

    def create_managed_image(
        self,
        name: str,
        requirements: List[ManagedImagePipRequirement],
        package_requirements: Optional[List[ManagedImagePackageRequirement]] = None,
        python_version: Optional[str] = None,
    ) -> ImageBuilder:
        """Create a new managed Docker image with the desired\
        custom requirements to run RIME on.

        These managed Docker images are managed by the RIME cluster and
        automatically upgrade when the installed version of RIME upgrades.
        Note: Images take a few minutes to be built.

        This method returns an object that can be used to track the progress of the
        image building job. The new custom image is only available for use in a stress
        test once it has status ``READY``.

        Args:
            name: str
                The name of the new Managed Image. This name serves as the unique
                identifier of the Managed Image. The call fails when an image with
                the specified name already exists.
            requirements: List[ManagedImagePipRequirement]
                List of additional pip requirements to be installed on the managed
                image. A ``ManagedImagePipRequirement`` can be created with the helper
                method ``Client.pip_requirement``.
                The first argument is the name of the library (e.g. ``tensorflow`` or
                ``xgboost``) and the second argument is a valid pip
                `version specifier <https://www.python.org/dev/peps/pep-0440/#version-specifiers>`
                (e.g. ``>=0.1.2`` or ``==1.0.2``) or an exact
                `version<https://peps.python.org/pep-0440/>`, such as ``1.1.2``,
                for the library.
            package_requirements: Optional[List[ManagedImagePackageRequirement]]
                [BETA] An optional List of additional operating system package
                requirements to install on the Managed Image. Currently only
                `Rocky Linux` package requirements are supported.
                Create a ``ManagedImagePackageRequirement`` parameter with
                the ``Client.os_requirement`` helper method.
                The first argument is the name of the package (e.g. ``texlive`` or
                ``vim``) and the second optional argument is a valid yum
                `version specifier` (e.g. ``0.1.2``) for the package.
            python_version: Optional[str]
                An optional version string specifying only the major and minor version
                for the python interpreter used. The string should be of the format
                X.Y and be present in the set of supported versions.

        Returns:
            ImageBuilder:
                A ``ImageBuilder`` object that provides an interface for monitoring
                the job in the backend.

        Raises:
            ValueError
                This error is generated when the request to the ImageRegistry
                service fails.

        Example:
            .. code-block:: python

               reqs = [
                    # Fix the version of `xgboost` to `1.0.2`.
                    rime_client.pip_requirement("xgboost", "==1.0.2"),
                    # We do not care about the installed version of `tensorflow`.
                    rime_client.pip_requirement("tensorflow")
                ]

               # Start a new image building job
               builder_job = rime_client.create_managed_image("xgboost102_tf", reqs)

               # Wait until the job has finished and print out status information.
               # Once this prints out the `READY` status, your image is available for
               # use in Stress Tests.
               builder_job.get_status(verbose=True, wait_until_finish=True)
        """

        if isinstance(package_requirements, ManagedImagePackageRequirement):
            package_requirements = list(package_requirements)

        req = RimeCreateImageRequest(
            name=name,
            pip_requirements=requirements,
            package_requirements=package_requirements,
        )

        if python_version is not None:
            req.python_version = python_version

        api = swagger_client.ImageRegistryApi(self._api_client)
        with RESTErrorHandler():
            image: RimeManagedImage = api.image_registry_create_image(body=req).image
        return ImageBuilder(
            self._api_client,
            image.name,
            requirements,
            package_requirements,
            python_version,
        )

    def has_managed_image(self, name: str, check_status: bool = False) -> bool:
        """Check whether a Managed Image with the specified name exists.

        Args:
            name: str
                The unique name of the Managed Image to check. The call returns
                False when no image with the specified name exists.
            check_status: bool
                Flag that determines whether to check the image status. When
                this flag is set to True, the call returns True if and only if the image
                with the specified name exists AND the image is ready to be used.

        Returns:
            bool:
                Specifies whether a Managed Image with this name exists.

        Example:
            .. code-block:: python

               if rime_client.has_managed_image("xgboost102_tensorflow"):
                    print("Image exists.")
        """
        api = swagger_client.ImageRegistryApi(self._api_client)
        try:
            res = api.image_registry_get_image(name=name)
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                return False
            else:
                raise ValueError(e.reason) from None
        if check_status:
            return res.image.status == RimeManagedImageStatus.READY
        return True

    def get_managed_image(self, name: str) -> Dict:
        """Get Managed Image by name.

        Args:
            name: str
                The unique name of the new Managed Image. The call raises
                an error when no image exists with this name.

        Returns:
            Dict:
                A dictionary with information about the Managed Image.

        Example:
            .. code-block:: python

               image = rime_client.get_managed_image("xgboost102_tensorflow")
        """
        api = swagger_client.ImageRegistryApi(self._api_client)
        with RESTErrorHandler():
            res = api.image_registry_get_image(name=name)
        return res.image.to_dict()

    def delete_managed_image(self, name: str) -> None:
        """Delete a managed Docker image.

        Args:
            name: str
                The unique name of the Managed Image.

        Example:
            .. code-block:: python

               image = rime_client.delete_managed_image("xgboost102_tensorflow")
        """
        api = swagger_client.ImageRegistryApi(self._api_client)
        try:
            api.image_registry_delete_image(name=name)
            print(f"Managed Image {name} successfully deleted")
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"Docker image with name {name} does not exist.")
            raise ValueError(e.reason) from None

    @staticmethod
    def pip_requirement(
        name: str, version_specifier: Optional[str] = None,
    ) -> ManagedImagePipRequirement:
        """Construct a PipRequirement object for use in ``create_managed_image()``."""
        if not isinstance(name, str) or (
            version_specifier is not None and not isinstance(version_specifier, str)
        ):
            raise ValueError(
                (
                    "Proper specification of a pip requirement has the name"
                    "of the library as the first argument and the version specifier"
                    "string as the second argument"
                    '(e.g. `pip_requirement("tensorflow", "==0.15.0")` or'
                    '`pip_requirement("xgboost")`)'
                )
            )
        res = ManagedImagePipRequirement(name=name)
        if version_specifier is not None:
            res.version_specifier = version_specifier
        return res

    @staticmethod
    def os_requirement(
        name: str, version_specifier: Optional[str] = None,
    ) -> ManagedImagePackageRequirement:
        """Construct a PackageRequirement object for ``create_managed_image()``."""
        if (
            not isinstance(name, str)
            or (
                version_specifier is not None and not isinstance(version_specifier, str)
            )
            or (
                version_specifier is not None and not re.match(r"\d", version_specifier)
            )
        ):
            raise ValueError(
                (
                    "Proper specification of a package requirement has the name"
                    "of the library as the first argument and optionally the version"
                    "specifier string as the second argument"
                    '(e.g. `os_requirement("texlive", "20200406")` or'
                    '`os_requirement("texlive")`)'
                )
            )
        res = ManagedImagePackageRequirement(
            name=name, package_type=ManagedImagePackageType.ROCKYLINUX
        )
        if version_specifier is not None:
            res.version_specifier = version_specifier
        return res

    @staticmethod
    def pip_library_filter(
        name: str, fixed_version: Optional[str] = None,
    ) -> ListImagesRequestPipLibraryFilter:
        """Construct a PipLibraryFilter object for use in ``list_managed_images()``."""
        if not isinstance(name, str) or (
            fixed_version is not None and not isinstance(fixed_version, str)
        ):
            raise ValueError(
                (
                    "Proper specification of a pip library filter has the name"
                    "of the library as the first argument and the semantic version"
                    "string as the second argument"
                    '(e.g. `pip_library_filter("tensorflow", "1.15.0")` or'
                    '`pip_library_filter("xgboost")`)'
                )
            )
        res = ListImagesRequestPipLibraryFilter(name=name)
        if fixed_version is not None:
            res.version = fixed_version
        return res

    def list_managed_images(
        self,
        pip_library_filters: Optional[List[ListImagesRequestPipLibraryFilter]] = None,
    ) -> Iterator[Dict]:
        """List all managed Docker images.

        Enables searching for images with specific pip libraries installed so that users
        can reuse Managed Images for Stress Tests.

        Args:
            pip_library_filters: Optional[List[ListImagesRequestPipLibraryFilter]]
                Optional list of pip libraries to filter by.
                Construct each ListImagesRequest.PipLibraryFilter object with the
                ``pip_library_filter`` convenience method.

        Returns:
            Iterator[Dict]:
                An iterator of dictionaries, each dictionary represents
                a single Managed Image.

        Raises:
            ValueError
                This error is generated when the request to the ImageRegistry
                service fails or the list of pip library filters is improperly
                specified.

        Example:
            .. code-block:: python

                # Filter for an image with catboost1.0.3 and tensorflow installed.
                filters = [
                    rime_client.pip_library_filter("catboost", "1.0.3"),
                    rime_client.pip_library_filter("tensorflow"),
                ]

                # Query for the images.
                images = rime_client.list_managed_images(
                    pip_library_filters=filters)

                # To get the names of the returned images.
                [image["name"] for image in images]
        """
        if pip_library_filters is None:
            pip_library_filters = []

        if pip_library_filters is not None:
            for pip_library_filter in pip_library_filters:
                if not isinstance(
                    pip_library_filter, ListImagesRequestPipLibraryFilter
                ):
                    raise ValueError(
                        f"pip library filter `{pip_library_filter}` is not of the "
                        f"correct type, should be of type "
                        f"ListImagesRequest.PipLibraryFilter. Please use "
                        f"rime_client.pip_library_filter to create these filters."
                    )

        # Iterate through the pages of images and break at the last page.
        api = swagger_client.ImageRegistryApi(self._api_client)
        page_token = ""
        while True:
            if page_token == "":
                body = RimeListImagesRequest(
                    pip_libraries=pip_library_filters, page_size=20,
                )
            else:
                body = RimeListImagesRequest(page_token=page_token, page_size=20)
            with RESTErrorHandler():
                # This function hits the additional REST binding on the RPC endpoint.
                # The method sends a POST request instead of a GET since it is
                # the only way to encode multiple custom messages (pip_libraries).
                res = api.image_registry_list_images2(body=body)
                for image in res.images:
                    yield image.to_dict()

            # If we've reached the last page token
            if page_token == res.next_page_token:
                break

            # Move to the next page
            page_token = res.next_page_token

    def list_agents(self,) -> Iterator[Dict]:
        """List all Agents available to the user.

        Returns:
            Iterator[Dict]:
                An iterator of dictionaries, each dictionary represents a single Agent.

        Raises:
            ValueError
                This error is generated when the request to the AgentManager
                service fails.

        Example:
            .. code-block:: python

                # Query for the images.
                agents = rime_client.list_agents()

                # To get the names of the returned Agents.
                [agent["name"] for agent in agents]
        """
        # Iterate through the pages of images and break at the last page.
        page_token = None
        api = swagger_client.AgentManagerApi(self._api_client)
        while True:
            with RESTErrorHandler():
                if page_token is None:
                    res = api.agent_manager_list_agents(
                        first_page_query_agent_status_types=[],
                        first_page_query_agent_ids=[],
                        page_size=100,
                    )
                else:
                    res = api.agent_manager_list_agents(
                        page_token=page_token, page_size=100
                    )
            for agent in res.agents:
                yield agent.to_dict()

            # If we've reached the last page token
            if not res.has_more:
                break

            # Move to the next page
            page_token = res.next_page_token

    def list_projects(self,) -> Iterator[Project]:
        """List all Projects.

        Returns:
            Iterator[Project]:
                An iterator of Projects.

        Raises:
            ValueError
                This error is generated when the request to the Project service fails.

        Example:
            .. code-block:: python

                # Query for projects.
                projects = rime_client.list_projects()

        """
        # Iterate through the pages of Test Cases and break at the last page.
        page_token = ""
        api = swagger_client.ProjectServiceApi(self._api_client)
        while True:
            with RESTErrorHandler():
                res = api.project_service_list_projects(page_token=page_token)
            for project in res.projects:
                yield Project(self._api_client, project.project.id.uuid)
            # we've reached the last page of Test Cases.
            if not res.has_more:
                break
            # Advance to the next page of Test Cases.
            page_token = res.next_page_token

    def start_stress_test(
        self, test_run_config: dict, project_id: str, **exp_fields: Dict[str, object]
    ) -> Job:
        """Start a Stress Testing run.

        Args:
            test_run_config: dict
                Configuration for the test to be run, which specifies unique ids to
                locate the model and datasets to be used for the test.
            project_id: str
                Identifier for the Project where the resulting test run will be stored.
                When not specified, stores the results in the default Project.
            exp_fields: Dict[str, object]
                [BETA] Fields for experimental features.

        Returns:
            Job:
                A Job that provides information about the model Stress Test job.

        Raises:
            ValueError
                This error is generated when the request to the ModelTesting
                service fails.

        Example:
            This example assumes that reference and evaluation datasets are registered
            with identifiers "foo" and "bar" respectively, and that a model with the
            unique identifier `model_uuid` is registered.

        .. code-block:: python

            config = {
                "data_info": {"ref_dataset_id": "foo", "eval_dataset_id": "bar"},
                "model_id": model_uuid,
                "run_name": "My Stress Test Run",
                "model_task": "Binary Classification",
            }

        Run the job using the specified configuration and the default Docker image in
        the RIME backend. Store the results in the RIME Project associated with this
        object.

        .. code-block:: python

           job = rime_client.start_stress_test_job(
              test_run_config=config, project_id="123-456-789"
           )
        """
        self._check_stress_test_limit()
        # TODO(blaine): Add config validation service.
        if not isinstance(test_run_config, dict):
            raise ValueError("The configuration must be a dictionary")
        # TODO (VAL-316): do proper runtime validation of all of the types in the config
        if project_id and not self._project_exists(project_id):
            raise ValueError("Project id {} does not exist".format(project_id))
        if "model_id" in test_run_config:
            if isinstance(test_run_config["model_id"], str):
                test_run_config["model_id"] = _get_uuid(test_run_config["model_id"])
        if "run_time_info" in test_run_config:
            if "agent_id" in test_run_config["run_time_info"]:
                if isinstance(test_run_config["run_time_info"]["agent_id"], str):
                    test_run_config["run_time_info"]["agent_id"] = _get_uuid(
                        test_run_config["run_time_info"]["agent_id"]
                    )
        if (
            "test_suite_config" in test_run_config
            and "custom_tests" in test_run_config["test_suite_config"]
        ):
            if not isinstance(
                test_run_config["test_suite_config"]["custom_tests"], list
            ):
                raise ValueError("The custom_tests configuration must be a list")
            test_run_config["test_suite_config"]["custom_tests"] = [
                json.dumps(test) if isinstance(test, dict) else test
                for test in test_run_config["test_suite_config"]["custom_tests"]
            ]

        cv_api = swagger_client.ConfigValidatorApi(self._api_client)
        with RESTErrorHandler():
            validate_body = ConfigvalidatorConfigTypeBody(
                config_json=json.dumps(test_run_config),
            )
            cv_api.config_validator_validate_test_config(
                config_type="CONFIG_TYPE_TEST_RUN", body=validate_body
            )
            req = StresstestsProjectIdUuidBody(
                test_run_config=test_run_config,
                experimental_fields=exp_fields if exp_fields else None,
            )
            Client._throttler.throttle(
                throttling_msg="Your request is throttled to limit # of model tests."
            )
            api = swagger_client.ModelTestingApi(self._api_client)
            job: RimeJobMetadata = api.model_testing_start_stress_test(
                body=req, project_id_uuid=project_id,
            ).job
        return Job(self._api_client, job.job_id)

    def get_test_run(self, test_run_id: str) -> TestRun:
        """Get a TestRun object with the specified test_run_id.

        Checks to see if the test_run_id exists, then returns TestRun object.

        Args:
            test_run_id: str
                ID of the test run to query for

        Returns:
            TestRun:
                A TestRun object corresponding to the test_run_id
        """
        try:
            api = swagger_client.ResultsReaderApi(self._api_client)
            api.results_reader_get_test_run(test_run_id=test_run_id)
            return TestRun(self._api_client, test_run_id)
        except ApiException as e:
            if e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"test run id {test_run_id} does not exist")
            raise ValueError(e.reason) from None

    def get_firewall_for_project(self, project_id: str) -> Firewall:
        """Get the active fw for a Project if it exists.

        Query the backend for an active `Firewall` in a specified Project which
        can be used to perform Firewall operations. If there is no active
        Firewall for the Project, this call will error.

        Args:
            project_id: ID of the Project which contains a Firewall.

        Returns:
            Firewall:
                A ``Firewall`` object.

        Raises:
            ValueError
                This error is generated when the Firewall does not exist or when
                the request to the Project service fails.

        Example:
            .. code-block:: python

                # Get FW in foo-project if it exists.
                firewall = rime_client.get_firewall_for_project("foo-project")
        """
        project = self.get_project(project_id)
        return project.get_firewall()

    def upload_file(
        self, file_path: Union[Path, str], upload_path: Optional[str] = None
    ) -> str:
        """Upload a file to make it accessible to the RIME cluster.

        The uploaded file is stored in the RIME cluster in a blob store
        using its file name.

        Args:
            file_path: Union[Path, str]
                Path to the file to be uploaded to RIME's blob store.
            upload_path: Optional[str] = None
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            str:
                A reference to the uploaded file's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the file.

        Raises:
            FileNotFoundError
                When the path ``file_path`` does not exist.
            IOError
                When ``file_path`` is not a file.
            ValueError
                When the specified upload_path is an empty string or there was an
                error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
                When the file upload fails, the incomplete file is
                NOT automatically deleted.

        Example:
             .. code-block:: python

                # Upload the file at location data_path.
                client.upload_file(data_path)
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.upload_dataset_file(file_path, upload_path)

    def upload_local_image_dataset_file(
        self,
        file_path: Union[Path, str],
        image_features: List[str],
        upload_path: Optional[str] = None,
    ) -> Tuple[List[Dict], str]:
        """Upload an image dataset file where image files are stored locally.

        The image dataset file is expected to be a list of JSON dictionaries,
        with an image_features that reference an image (either an absolute path
        or a relative path to an image file stored locally).
        Every image within the file is also uploaded to blob store,
        and the final file is also uploaded.
        If your image paths already reference an external blob storage,
        then use `upload_file` instead to upload the dataset file.

        Args:
            file_path: Union[Path, str]
                Path to the file to be uploaded to RIME's blob store.
            image_features: List[str]
                Keys to image file paths.
            upload_path: Optional[str]
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            Tuple[List[Dict], str]:
                The list of dicts contains the updated
                dataset file with image paths replaced by s3 paths. The string contains
                a reference to the uploaded file's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the file.

        Raises:
            FileNotFoundError
                When the path ``file_path`` does not exist.
            IOError
                When ``file_path`` is not a file.
            ValueError
                When there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
                In the scenario the file fails to upload, the incomplete file will
                NOT automatically be deleted.
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with open(file_path, "r") as fp:
            data_dicts = json.load(fp)
            is_list = isinstance(data_dicts, list)
            is_all_dict = all(isinstance(d, dict) for d in data_dicts)
            if not is_list or not is_all_dict:
                raise ValueError(
                    "Loaded image dataset file must be a list of dictionaries."
                )
        null_counter: Counter = Counter()
        # first check if image path exists
        for data_dict in data_dicts:
            for key in image_features:
                if data_dict.get(key) is None:
                    null_counter[key] += 1
                    continue
                image_path = Path(data_dict[key])
                if not image_path.is_absolute():
                    image_path = file_path.parent / image_path
                if not image_path.exists():
                    raise ValueError(f"Image path does not exist: {image_path}")
                data_dict[key] = image_path

        for key, num_nulls in null_counter.items():
            logger.warning(f"Found {num_nulls} null paths for feature {key}.")

        # then upload paths, replace dict
        for data_dict in data_dicts:
            for key in image_features:
                if data_dict.get(key) is None:
                    continue
                uploaded_image_path = self.upload_file(
                    data_dict[key], upload_path=upload_path
                )
                data_dict[key] = uploaded_image_path

        # save dictionary with s3 paths to a new temporary file, upload file to S3
        with TemporaryDirectory() as temp_dir:
            # save file to a temporary directory
            temp_path = Path(temp_dir) / file_path.name
            with open(temp_path, "w") as fp:
                json.dump(data_dicts, fp)
            return (
                data_dicts,
                self.upload_file(temp_path, upload_path=upload_path),
            )

    def upload_data_frame(
        self,
        data_frame: pd.DataFrame,
        name: Optional[str] = None,
        upload_path: Optional[str] = None,
    ) -> str:
        """Upload a pandas DataFrame to make it accessible to the RIME cluster.

        The uploaded file is stored in the RIME cluster in a blob store
        using its file name.

        Args:
            data_frame: pd.DataFrame
                Path to the file to be uploaded to RIME's blob store.
            name: Optional[str] = None
                Name of the file in the blob store file system. If omitted,
                a unique random string will be assigned as the file name.
            upload_path: Optional[str] = None
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            str:
                A reference to the uploaded file's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the file.

        Raises:
            ValueError
                When the specified upload_path is an empty string or there was an
                error in obtaining a blobstore location from the
                RIME backend or in uploading ``file_path`` to RIME's blob store.
                When the file upload fails, the incomplete file is
                NOT automatically deleted.

        Example:
             .. code-block:: python

                # Upload pandas data frame.
                client.upload_data_frame(df)
        """
        with TemporaryDirectory() as temp_dir:
            name = name or f"{uuid4()}-data"
            temp_path = Path(temp_dir) / f"{name}.parquet"
            data_frame.to_parquet(temp_path, index=False)
            return self.upload_file(temp_path, upload_path=upload_path)

    def upload_directory(
        self,
        dir_path: Union[Path, str],
        upload_hidden: bool = False,
        upload_path: Optional[str] = None,
    ) -> str:
        """Upload a model directory to make it accessible to the RIME cluster.

        The uploaded directory is stored in the RIME cluster in a blob store.
        All files contained within ``dir_path`` and its subdirectories are uploaded
        according to their relative paths within ``dir_path``. When
        `upload_hidden` is set to False, all hidden files and subdirectories
        that begin with a '.' are not uploaded.

        Args:
            dir_path: Union[Path, str]
                Path to the directory to be uploaded to RIME's blob store.
            upload_hidden: bool = False
                Whether to upload hidden files or subdirectories
                (i.e. those beginning with a '.').
            upload_path: Optional[str] = None
                Name of the directory in the blob store file system. If omitted,
                a unique random string will be the directory.

        Returns:
            str:
                A reference to the uploaded directory's location in the blob store. This
                reference can be used to refer to that object when writing RIME configs.
                Please store this reference for future access to the directory.

        Raises:
            FileNotFoundError
                When the directory ``dir_path`` does not exist.
            IOError
                When ``dir_path`` is not a directory or contains no files.
            ValueError
                When the specified upload_path is an empty string or
                there was an error in obtaining a blobstore location from the
                RIME backend or in uploading ``dir_path`` to RIME's blob store.
                In the scenario the directory fails to upload, files will NOT
                automatically be deleted.
        """
        if upload_path is not None and upload_path == "":
            raise ValueError("specified upload_path must not be an empty string")
        if isinstance(dir_path, str):
            dir_path = Path(dir_path)
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.upload_model_directory(
                dir_path, upload_hidden=upload_hidden, upload_path=upload_path,
            )

    def list_uploaded_file_urls(self) -> Iterator[str]:
        """Return an iterator of file paths that have been uploaded using ``client.upload_file``.

        Returns:
            Iterator[str]:
                An iterator of file path strings.

        Example:
            .. code-block:: python

                # List all file URLs
                urls = rime_client.list_uploaded_file_urls()
        """
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.list_uploaded_files_urls()

    def delete_uploaded_file_url(self, upload_url: str) -> None:
        """Delete the file at the specified upload url in the RIME blob store.

        Args:
            upload_url: str
                Url to the file to be deleted in the RIME blob store.

        Returns:
            None

        Example:
            .. code-block:: python

                # Delete a file URL returned by list_uploaded_file_urls
                urls = rime_client.list_uploaded_file_urls()
                first_url = next(urls)
                rime_client.delete_uploaded_file_url(first_url)
        """
        with RESTErrorHandler():
            fum = FileUploadModule(self._api_client)
            return fum.delete_uploaded_file_url(upload_url)

    def get_job(self, job_id: str) -> BaseJob:
        """Get job by ID.

        Args:
            job_id: ID of the Job to return.

        Returns:
            Job:
                A ``Job`` object.

        Raises:
            ValueError
                This error is generated when no Job with the specified ID exists.

        Example:
            .. code-block:: python

                # Get Job with ID if it exists.
                job = rime_client.get_job("123-456-789")
        """
        api = swagger_client.JobReaderApi(self._api_client)
        try:
            job_response = api.job_reader_get_job(job_id=job_id)
        except ApiException as e:
            if e.status == HTTPStatus.BAD_REQUEST:
                raise ValueError(f"job id `{job_id}` is not a valid job id.")
            elif e.status == HTTPStatus.NOT_FOUND:
                raise ValueError(f"Did not find job id `{job_id}`.")
            else:
                raise ValueError(e.reason) from None
        if job_response.job.job_type == RimeJobType.MODEL_STRESS_TEST:
            return Job(self._api_client, job_id)
        elif job_response.job.job_type == RimeJobType.FIREWALL_BATCH_TEST:
            return ContinuousTestJob(self._api_client, job_id)
        elif job_response.job.job_type == RimeJobType.IMAGE_BUILDER:
            return ImageBuilderJob(self._api_client, job_id)
        elif job_response.job.job_type == RimeJobType.FILE_SCAN:
            return FileScanJob(self._api_client, job_id)
        else:
            raise ValueError(f"Invalid job type {job_response.job.job_type}.")

    def start_file_scan(
        self,
        model_file_info: dict,
        custom_image: Optional[RuntimeinfoCustomImage] = None,
        rime_managed_image: Optional[str] = None,
        ram_request_megabytes: Optional[int] = None,
        cpu_request_millicores: Optional[int] = None,
        agent_id: Optional[str] = None,
    ) -> FileScanJob:
        """Start a File Scan job.

        Args:
            model_file_info: dict
                Configuration for the ML file scan, which specifies the model file
                or repository.
            custom_image: Optional[RuntimeinfoCustomImage]
                Specification of a customized container image to use running the model
                test. The image must have all dependencies required by your model.
                The image must specify a name for the image and optionally a pull secret
                (of type RuntimeinfoCustomImagePullSecret) with the name of the
                kubernetes pull secret used to access the given image.
            rime_managed_image: Optional[str]
                Name of a Managed Image to use when running the model test.
                The image must have all dependencies required by your model. To create
                new Managed Images with your desired dependencies, use the client's
                `create_managed_image()` method.
            ram_request_megabytes: Optional[int]
                Megabytes of RAM requested for the Stress Test Job.
                The limit is equal to megabytes requested.
            cpu_request_millicores: Optional[int]
                Millicores of CPU requested for the Stress Test Job.
                The limit is equal to millicores requested.
            agent_id: Optional[str]
                ID of the Agent that runs the File Scan job.
                When unspecified, the workspace's default Agent is used.

        Returns:
            FileScanJob:
                An ML File Scan Job object.

        Raises:
            ValueError
                This error is generated when the request to the FileScanning
                service fails.

        Example:
            This example shows how to scan a Huggingface model file.

        .. code-block:: python

            model_file_info = {
                "scan_type": "huggingface",
                "scan_path": "https://huggingface.co/transformers/v2.11.0",
            }

           job = rime_client.start_file_scan(model_file_info)
        """
        if not isinstance(model_file_info, dict):
            raise ValueError("The configuration must be a dictionary")

        if ram_request_megabytes is not None and ram_request_megabytes <= 0:
            raise ValueError(
                "The requested number of megabytes of RAM must be positive"
            )

        if cpu_request_millicores is not None and cpu_request_millicores <= 0:
            raise ValueError(
                "The requested number of millicores of CPU must be positive"
            )
        model_info = model_info_from_dict(model_file_info)
        req = RimeStartFileScanRequest(file_info=model_info,)

        req.run_time_info = RuntimeinfoRunTimeInfo()
        if cpu_request_millicores:
            req.run_time_info.resource_request.cpu_request_millicores = (
                cpu_request_millicores
            )
        if ram_request_megabytes:
            req.run_time_info.resource_request.ram_request_megabytes = (
                ram_request_megabytes
            )
        if custom_image:
            req.run_time_info.custom_image = RuntimeinfoCustomImageType(
                custom_image=custom_image
            )
        if rime_managed_image:
            req.run_time_info.custom_image = RuntimeinfoCustomImageType(
                managed_image_name=rime_managed_image
            )
        if agent_id:
            req.run_time_info.agent_id = agent_id

        Client._throttler.throttle(
            throttling_msg="Your request is throttled to limit # of file scans."
        )
        api = swagger_client.FileScanningApi(self._api_client)
        with RESTErrorHandler():
            response = api.file_scanning_start_file_scan(body=req)
            job: RimeJobMetadata = response.job
            return FileScanJob(self._api_client, job.job_id)

    def list_file_scan_results(self) -> Iterator[dict]:
        """List all ML file scan results.

        These contain the security reports for the scanned files
        or repositories.

        Returns:
            Iterator[dict]:
                An iterator of dictionaries, each dictionary represents a single ML
                File Scan result.

        Raises:
            ValueError
                This error is generated when the request to the FileScanning
                service fails.

        Example:
            .. code-block:: python

                # List all ML file scan results.
                results = rime_client.list_file_scan_results()
        """
        # Iterate through the pages of file scan results and break at the last page.
        page_token = ""
        api = swagger_client.FileScanningApi(self._api_client)
        while True:
            with RESTErrorHandler():
                res = api.file_scanning_list_file_scan_results(
                    page_token=page_token, page_size=20
                )
            for file_scan_result in res.results:
                model_file_info = convert_model_info_to_dict(
                    file_scan_result.model_file_info
                )
                file_scan_result_dict = file_scan_result.to_dict()
                file_scan_result_dict["model_file_info"] = model_file_info
                yield file_scan_result_dict

            # If we've reached the last page token
            if not res.has_more:
                break

            # Move to the next page
            page_token = res.next_page_token
