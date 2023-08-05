import base64
import builtins
import copy
import io
import json
import os

from abc import ABC, abstractmethod
from importlib import import_module


class InvalidTypeException(Exception):
    def __init__(self, msg, errors=None):
        super().__init__(msg)
        self.msg = msg
        self.errors = errors


class InvalidPayloadException(Exception):
    def __init__(self, msg, errors=None):
        super().__init__(msg)
        self.msg = msg
        self.errors = errors


class TypeSerializer(ABC):
    _schema = {
        "required": False,
    }

    def __init__(self, *args, **kwargs):
        return self.define(*args, **kwargs)

    def define(self, *args, **kwargs):
        for key in kwargs:
            if key in self._schema:
                self._schema[key] = kwargs[key]

    def schema(self, **kwargs):
        return {
            **self._schema,
            **kwargs,
        }

    @abstractmethod
    def serialize(self, obj):
        pass

    @abstractmethod
    def deserialize(self, data):
        pass


class FloatType(TypeSerializer):
    def schema(self):
        return super().schema(type="float")

    def serialize(self, obj):
        try:
            output = float(obj)
        except ValueError:
            raise InvalidTypeException("invalid_float_value")

        return output

    def deserialize(self, data):
        try:
            obj = float(data)
        except ValueError:
            raise InvalidTypeException("invalid_float_value")

        return obj


class StringType(TypeSerializer):
    def define(self, max_length=None, **kwargs):
        self.max_length = max_length
        super().define(**kwargs)

    def schema(self):
        return super().schema(
            **{
                "type": "string",
                "max_length": self.max_length,
            }
        )

    def serialize(self, obj):
        output = str(obj)

        if self.max_length:
            if len(output) > self.max_length:
                raise InvalidTypeException("invalid_string_too_long")

        return output

    def deserialize(self, data):
        obj = str(data)

        if self.max_length:
            if len(obj) > self.max_length:
                raise InvalidTypeException("invalid_string_too_long")

        return obj


class JsonType(TypeSerializer):
    def schema(self):
        return super().schema(type="json")

    def serialize(self, obj):
        if not isinstance(obj, dict) and not isinstance(obj, list):
            raise InvalidTypeException("invalid_json_type")

        try:
            output = json.loads(json.dumps(obj))
        except TypeError:
            raise InvalidTypeException("invalid_json")

        return output

    def deserialize(self, data):
        if isinstance(data, str):
            try:
                obj = json.loads(data)
            except ValueError:
                raise InvalidTypeException("invalid_json_str")
        elif isinstance(data, dict) or isinstance(data, list):
            obj = data
        else:
            raise InvalidTypeException("invalid_json")

        return obj


class ImageType(TypeSerializer):
    def define(self, size=None, mode=None, raw=False, **kwargs):
        self.size = size
        self.mode = mode
        self.raw = raw
        super().define(**kwargs)

    def schema(self):
        return super().schema(
            type="image",
            size=list(self.size) if self.size is not None else None,
            mode=str(self.mode) if self.mode is not None else None,
            raw=self.raw,
        )

    def serialize(self, obj):
        try:
            PIL_Image = import_module("PIL.Image")
        except ModuleNotFoundError:
            raise RuntimeError("pillow_required_for_image_inputs")

        # Load image from disk
        if isinstance(obj, str) and os.path.isfile(obj):
            obj = PIL_Image.open(obj)

        # Load image from base64
        elif isinstance(obj, str):
            base64_data = obj

            if "," in base64_data:
                base64_data = obj.split(",")[1]

            obj = PIL_Image.open(io.BytesIO(base64.b64decode(base64_data)))

        if self.size is not None and obj.size != self.size:
            raise InvalidTypeException("invalid_image_size")

        if self.mode is not None and obj.mode != self.mode:
            raise InvalidTypeException("invalid_image_mode")

        buffer = io.BytesIO()
        obj.save(buffer, format="PNG")
        output = base64.b64encode(buffer.getvalue()).decode("ascii")
        return output

    def deserialize(self, data):
        if self.raw:
            return str(data)

        try:
            PIL_Image = import_module("PIL.Image")
        except ModuleNotFoundError:
            raise RuntimeError("pillow_required_for_image_inputs")

        if "," in data:
            data = data.split(",")[1]

        obj = PIL_Image.open(io.BytesIO(base64.b64decode(data)))

        if self.size is not None and obj.size != self.size:
            raise InvalidTypeException("invalid_image_size")

        if self.mode is not None and obj.mode != self.mode:
            raise InvalidTypeException("invalid_image_mode")

        return obj


class BinaryType(TypeSerializer):
    def schema(self):
        return super().schema(type="binary")

    def serialize(self, obj):
        # Load binary from disk
        if isinstance(obj, str) and os.path.isfile(obj):
            with open(obj, "rb") as f:
                obj = f.read()

        try:
            output = base64.b64encode(obj).decode("ascii")
        except TypeError:
            raise InvalidTypeException("invalid_binary_data")

        return output

    def deserialize(self, data):
        try:
            return io.BytesIO(base64.b64decode(data)).getvalue()
        except TypeError:
            raise InvalidTypeException("invalid_binary_data")


