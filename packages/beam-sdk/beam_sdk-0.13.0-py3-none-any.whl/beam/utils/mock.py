import os
import importlib
import traceback
import importlib
import json

from http import HTTPStatus
from beam.app import App
from beam.types import Types, InvalidPayloadException, InvalidTypeException


class MockAPI:
    """
    Arguments:
        handler: specify what method in which file to use as the entry point
        loader:
    """

    def __init__(self, app: App) -> None:

        self.app = app
        self._load_trigger()
        self._load_handler()

        if self.loader is not None and self.loader != "":
            self.loader_output = self._run_loader()

    def _load_trigger(self) -> None:
        self.trigger = self.app.Trigger.get_trigger().validate_and_dump()
        self.handler = self.trigger.get("handler", None)
        self.loader = self.trigger.get("loader")
        self.loader_output = None

    # Run loader
    def _run_loader(self):
        module_file, func = self.loader.split(":")
        module = os.path.splitext(module_file)[0]

        try:
            loader_module = importlib.import_module(module)
            self.loader_method = getattr(loader_module, func)
            return self.loader_method()
        except BaseException:
            raise Exception(f"Unable to run loader: {traceback.format_exc()}")

    # Load handler method
    def _load_handler(self) -> None:
        inputs = self.trigger.get("inputs", None)

        if inputs is not None:
            self.inputs = Types.load_schema(inputs)
        else:
            self.inputs = {}

        outputs = self.trigger.get("outputs", None)
        if outputs is not None:
            self.outputs = Types.load_schema(outputs)

        module_file, func = self.handler.split(":")
        module = os.path.splitext(module_file)[0]

        try:
            # instantiate handler and inputs / outputs
            handler_module = importlib.import_module(module)
            self.handler_method = getattr(handler_module, func)
        except BaseException:
            raise Exception("Unable to load handler")

    def call(self, **_input):
        deserialization_errors = []
        deserialized_payload = {}
        serialized_output = {}

        # serialize and validate inputs
        try:
            deserialized_payload = Types.deserialize(_input, self.inputs)
        except (InvalidPayloadException, InvalidTypeException) as exc:
            deserialization_errors = exc.errors

        if deserialization_errors:
            return {"errors": deserialization_errors}, HTTPStatus.BAD_REQUEST

        # If the user ran a loader prior to starting the api, pass in the object they returned
        if self.loader_output is not None:
            deserialized_payload["loader_output"] = self.loader_output

        try:
            output = self.handler_method(**deserialized_payload)
        except BaseException:
            return {
                "errors": [traceback.format_exc()]
            }, HTTPStatus.INTERNAL_SERVER_ERROR

        # serialize and validate outputs
        try:
            serialized_output = Types.serialize(output, self.outputs)
        except (
            InvalidPayloadException,
            InvalidTypeException,
            BaseException,
        ) as exc:
            serialization_errors = getattr(exc, "errors", [])
            return {"errors": serialization_errors}, HTTPStatus.INTERNAL_SERVER_ERROR

        return serialized_output, HTTPStatus.OK