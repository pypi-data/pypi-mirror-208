import base64
from datetime import timedelta
from io import IOBase
import json
import os
from urllib.parse import urlencode
import jwt
import requests
import sys
import warnings
import io
import re

from craft_ai_sdk.constants import DEPLOYMENT_EXECUTION_RULES

from .io import INPUT_OUTPUT_TYPES, Input, Output, InputSource, OutputDestination
from craft_ai_sdk.exceptions import SdkException

from .utils import (
    STEP_PARAMETER,
    _datetime_to_timestamp_in_ms,
    handle_data_store_response,
    handle_http_request,
    handle_http_response,
    log_action,
    log_func_result,
    map_container_config_step_parameter,
    merge_paths,
    use_authentication,
    remove_none_values,
)

warnings.simplefilter("always", DeprecationWarning)


class CraftAiSdk:
    """Main class to instantiate

    Attributes:
        base_environment_url (str): Base URL to CraftAI Environment.
        base_environment_api_url (str): Base URL to CraftAI Environment API.
        base_control_url (str): Base URL to CraftAI authorization server.
        base_control_api_url (str): Base URL to CraftAI authorization server API.
        verbose_log (bool): If True, information during method execution will be
            printed.
        warn_on_metric_outside_of_step (bool): If True, a warning will be printed when
            a metric is added outside of a step.
    """

    _access_token_margin = timedelta(seconds=30)
    _version = "0.16.0rc1"  # Would be better to share it somewhere

    def __init__(
        self,
        sdk_token=None,
        environment_url=None,
        control_url=None,
        verbose_log=None,
        warn_on_metric_outside_of_step=True,
    ):
        """Inits CraftAiSdk.

        Args:
            sdk_token (:obj:`str`, optional): SDK token. You can retrieve it
                from the website.
                Defaults to ``CRAFT_AI_SDK_TOKEN`` environment variable.
            environment_url (:obj:`str`, optional): URL to CraftAI environment.
                Defaults to ``CRAFT_AI_ENVIRONMENT_URL`` environment variable.
            control_url (:obj:`str`, optional): URL to CraftAI authorization server.
                You probably don't need to set it.
                Defaults to ``CRAFT_AI_CONTROL_URL`` environment variable, or
                https://mlops-platform.craft.ai.
            verbose_log (:obj:`bool`, optional): If ``True``, information during method
                execution will be printed.
                Defaults to ``True`` if the environment variable ``SDK_VERBOSE_LOG`` is
                set to ``true``; ``False`` if it is set to ``false``; else, defaults to
                ``True`` in interactive mode; ``False`` otherwise.
            warn_on_metric_outside_of_step (:obj:`bool`, optional): If ``True``, a
                warning will be raised when a metric is added outside of a step.
                Defaults to ``True``.

        Raises:
            ValueError: if the ``sdk_token`` or ``environment_url`` is not defined and
            the corresponding environment variable is not set.
        """
        self._session = requests.Session()
        self._session.headers["craft-ai-client"] = f"craft-ai-sdk@{self._version}"

        # Set authorization token
        if sdk_token is None:
            sdk_token = os.environ.get("CRAFT_AI_SDK_TOKEN")
        if not sdk_token:
            raise ValueError(
                'Parameter "sdk_token" should be set, since '
                '"CRAFT_AI_SDK_TOKEN" environment variable is not defined.'
            )
        self._refresh_token = sdk_token
        self._access_token = None
        self._access_token_data = None

        # Set base environment url
        if environment_url is None:
            environment_url = os.environ.get("CRAFT_AI_ENVIRONMENT_URL")
        if not environment_url:
            raise ValueError(
                'Parameter "environment_url" should be set, since '
                '"CRAFT_AI_ENVIRONMENT_URL" environment variable is not defined.'
            )
        environment_url = environment_url.rstrip("/")
        self.base_environment_url = environment_url
        self.base_environment_api_url = f"{environment_url}/api/v1"

        # Set base control url
        if control_url is None:
            control_url = os.environ.get("CRAFT_AI_CONTROL_URL")
        if not control_url:
            control_url = "https://mlops-platform.craft.ai"
        control_url = control_url.rstrip("/")
        self.base_control_url = control_url
        self.base_control_api_url = f"{control_url}/api/v1"

        if verbose_log is None:
            env_verbose_log = os.environ.get("SDK_VERBOSE_LOG", "").lower()
            # Detect interactive mode: https://stackoverflow.com/a/64523765
            verbose_log = (
                True
                if env_verbose_log == "true"
                else False
                if env_verbose_log == "false"
                else hasattr(sys, "ps1")
            )
        self.verbose_log = verbose_log

        # Set warn_on_metric_outside_of_step
        self.warn_on_metric_outside_of_step = warn_on_metric_outside_of_step

    # _____ REQUESTS METHODS _____

    @handle_http_request
    @use_authentication
    def _get(self, url, params=None, **kwargs):
        return self._session.get(
            url,
            params=params,
            **kwargs,
        )

    @handle_http_request
    @use_authentication
    def _post(self, url, data=None, params=None, files=None, **kwargs):
        return self._session.post(
            url,
            data=data,
            params=params,
            files=files,
            **kwargs,
        )

    @handle_http_request
    @use_authentication
    def _put(self, url, data=None, params=None, files=None, **kwargs):
        return self._session.put(
            url,
            data=data,
            params=params,
            files=files,
            **kwargs,
        )

    @handle_http_request
    @use_authentication
    def _delete(self, url, **kwargs):
        return self._session.delete(url, **kwargs)

    # _____ AUTHENTICATION & PROFILE _____

    @handle_http_request
    def _query_refresh_access_token(self):
        url = f"{self.base_control_api_url}/auth/refresh"
        data = {"refresh_token": self._refresh_token}
        return self._session.post(url, json=data)

    def _refresh_access_token(self):
        response = self._query_refresh_access_token()
        self._access_token = response["access_token"]
        self._access_token_data = jwt.decode(
            self._access_token, options={"verify_signature": False}
        )

    def _clear_access_token(self):
        self._access_token = None
        self._access_token_data = None

    def who_am_i(self):
        """Get the information of the current user

        Returns:
            :obj:`dict` containing user infos"""
        url = f"{self.base_control_api_url}/users/me"
        return self._get(url)

    @property
    def warn_on_metric_outside_of_step(self):
        """Whether a warning should be raised when a metric is added outside of a
        step."""
        return self._warn_on_metric_outside_of_step

    @warn_on_metric_outside_of_step.setter
    def warn_on_metric_outside_of_step(self, value):
        if not isinstance(value, bool):
            raise TypeError("warn_on_metric_outside_of_step must be a boolean")
        self._warn_on_metric_outside_of_step = value

    # _____ STEPS _____

    def _log_step_with_io(self, step):
        if {"name", "inputs", "outputs"} <= step.keys():
            msg = f'Step "{step["name"]}" created'
            if step["inputs"]:
                msg += "\n  Inputs: "
                for inp in step["inputs"]:
                    required_str = ", required" if inp.get("is_required", False) else ""
                    msg += f'\n    - {inp["name"]} ({inp["data_type"]}{required_str})'

            if step["outputs"]:
                msg += "\n  Outputs: "
                for output in step["outputs"]:
                    msg += f'\n    - {output["name"]} ({output["data_type"]})'

            log_action(self, msg)

    @log_func_result("Steps creation")
    def create_step(
        self,
        step_name,
        function_path=None,
        function_name=None,
        repository_branch=STEP_PARAMETER.FALLBACK_PROJECT,
        description=None,
        container_config=None,
        inputs=None,
        outputs=None,
    ):
        """Create pipeline step from a function located on a remote repository.

        Use :obj:`STEP_PARAMETER` to explicitly set a value to null or fall back on
        project information.

        Args:
            step_name (str): Step name.
            function_path (:obj:`str`, optional): Path to the file that contains the
                function. This parameter is required if parameter "dockerfile_path"
                is not specified.
            function_name (:obj:`str`, optional): Name of the function in that file.
                This parameter is required if parameter "dockerfile_path" is not
                specified.
            repository_branch (:obj:`str`, optional): Branch name. Defaults to falling
                back on project information.
            description (:obj:`str`, optional): Description. Defaults to None.
            container_config (:obj:`dict[str, str]`, optional): Some step configuration,
                with the following optional keys:

                * ``"language"`` (:obj:`str`): Language and version used for the step.
                  Defaults to falling back on project information.
                * ``"repository_url"`` (:obj:`str`): Remote repository url.
                  Defaults to falling back on project information.
                * ``"repository_deploy_key"`` (:obj:`str`): Private SSH key of the
                  repository.
                  Defaults to falling back on project information, can be set to null.
                * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
                  file. Environment variables created through
                  :func:`create_or_update_environment_variable` can be used
                  in requirements.txt, as in ``"${ENV_VAR}"``.
                  Defaults to falling back on project information, can be set to null.
                * ``"included_folders"`` (:obj:`list[str]`): List of folders and files
                  in the repository required for the step execution.
                  Defaults to falling back on project information, can be set to null.
                * ``"system_dependencies"`` (:obj:`list[str]`): List of system
                  dependencies.
                  Defaults to falling back on project information, can be set to null.
                * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile. This
                  parameter should only be used as a last resort and for advanced use.
                  When specified, the following parameters should be set to null:
                  ``"function_path"``, ``"function_name"``, ``"language"``,
                  ``"requirements_path"`` and ``"system_dependencies"``.

            inputs(`list` of instances of :class:`Input`): List of inputs. Each
                parameter of the step function should be specified as an instance of
                :class:`Input` via this parameter `inputs`.
                During the execution of the step, the value of the inputs would be
                passed as function arguments.
            outputs(`list` of instances of :class:`Output`): List of the step
                outputs. For the step to have outputs, the function should return a
                :obj:`dict` with the name of the output as keys and the value of the
                output as values. Each output should be specified as an instance
                of :class:`Output` via this parameter `outputs`.

        Returns:
            :obj:`list` of :obj:`dict[str, str]`: List of steps represented as
            :obj:`dict` (with either keys ``"id"`` and ``"name"`` if the creation
            succeeded or keys ``"name"`` and ``"error"`` if the creation failed).
        """

        container_config = {} if container_config is None else container_config.copy()
        if repository_branch is not None:
            container_config.update({"repository_branch": repository_branch})

        data = remove_none_values(
            {
                "step_name": step_name,
                "function_path": function_path,
                "function_name": function_name,
                "description": description,
                "container_config": map_container_config_step_parameter(
                    container_config
                ),
            }
        )

        if inputs is not None:
            if any([not isinstance(input_, Input) for input_ in inputs]):
                raise ValueError("'inputs' must be a list of instances of Input.")
            data["inputs"] = [inp.to_dict() for inp in inputs]

        if outputs is not None:
            if any([not isinstance(output_, Output) for output_ in outputs]):
                raise ValueError("'outputs' must be a list of instances of Output.")
            data["outputs"] = [output.to_dict() for output in outputs]

        url = f"{self.base_environment_api_url}/steps"

        log_action(
            self,
            "Please wait while step is being created. This may take a while...",
        )

        created_step = self._post(url, json=data)
        self._log_step_with_io(created_step)
        return created_step

    def get_step(self, step_name):
        """Get a single step if it exists.

        Args:
            step_name (str): The name of the step to get.

        Returns:
            :obj:`dict`: ``None`` if the step does not exist; otherwise
            the step information, with the following keys:

                * ``"name"`` (:obj:`str`): Name of the step.
                * ``"status"`` (:obj:`str`): either ``"Pending"`` or ``"Ready"``.
                * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
                * ``"updated_at"`` (:obj:`str`): The last update date in ISO format.
                * ``"inputs"`` (:obj:`dict`): The inputs of the step.
                * ``"outputs"`` (:obj:`dict`): The outputs of the step.
        """
        url = f"{self.base_environment_api_url}/steps/{step_name}"
        try:
            step = self._get(
                url,
            )
        except SdkException as error:
            if error.status_code == 404:
                return None
            raise error

        # Filter step information
        returned_keys = (
            "name",
            "status",
            "created_at",
            "updated_at",
            "inputs",
            "outputs",
        )
        return dict((key, step[key]) for key in returned_keys if key in step)

    def list_steps(self):
        """Get the list of all steps.

        Returns:
            :obj:`list` of :obj:`dict`: List of steps represented as :obj:`dict`
            (with keys ``"name"``, ``"status"``, ``"created_at"``, ``"updated_at"``).
        """
        url = f"{self.base_environment_api_url}/steps"

        return self._get(url)

    @log_func_result("Step update")
    def update_step(
        self,
        step_name,
        function_path=None,
        function_name=None,
        repository_branch=STEP_PARAMETER.FALLBACK_PROJECT,
        description=None,
        container_config=None,
    ):
        """Update a pipeline step from a source code located on a remote repository.

        The current step configuration will be **replaced** by the provided options.
        Use :obj:`STEP_PARAMETER` to explicitly set a value to null or fall back on
        project information.

        Warning:
            This feature is experimental and may behave unexpectedly. It is your
            responsibility to check the state and behavior of the step after an update.
            If the creation of the new step configuration takes more than roughly a
            minute, this function will return (time out) before the update terminated
            and you will need to check the step status manually at regular intervals.
            If several step updates are applies at the same time, in some rare cases the
            code used for the step may not match its configuration.

        Args:
            step_name (str): Name of the step to update.
            function_path (:obj:`str`, optional): Path to the file that contains the
                function. This parameter is required if parameter "dockerfile_path"
                is not specified.
            function_name (:obj:`str`, optional): Name of the function in that file.
                This parameter is required if parameter "dockerfile_path" is not
                specified.
            repository_branch (:obj:`str`, optional): Branch name. Defaults to falling
                back on project information.
            description (:obj:`str`, optional): Description. Defaults to None.
            container_config (:obj:`dict[str, str]`, optional): Some step configuration,
                with the following optional keys:

                * ``"language"`` (:obj:`str`): Language and version used for the step.
                  Defaults to falling back on project information.
                * ``"repository_url"`` (:obj:`str`): Remote repository url.
                  Defaults to falling back on project information.
                * ``"repository_deploy_key"`` (:obj:`str`): Private SSH key of the
                  repository.
                  Defaults to falling back on project information, can be set to null.
                * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
                  file. Environment variables created through
                  :func:`create_or_update_environment_variable` can be used
                  in requirements.txt, as in ``"${ENV_VAR}"``.
                  Defaults to falling back on project information, can be set to null.
                * ``"included_folders"`` (:obj:`list[str]`): List of folders and files
                  in the repository required for the step execution.
                  Defaults to falling back on project information, can be set to null.
                * ``"system_dependencies"`` (:obj:`list[str]`): List of system
                  dependencies.
                  Defaults to falling back on project information, can be set to null.
                * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile. This
                  parameter should only be used as a last resort and for advanced use.
                  When specified, the following parameters should be set to null:
                  ``"function_path"``, ``"function_name"``, ``"language"``,
                  ``"requirements_path"`` and ``"system_dependencies"``.

        Returns:
            :obj:`dict[str, str]`: Information of the updated step represented as
            :obj:`dict` (with either keys ``"id"`` and ``"name"`` if the creation
            succeeded or keys ``"name"`` and ``"error"`` if the creation failed).
        """

        url = f"{self.base_environment_api_url}/steps/{step_name}"

        container_config = {} if container_config is None else container_config.copy()
        if repository_branch is not None:
            container_config.update({"repository_branch": repository_branch})
        data = remove_none_values(
            {
                "function_path": function_path,
                "function_name": function_name,
                "description": description,
                "container_config": map_container_config_step_parameter(
                    container_config
                ),
            }
        )

        log_action(
            self,
            "Please wait while step is being updated. This may take a while...",
        )
        return self._put(url, json=data)

    @log_func_result("Step deletion")
    def delete_step(self, step_name, force_dependents_deletion=False):
        """Delete one step.

        Args:
            step_name (str): Name of the step to delete
                as defined in the ``config.yaml`` configuration file.
            force_dependents_deletion (:obj:`bool`, optional): if True the associated
                step’s dependencies will be deleted too (pipeline, pipeline executions,
                deployments). Defaults to False.

        Returns:
            :obj:`dict[str, str]`: Deleted step represented as :obj:`dict`
            (with keys ``"id"`` and ``"name"``).
        """
        url = f"{self.base_environment_api_url}/steps/{step_name}"
        params = {
            "force_dependents_deletion": force_dependents_deletion,
        }
        return self._delete(url, params=params)

    # _____ PIPELINES _____

    @log_func_result("Pipeline creation")
    def create_pipeline(self, pipeline_name, step_name):
        """Create a pipeline containing a single step.

        Args:
            pipeline_name (str): Name of the pipeline to be created.
            step_name (str): Name of the step to be included in the pipeline.
                Note that the step should have the status ``"Ready"`` to create the
                pipeline.

        Returns:
            :obj:`dict[str, str]`: Created pipeline represented as :obj:`dict`
            (with key ``"id"``).
        """
        url = f"{self.base_environment_api_url}/pipelines"
        body = {
            "pipeline_name": pipeline_name,
            "step_names": [step_name],
        }

        resp = self._post(url, json=body)
        return resp

    def _get_pipeline(self, pipeline_name):
        url = f"{self.base_environment_api_url}/pipelines/{pipeline_name}"
        return self._get(url)

    def get_pipeline(self, pipeline_name):
        """Get a single pipeline if it exists.

        Args:
            pipeline_name (str): Name of the pipeline to get.

        Returns:
            :obj:`dict`: The pipeline information or None if the pipeline does not
            exist.

                * ``"id"`` (:obj:`str`): Pipeline id.
                * ``"name"`` (:obj:`str`): Pipeline name.
                * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
                * ``"steps"`` (:obj:`list`): List of step names.
        """
        try:
            return self._get_pipeline(pipeline_name)
        except SdkException as error:
            if error.status_code == 404:
                return None
            raise error

    def list_pipelines(self):
        """Get the list of all pipelines.

        Returns:
            :obj:`list` of :obj:`dict`: List of pipelines represented as :obj:`dict`
            (with keys ``"pipeline_name"``, ``"created_at"``).
        """
        url = f"{self.base_environment_api_url}/pipelines"

        return self._get(url)

    @log_func_result("Pipeline deletion")
    def delete_pipeline(self, pipeline_name, force_deployments_deletion=False):
        """Delete a pipeline identified by its name and id.

        Args:
            pipeline_name (str): Name of the pipeline.
            force_deployments_deletion (:obj:`bool`, optional): if True the associated
                endpoints will be deleted too. Defaults to False.

        Returns:
            :obj:`dict`: The deleted pipeline and its associated deleted endpoints.
            The returned ``dict`` contains two keys:

                * ``"pipeline"`` (:obj:`dict`): Deleted pipeline represented as
                  :obj:`dict` (with keys ``"id"`` and ``"name"``).
                * ``"endpoints"`` (:obj:`list`): List of deleted endpoints represented
                  as :obj:`dict` (with keys ``"id"`` and ``"name"``).
        """
        url = f"{self.base_environment_api_url}/pipelines/{pipeline_name}"
        params = {
            "force_deployments_deletion": force_deployments_deletion,
        }
        return self._delete(url, params=params)

    # _____ PIPELINE EXECUTIONS _____

    @log_func_result("Pipeline execution startup")
    def execute_pipeline(self, pipeline_name):
        """Execute a pipeline.

        Warning:
            .. deprecated:: 0.8.1
             This function is deprecated and its usage is not supported.
             Prefer creating an endpoint and triggering your pipeline with it.

        Args:
            pipeline_name (str): Name of an existing pipeline.

        Returns:
            :obj:`dict[str, str]`: Created pipeline execution represented as :obj:`dict`
            (with key ``"execution_id"``).
        """
        warnings.warn(
            "execute_pipeline is deprecated since version 0.8.1", DeprecationWarning
        )

        url = f"{self.base_environment_api_url}/pipelines/{pipeline_name}/run"

        resp = self._post(url, allow_redirects=False)

        log_action(
            self,
            "Pipeline execution may take a while. Please check regularly its status "
            + "with `get_pipeline_execution`",
        )
        return resp

    @log_func_result("Pipeline execution startup")
    def run_pipeline(self, pipeline_name, inputs=None, inputs_mapping=None):
        """Run a pipeline.

        Args:
            pipeline_name (str): Name of an existing pipeline.
            inputs (dict, optional): Dictionary of inputs to pass to the pipeline with
                input names as keys and corresponding values as values.
                For files, the value should be the path to the file or a file content
                in an instance of io.IOBase.
                Defaults to None.
            inputs_mapping(`list` of instances of :class:`InputSource`):
                List of input mappings, to map pipeline inputs to different
                sources (such as environment variables). See :class:`InputSource`
                for more details.

        Returns:
            :obj:`dict[str, str]`: Created pipeline execution represented as :obj:`dict`
            with output_names as keys and corresponding values as values.
        """
        if inputs is None:
            inputs = {}
        # Retrieve pipeline input types
        pipeline = self._get_pipeline(pipeline_name)
        pipeline_inputs = pipeline["open_inputs"]
        input_types = {
            input["input_name"]: input["data_type"] for input in pipeline_inputs
        }

        # Get files to upload and data to send
        files = {}
        data = {"json_inputs": {}, "inputs_mapping": []}
        for input_name, input_value in inputs.items():
            if input_types.get(input_name) == INPUT_OUTPUT_TYPES.FILE:
                if isinstance(input_value, str):
                    files[input_name] = open(input_value, "rb")
                elif isinstance(input_value, IOBase) and input_value.readable():
                    files[input_name] = input_value
                else:
                    raise SdkException(
                        f"Input {input_name} is a file but \
value is not a string or bytes"
                    )
            elif input_types.get(input_name) != INPUT_OUTPUT_TYPES.FILE:
                data["json_inputs"][input_name] = input_value
        data["json_inputs"] = json.dumps(data["json_inputs"])
        if inputs_mapping is not None:
            if any(
                [
                    not isinstance(input_mapping_, InputSource)
                    for input_mapping_ in inputs_mapping
                ]
            ):
                raise ValueError(
                    "'inputs_mapping' must be a list of instances of InputSource."
                )
            data["inputs_mapping"] = json.dumps(
                [input_mapping_.to_dict() for input_mapping_ in inputs_mapping]
            )
        # Execute pipeline
        url = f"{self.base_environment_api_url}/pipelines/{pipeline_name}/run"
        post_result = self._post(url, data=data, files=files, allow_redirects=False)
        for file in files.values():
            file.close()
        log_action(
            self,
            f"The pipeline execution may take a while, \
you can check its status and get information on the Executions page of the front-end.\n\
Its execution ID is \"{post_result['execution_id']}\".",
        )
        # Wait for pipeline execution to finish
        execution_id = post_result["execution_id"]
        return self._retrieve_pipeline_execution_outputs(pipeline_name, execution_id)

    @log_func_result("Pipeline execution results retrieval")
    def _retrieve_pipeline_execution_outputs(self, pipeline_name, execution_id):
        url = (
            f"{self.base_environment_api_url}"
            f"/pipelines/{pipeline_name}/executions/{execution_id}\
/outputs?wait_for_results=true"
        )
        response = self._get(url)

        parsed_response = {}
        for output in response["outputs"]:
            if output == "artifact":
                for artifact_name in response["outputs"]["artifact"]:
                    parsed_response[
                        artifact_name
                    ] = self._retrieve_single_pipeline_execution_output(
                        pipeline_name,
                        execution_id,
                        artifact_name,
                    )
            elif output == "parameter":
                for parameter_name in response["outputs"]["parameter"]:
                    parsed_response[parameter_name] = response["outputs"]["parameter"][
                        parameter_name
                    ]
        return parsed_response

    def _retrieve_single_pipeline_execution_output(
        self, pipeline_name, execution_id, output_name
    ):
        url = (
            f"{self.base_environment_api_url}"
            f"/pipelines/{pipeline_name}\
/executions/{execution_id}/outputs/{output_name}"
        )
        response = self._get(url)
        return response

    def list_pipeline_executions(self, pipeline_name):
        """Get a list of executions for the given pipeline

        Args:
            pipeline_name (str): Name of an existing pipeline.

        Returns:
            :obj:`list`: A list of information on the pipeline execution
            represented as dict (with keys ``"execution_id"``,
            ``"status"``, ``"created_at``, ``"steps"``, ``"pipeline_name"``).
            In particular the keys:

                * ``"steps"`` is a :obj:`list` of the execution steps represented
                  as :obj:`dict` (with keys ``"name"``, ``"status"``).
                * ``"pipeline_name"`` is the executed pipeline name.
        """
        url = f"{self.base_environment_api_url}/pipelines/{pipeline_name}/executions"

        return self._get(url)

    def get_pipeline_execution(self, pipeline_name, execution_id):
        """Get the status of one pipeline execution identified by its name.

        Args:
            pipeline_name (str): Name of an existing pipeline.
            execution_id (str): Name of the pipeline execution.

        Returns:
            :obj:`dict`: Information on the pipeline execution with id
            ``execution_id`` represented as dict (with keys ``"execution_id"``,
            ``"status"``, ``"created_at``, ``"steps"``, ``"pipeline_name"``,
            ``"created_by"``).
            In particular the keys:

                * ``"steps"`` is a :obj:`list` of the execution steps represented
                  as :obj:`dict` (with keys ``"name"``, ``"status"``).
                * ``"pipeline_name"`` is the executed pipeline name.
        """
        pipeline_url = f"{self.base_environment_api_url}/pipelines/{pipeline_name}"
        url = f"{pipeline_url}/executions/{execution_id}"

        return self._get(url)

    def get_pipeline_execution_logs(
        self,
        pipeline_name,
        execution_id,
        from_datetime=None,
        to_datetime=None,
        limit=None,
    ):
        """Get the logs of an executed pipeline identified by its name.

        Args:
            pipeline_name (str): Name of an existing pipeline.
            execution_id (str): ID of the pipeline execution.
            from_datetime (:obj:`datetime.time`, optional): Datetime from which the logs
                are collected.
            to_datetime (:obj:`datetime.time`, optional): Datetime until which the logs
                are collected.
            limit (:obj:`int`, optional): Maximum number of logs that are collected.

        Returns:
            :obj:`list`: List of collected logs represented as dict (with keys
            ``"message"``, ``"timestamp"`` and ``"stream"``).
        """
        pipeline_url = f"{self.base_environment_api_url}/pipelines/{pipeline_name}"
        url = f"{pipeline_url}/executions/{execution_id}/logs"

        data = {}
        if from_datetime is not None:
            data["from"] = _datetime_to_timestamp_in_ms(from_datetime)
        if to_datetime is not None:
            data["to"] = _datetime_to_timestamp_in_ms(to_datetime)
        if limit is not None:
            data["limit"] = limit

        log_action(
            self,
            "Please wait while logs are being downloaded. This may take a while...",
        )
        logs_by_steps = self._post(url, json=data)

        if len(logs_by_steps) == 0:
            return []

        return logs_by_steps[0]

    # _____ DEPLOYMENTS _____

    @log_func_result("Deployment creation")
    def create_deployment(
        self,
        pipeline_name,
        deployment_name,
        execution_rule,
        inputs_mapping=None,
        outputs_mapping=None,
    ):
        """Create a custom deployment associated to a given pipeline.

        Args:
            pipeline_name (str): Name of the pipeline.
            deployment_name (str): Name of the deployment.
            execution_rule(str): Execution rule of the deployment. Must
                be "endpoint". For convenience, members of the enumeration
                :class:`DEPLOYMENT_EXECUTION_RULES` could be used too.
            inputs_mapping(`list` of instances of :class:`InputSource`):
                List of input mappings, to map pipeline inputs to different
                sources (such as constant values, endpoint inputs, or environment
                variables). See :class:`InputSource` for more details.
                For endpoint rules, if an input of the step in the pipeline is not
                explicitly mapped, it will be automatically mapped to an endpoint
                input with the same name.
            outputs_mapping(`list` of instances of :class:`OutputDestination`):
                List of output mappings, to map pipeline outputs to different
                destinations.
                See :class:`OutputDestination` for more details. Each output
                of the step should be explicitly mapped.

        Returns:
            :obj:`dict[str, str]`: Created endpoint represented as :obj:`dict`
            (with key ``"id"`` and ``"name"``).
        """

        if execution_rule not in set(DEPLOYMENT_EXECUTION_RULES):
            raise ValueError("Invalid 'execution_rule', must be: endpoint.")

        url = f"{self.base_environment_api_url}/endpoints"

        data = {
            "pipeline_name": pipeline_name,
            "name": deployment_name,
        }

        if inputs_mapping is not None:
            if any(
                [
                    not isinstance(input_mapping_, InputSource)
                    for input_mapping_ in inputs_mapping
                ]
            ):
                raise ValueError("'inputs' must be a list of instances of InputSource.")
            data["inputs"] = [
                input_mapping_.to_dict() for input_mapping_ in inputs_mapping
            ]

        if outputs_mapping is not None:
            if any(
                [
                    not isinstance(output_mapping_, OutputDestination)
                    for output_mapping_ in outputs_mapping
                ]
            ):
                raise ValueError(
                    "'outputs' must be a list of instances of OutputDestination."
                )
            data["outputs"] = [
                output_mapping_.to_dict() for output_mapping_ in outputs_mapping
            ]

        # filter optional parameters
        data = {k: v for k, v in data.items() if v is not None}

        return self._post(url, json=data)

    @log_func_result("Endpoint deletion")
    def delete_deployment(self, deployment_name):
        """Delete a deployment identified by its name.

        Args:
            deployment_name (str): Name of the deployment.

        Returns:
            :obj:`dict`: Deleted deployment represented as dict (with keys ``"id"``,
            ``"name"``).
        """
        url = f"{self.base_environment_api_url}/endpoints/{deployment_name}"
        return self._delete(url)

    def list_deployments(self):
        """Get the list of all deployments.

        Returns:
            :obj:`list` of :obj:`dict`: List of deployments represented as :obj:`dict`
            (with keys ``"id"``, ``"name"`` and ``"pipeline"``).
        """
        url = f"{self.base_environment_api_url}/endpoints"
        return self._get(url)

    def get_deployment(self, deployment_name):
        """Get information of a deployment.

        Args:
            deployment_name (str): Name of the deployment.

        Returns:
            :obj:`dict`: Deployment information represented as :obj:`dict` (with keys
            ``"id"``, ``"name"`` and ``"pipeline"``).
        """
        url = f"{self.base_environment_api_url}/endpoints/{deployment_name}"
        return self._get(url)

    # _____ ENDPOINTS _____

    @log_func_result("Endpoint creation")
    def create_endpoint(
        self,
        pipeline_name,
        endpoint_name,
        inputs_mapping=None,
        outputs_mapping=None,
    ):
        """Create a custom endpoint associated to a given pipeline.

        Warning:
            .. deprecated:: 0.8.1
             This function is deprecated and its usage is not supported.
             Prefer using create_deployment instead.

        Args:
            pipeline_name (str): Name of the pipeline.
            endpoint_name (str): Name of the endpoint.
            inputs_mapping(`list` of instances of :class:`InputSource`):
                List of input mappings, to map pipeline inputs to different
                sources (such as constant values, endpoint inputs, or environment
                variables). See :class:`InputSource` for more details.
                If an input of the step in the pipeline is not explicitly mapped, it
                will be automatically mapped to an endpoint input with the same name.
            outputs_mapping(`list` of instances of :class:`OutputDestination`):
                List of output mappings, to map pipeline outputs to different
                destinations (either exposed by the endpoint, or not).
                See :class:`OutputDestination` for more details. Each output
                of the step should be explicitly mapped.

        Returns:
            :obj:`dict[str, str]`: Created endpoint represented as :obj:`dict`
            (with key ``"id"`` and ``"name"``).
        """
        warnings.warn(
            "create_endpoint is deprecated since version 0.12.0", DeprecationWarning
        )
        return self.create_deployment(
            pipeline_name,
            endpoint_name,
            DEPLOYMENT_EXECUTION_RULES.ENDPOINT,
            inputs_mapping,
            outputs_mapping,
        )

    @log_func_result("Endpoint deletion")
    def delete_endpoint(self, endpoint_name):
        """Delete an endpoint identified by its name.

        Warning:
            .. deprecated:: 0.12.0
             This function is deprecated and its usage is not supported.
             Prefer using delete_deployment instead.

        Args:
            endpoint_name (str): Name of the endpoint.

        Returns:
            :obj:`dict`: Deleted endpoint represented as dict (with keys ``"id"``,
            ``"name"``).
        """
        warnings.warn(
            "delete_endpoint is deprecated since version 0.12.0", DeprecationWarning
        )
        return self.delete_deployment(endpoint_name)

    def list_endpoints(self):
        """Get the list of all endpoints.

        Warning:
            .. deprecated:: 0.12.0
             This function is deprecated and its usage is not supported.
             Prefer using list_deployments instead.

        Returns:
            :obj:`list` of :obj:`dict`: List of endpoints represented as :obj:`dict`
            (with keys ``"id"``, ``"name"`` and ``"pipeline"``).
        """
        warnings.warn(
            "list_endpoints is deprecated since version 0.12.0", DeprecationWarning
        )
        return self.list_deployments()

    def get_endpoint(self, endpoint_name):
        """Get information of an endpoint.

        Warning:
            .. deprecated:: 0.12.0
             This function is deprecated and its usage is not supported.
             Prefer using get_deployment instead.

        Args:
            endpoint_name (str): Name of the endpoint.

        Returns:
            :obj:`dict`: Endpoint information represented as :obj:`dict` (with keys
            ``"id"``, ``"name"`` and ``"pipeline"``).
        """
        warnings.warn(
            "get_endpoint is deprecated since version 0.12.0", DeprecationWarning
        )
        return self.get_deployment(endpoint_name)

    @log_func_result("Endpoint trigger")
    def trigger_endpoint(
        self, endpoint_name, endpoint_token, inputs={}, wait_for_results=True
    ):
        """Trigger an endpoint.

        Args:
            endpoint_name (str): Name of the endpoint.
            endpoint_token (str): Token to access endpoint.
            inputs (:obj:`dict`, optional): Dictionary of inputs to pass to the endpoint
                with input names as keys and corresponding values as values.
                For files, the value should be an instance of io.IOBase.
                Defaults to {}.
            wait_for_results (:obj:`bool`, optional): Automatically call
                `retrieve_endpoint_results` and returns the execution result.
                Defaults to `True`.

        Returns:
            :obj:`dict[str, str]`: Created pipeline execution represented as :obj:`dict`
            (with key ``"execution_id"`` if ``"wait_for_results"`` is ``False``,
            otherwise with key ``"status"``, ``"execution"`` & ``"results"`` or
            ``"error"`` depending on ``"status"`` if ``"wait_for_results"`` is ``True``
            or unspecified).
        """

        body = {}
        files = {}
        for input_name, input_value in inputs.items():
            if isinstance(input_value, IOBase) and input_value.readable():
                files[input_name] = input_value
            else:
                body[input_name] = input_value

        url = f"{self.base_environment_url}/endpoints/{endpoint_name}"
        post_result = requests.post(
            url,
            headers={"Authorization": f"EndpointToken {endpoint_token}"},
            allow_redirects=False,
            json=body,
            files=files,
        )
        parsed_response = handle_http_response(post_result)
        if wait_for_results and 200 <= post_result.status_code < 400:
            return self.retrieve_endpoint_results(
                endpoint_name, parsed_response["execution_id"], endpoint_token
            )
        return parsed_response

    @log_func_result("Endpoint result retrieval")
    def retrieve_endpoint_results(self, endpoint_name, execution_id, endpoint_token):
        """Get the results of an endpoint execution.

        Args:
            endpoint_name (str): Name of the endpoint.
            execution_id (str): ID of the execution returned by `trigger_endpoint`.
            endpoint_token (str): Token to access endpoint.

        Returns:
            :obj:`dict[str, str]`: Created pipeline execution represented as :obj:`dict`
            (with key ``"status"``, ``"execution"`` & ``"results"`` or ``"error"``
            depending on ``"status"``).
        """

        url = (
            f"{self.base_environment_url}"
            f"/endpoints/{endpoint_name}/executions/{execution_id}"
        )
        query = urlencode({"token": endpoint_token})
        response = requests.get(f"{url}?{query}")

        # 500 is returned if the pipeline failed too. In that case, it is not a
        # standard API error
        if response.status_code == 500:
            try:
                return handle_http_response(response)
            except KeyError:
                return response.json()

        if "application/octet-stream" in response.headers.get("Content-Type", ""):
            execution_id = response.headers.get("Execution-Id", "")
            content_disposition = response.headers.get("Content-Disposition", "")
            output_name = content_disposition.split(f"_{execution_id}_")[1]
            return {"outputs": {output_name: handle_http_response(response)}}
        else:
            return handle_http_response(response)

    def generate_new_endpoint_token(self, endpoint_name):
        """Generate a new endpoint token for an endpoint.

        Args:
            endpoint_name (str): Name of the endpoint.

        Returns:
            :obj:`dict`: New endpoint token represented as :obj:`dict` (with keys
            ``"endpoint_token"``).
        """
        url = (
            f"{self.base_environment_api_url}"
            f"/endpoints/{endpoint_name}/generate-new-token"
        )
        return self._post(url)

    # _____ DATA STORE _____

    def get_data_store_object_information(self, object_path_in_datastore):
        """Get information about a single object in the data store.

        Args:
            object_path_in_datastore (str): Location of the object in the data store.

        Returns:
            :obj:`dict`: Object information, with the following keys:

                * ``"path"`` (:obj:`str`): Location of the object in the data store.
                * ``"last_modified"`` (:obj:`str`): The creation date or last
                  modification date in ISO format.
                * ``"size"`` (:obj:`int`): The size of the object in bytes.
        """
        url = f"{self.base_environment_api_url}/data-store/information"
        data = {
            "path_to_object": object_path_in_datastore,
        }
        return self._post(url, json=data)

    def list_data_store_objects(self):
        """Get the list of the objects stored in the data store.

        Returns:
            :obj:`list` of :obj:`dict`: List of objects in the data store represented
            as :obj:`dict` (with keys ``"path"``, ``"last_modified"``, and ``"size"``).
        """
        url = f"{self.base_environment_api_url}/data-store/list"
        return self._get(url)

    def _get_upload_presigned_url(self, object_path_in_datastore):
        url = f"{self.base_environment_api_url}/data-store/upload"
        params = {"path_to_object": object_path_in_datastore}
        resp = self._get(url, params=params)
        presigned_url, data = resp["signed_url"], resp["fields"]

        return presigned_url, data

    def _get_upload_presigned_url_without_check(self):
        url = f"{self.base_environment_api_url}/data-store/upload"
        resp = self._get(url)
        presigned_url, data = resp["signed_url"], resp["fields"]

        # Extract prefix condition from the presigned url
        policy = data["policy"]
        policy_decode = json.loads(base64.b64decode(policy))
        prefix_condition = next(
            condition
            for condition in policy_decode["conditions"]
            if isinstance(condition, list) and condition[0] == "starts-with"
        )
        prefix = prefix_condition[-1]
        return presigned_url, data, prefix

    @log_func_result("Object upload")
    def upload_data_store_object(self, filepath_or_buffer, object_path_in_datastore):
        """Upload a file as an object into the data store.

        Args:
            filepath_or_buffer (:obj:`str`, or file-like object): String, path to the
                file to be uploaded ;
                or file-like object implementing a ``read()`` method (e.g. via builtin
                ``open`` function). The file object must be opened in binary mode,
                not text mode.
            object_path_in_datastore (str): Destination of the uploaded file.
        """
        if isinstance(filepath_or_buffer, str):
            # this is a filepath: call the method again with a buffer
            with open(filepath_or_buffer, "rb") as file_buffer:
                return self._upload_data_store_object(
                    file_buffer, object_path_in_datastore
                )

        if not hasattr(filepath_or_buffer, "read"):  # not a readable buffer
            raise ValueError(
                "'filepath_or_buffer' must be either a string (filepath) or an object "
                "with a read() method (file-like object)."
            )
        if isinstance(filepath_or_buffer, io.IOBase) and filepath_or_buffer.tell() > 0:
            filepath_or_buffer.seek(0)
        return self._upload_data_store_object(
            filepath_or_buffer, object_path_in_datastore
        )

    def _upload_data_store_object(self, buffer, object_path_in_datastore):
        files = {"file": buffer}

        try:
            presigned_url, data = self._get_upload_presigned_url(
                object_path_in_datastore
            )
        except SdkException as error:
            validationError = re.match(
                '^"path_to_object" does not match the required pattern. (?P<pattern>.*)$',  # noqa: E501
                error.message,
            )
            if validationError is None:
                raise error
            warnings.warn(
                "The provided object path does not match the required pattern. "
                f"{validationError.group('pattern')} "
                "The use of such path is deprecated and will eventually be forbidden.",
                DeprecationWarning,
            )

            presigned_url, data, prefix = self._get_upload_presigned_url_without_check()
            data["key"] = merge_paths(prefix, object_path_in_datastore)

        resp = requests.post(url=presigned_url, data=data, files=files)
        handle_data_store_response(resp)

    def _get_download_presigned_url(self, object_path_in_datastore):
        url = f"{self.base_environment_api_url}/data-store/download"
        data = {
            "path_to_object": object_path_in_datastore,
        }
        presigned_url = self._post(url, data=data)["signed_url"]
        return presigned_url

    @log_func_result("Object download")
    def download_data_store_object(self, object_path_in_datastore, filepath_or_buffer):
        """Download an object in the data store and save it into a file.

        Args:
            object_path_in_datastore (str): Location of the object to download from the
                data store.
            filepath_or_buffer (:obj:`str` or file-like object):
                String, filepath to save the file to ; or a file-like object
                implementing a ``write()`` method, (e.g. via builtin ``open`` function).
                The file object must be opened in binary mode, not text mode.

        Returns:
            str: content of the file
        """
        presigned_url = self._get_download_presigned_url(object_path_in_datastore)
        resp = requests.get(presigned_url)
        object_content = handle_data_store_response(resp)

        if isinstance(filepath_or_buffer, str):  # filepath
            with open(filepath_or_buffer, "wb") as f:
                f.write(object_content)
        elif hasattr(filepath_or_buffer, "write"):  # writable buffer
            filepath_or_buffer.write(object_content)
            if (
                isinstance(filepath_or_buffer, io.IOBase)
                and filepath_or_buffer.tell() > 0
            ):
                filepath_or_buffer.seek(0)
        else:
            raise ValueError(
                "'filepath_or_buffer' must be either a string (filepath) or an object "
                "with a write() method (file-like object)."
            )

    @log_func_result("Object deletion")
    def delete_data_store_object(self, object_path_in_datastore):
        """Delete an object on the datastore.

        Args:
            object_path_in_datastore (str): Location of the object to be deleted in the
                data store.

        Returns:
            :obj:`dict`: Deleted object represented as dict (with key ``"path"``).
        """
        url = f"{self.base_environment_api_url}/data-store/delete"
        data = {
            "path_to_object": object_path_in_datastore,
        }
        return self._delete(url, data=data)

    # _____ ENVIRONMENT_VARIABLE _____

    @log_func_result("Environment variable definition")
    def create_or_update_environment_variable(
        self, environment_variable_name, environment_variable_value
    ):
        """Create or update an environment variable available for
        all pipelines executions.

        Args:
            environment_variable_name (str):
               Name of the environment variable to create.
            environment_variable_value (str):
               Value of the environment variable to create.

        Returns:
            :obj:`dict`: An object containing the id of environment variable
            (with keys ``"id"``)

        """
        url = (
            f"{self.base_environment_api_url}"
            f"/environment-variables/{environment_variable_name}"
        )
        data = {
            "value": environment_variable_value,
        }
        return self._put(url, data)

    def list_environment_variables(self):
        """Get a list of all environments variables.

        Returns:
            :obj:`list` of :obj:`dict`: List of environment variable
            as :obj:`dict` (with keys ``"name"`` and ``"value"``)
        """
        url = f"{self.base_environment_api_url}/environment-variables"
        return self._get(url)

    @log_func_result("Environment variable deletion")
    def delete_environment_variable(self, environment_variable_name):
        """Delete the specified environment variable

        Args:
           environment_variable_name (str): Name of the environment variable to delete.

        Returns:
            :obj:`dict` (with keys ``"name"`` and ``"value"``) of the
            deleted environment variable
        """
        url = (
            f"{self.base_environment_api_url}"
            f"/environment-variables/{environment_variable_name}"
        )
        return self._delete(url)