class BooleanType(TypeSerializer):
    """
    In the case of types where both the serialized and deserialized values are
    valid in both JSON payloads, as well as python objects, we can re-use the same
    logic for serialize/deserialize. For example, you can pass a boolean object
    as JSON, but you can also use that type directly in application logic as a boolean.
    """

    def schema(self):
        return super().schema(
            type="boolean",
        )

    def _to_boolean(self, obj):
        if isinstance(obj, bool):
            return obj

        elif isinstance(obj, str):
            if obj.lower() == "true":
                return True
            elif obj.lower() == "false":
                return False
            else:
                raise InvalidTypeException("invalid_boolean_value")

        elif isinstance(obj, int) or isinstance(obj, float):
            obj = int(obj)
            if obj == 1:
                return True
            elif obj == 0:
                return False
            else:
                raise InvalidTypeException("invalid_boolean_value")

        return obj

    def serialize(self, obj):
        return self._to_boolean(obj)

    def deserialize(self, data):
        return self._to_boolean(data)


class PythonVersion:
    Python37 = "python3.7"
    Python38 = "python3.8"
    Python39 = "python3.9"
    Python310 = "python3.10"

    Types = (
        (Python37, "python3.7"),
        (Python38, "python3.8"),
        (Python39, "python3.9"),
        (Python310, "python3.10"),
    )


class GpuType:
    NoGPU = ""
    Any = "any"
    T4 = "T4"
    A10G = "A10G"

    Types = (
        (NoGPU, ""),
        (Any, "any"),
        (T4, "T4"),
        (A10G, "A10G"),
    )


class OutputType:
    Directory = "directory"
    File = "file"

    Types = ((Directory, "directory"), (File, "file"))


class MountType:
    Persistent = "persistent"
    Shared = "shared"

    Types = (
        (Persistent, "persistent"),
        (Shared, "shared"),
    )


class AutoscalingType:
    MaxRequestLatency = "max_request_latency"

    Types = ((MaxRequestLatency, "max_request_latency"),)


class Types:
    Float = FloatType
    String = StringType
    Json = JsonType
    Image = ImageType
    Binary = BinaryType
    Boolean = BooleanType

    type_registry = {
        "float": FloatType,
        "string": StringType,
        "json": JsonType,
        "image": ImageType,
        "binary": BinaryType,
        "boolean": BooleanType,
        
    }

    deprecated_type_registry = {
        "numpy": None,
        "dataframe": None,
        "tensor": None,
    }

    @staticmethod
    def serialize(objects, schema):
        serialized_data = {}
        errors = []

        if not isinstance(objects, dict):
            raise InvalidTypeException("invalid_object_format")

        for key in schema.keys():
            type_schema = schema[key].schema()

            if key not in objects.keys():
                if type_schema["required"]:
                    errors.append(f"{key}:required")
                continue

            if objects[key] is None and not type_schema["required"]:
                serialized_data[key] = None
                continue

            _type = schema[key]
            _input = objects[key]

            try:
                serialized_data[key] = _type.serialize(_input)
            except InvalidTypeException as exc:
                errors.append(f"{key}:{exc}")

        if errors:
            raise InvalidPayloadException("invalid_object", errors=errors)

        return serialized_data

    @staticmethod
    def deserialize(data, schema):
        deserialized_payload = {}
        errors = []

        if not isinstance(data, dict):
            raise InvalidTypeException("invalid_data_format")

        for key in schema.keys():
            type_schema = schema[key].schema()

            if key not in data.keys():
                if type_schema["required"]:
                    errors.append(f"{key}:required")
                continue

            if data[key] is None and not type_schema["required"]:
                deserialized_payload[key] = None
                continue

            _type = schema[key]
            _input = data[key]

            try:
                deserialized_payload[key] = _type.deserialize(_input)
            except InvalidTypeException as exc:
                errors.append(f"{key}:{exc}")

        if errors:
            raise InvalidPayloadException("invalid_data", errors=errors)

        return deserialized_payload

    @staticmethod
    def dump_schema(schema):
        dumped = {}
        for key, val in schema.items():
            dumped[key] = val.schema()

            if getattr(val, "required", True) is False:
                dumped[key]["required"] = False

        return dumped

    @staticmethod
    def load_schema(description):
        if not isinstance(description, dict):
            raise InvalidTypeException("invalid_schema_description")

        schema = {}
        for key, val in description.items():
            if "type" not in val or val["type"] not in {**Types.type_registry, **Types.deprecated_type_registry}:
                raise InvalidTypeException("invalid_schema_field_type")
            
            if val["type"] in Types.deprecated_type_registry:
                # These types are deprecated and will be removed in the future
                continue

            schema[key] = Types.type_registry[val["type"]]()
            kwargs = copy.copy(val)
            del kwargs["type"]
            schema[key].define(**kwargs)

            if kwargs.get("required", True) is False:
                setattr(schema[key], "required", False)

        return schema

    @staticmethod
    def to_list():
        t_list = []
        type_dict = Types.type_registry

        for key in type_dict:
            t_list.append(key)

        return t_list
