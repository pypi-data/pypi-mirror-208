from strenum import LowercaseStrEnum
from craft_ai_sdk.utils import remove_none_values


class INPUT_OUTPUT_TYPES(LowercaseStrEnum):
    """Enumeration for Input and Output data types."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"
    FILE = "file"


class Input:
    """Class to specify a step input when creating a step
    (cf. :meth:`.CraftAiSdk.create_step`).

    Args:
        name (str): Name of the input. This corresponds to the name of a
            parameter of a step function.
        data_type (str): Type of the input: It could be one of "string", "number",
            "boolean", "json", "array" or "file". For convenience, members of the
            enumeration :class:`INPUT_OUTPUT_TYPES` could be used too.
        description (:obj:`str`, optional): Description. Defaults to None.
        is_required (:obj:`bool`, optional): Specify if an value should be provided at
            execution time. Defaults to None.
        default_value (:obj:`Any`, optional): A default value for the step input at
            execution time. The type for `default_value` should match the type specified
            by `data_type`. Defaults to None.
    """

    def __init__(
        self, name, data_type, description=None, is_required=None, default_value=None
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.is_required = is_required
        self.default_value = default_value

    def to_dict(self):
        input = {
            "name": self.name,
            "data_type": self.data_type,
            "description": self.description,
            "is_required": self.is_required,
            "default_value": self.default_value,
        }
        return remove_none_values(input)


class Output:
    """Class to specify a step output when creating a step
    (cf. :meth:`.CraftAiSdk.create_step`).

    Args:
        name (str): Name of the output. This corresponds to the key of the `dict`
            returned by the step function.
        data_type (Any): Type of the output. It could be one of "string", "number",
            "boolean", "json", "array" or "file". For convenience, members of the
            enumeration :class:`INPUT_OUTPUT_TYPES` could be used too.
        description (:obj:`str`, optional): Description. Defaults to None.
    """

    def __init__(self, name, data_type, description=None):
        self.name = name
        self.data_type = data_type
        self.description = description

    def to_dict(self):
        output = {
            "name": self.name,
            "data_type": self.data_type,
            "description": self.description,
        }

        return remove_none_values(output)


class InputSource:
    """Class to specify to which source a step input should be mapped when creating
    a deployment (cf. :meth:`.CraftAiSdk.create_deployment`). The different sources can
    be one of:

        * :obj:`endpoint_input_name` (`str`): An endpoint input with the provided
          name.
        * :obj:`constant_value`: A constant value.
        * :obj:`environment_variable_name`: The value of the provided
          environment variable.
        * :obj:`is_null`: Nothing.

    If the execution rule of the deployment is endpoint and the input is directly mapped
    to an endpoint input, two more parameters can be specified:

        * :obj:`default_value`
        * :obj:`is_required`

    Args:
        step_input_name (str): Name of the step input to be mapped.
        endpoint_input_name (:obj:`str`, optional): Name of the endpoint input to which
            the input is mapped.
        environment_variable_name (:obj:`str`, optional): Name of the environment
            variable to which the input is mapped.
        constant_value (:obj:`Any`, optional): A constant value.
        is_null (`True`, optional): If specified, the input is not provided any
            value at execution time.
        default_value (:obj:`Any`, optional): This parameter could only be specified if
            the parameter `endpoint_input_name` is specified.
        is_required (:obj:`bool`, optional): This parameter could only be specified if
            the parameter `endpoint_input_name` is specified. If set to `True`, the
            corresponding endpoint input should be provided at execution time.
    """

    def __init__(
        self,
        step_input_name,
        endpoint_input_name=None,
        environment_variable_name=None,
        is_required=None,
        default_value=None,
        constant_value=None,
        is_null=None,
    ):
        self.step_input_name = step_input_name
        self.endpoint_input_name = endpoint_input_name
        self.environment_variable_name = environment_variable_name
        self.is_required = is_required
        self.default_value = default_value
        self.constant_value = constant_value
        self.is_null = is_null

    def to_dict(self):
        input_mapping_dict = {
            "step_input_name": self.step_input_name,
            "endpoint_input_name": self.endpoint_input_name,
            "environment_variable_name": self.environment_variable_name,
            "is_required": self.is_required,
            "default_value": self.default_value,
            "constant_value": self.constant_value,
            "is_null": self.is_null,
        }

        return remove_none_values(input_mapping_dict)


class OutputDestination:
    """Class to specify to which destination a step output should be mapped when creating
    a deployment (cf. :meth:`.CraftAiSdk.create_deployment`). If the execution rule of
    the deployment is endpoint, an output could either be exposed as an output of the
    endpoint (via `endpoint_output_name` parameter) or not (via `is_null` parameter).

    Args:
        step_output_name (str): Name of the step output to be mapped.
        endpoint_output_name (:obj:`str`, optional): Name of the endpoint output to
            which the output is mapped.
        is_null (`True`, optional): If specified, the output is not exposed as a
            deployment output.
    """

    def __init__(self, step_output_name, endpoint_output_name=None, is_null=None):
        self.step_output_name = step_output_name
        self.endpoint_output_name = endpoint_output_name
        self.is_null = is_null

    def to_dict(self):
        output_mapping_dict = {
            "step_output_name": self.step_output_name,
            "endpoint_output_name": self.endpoint_output_name,
            "is_null": self.is_null,
        }

        return remove_none_values(output_mapping_dict)
