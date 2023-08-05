import beam
from beam.utils.mock import MockAPI


def test_valid_inputs():
    app = beam.App(
        name="some_app",
        cpu=1,
        memory="128mi",
    )

    schema = {
        "input1": beam.Types.String(),
        "input2": beam.Types.Float(),
        "input4": beam.Types.Boolean(),
        "input5": beam.Types.Json(),
    }

    app.Trigger.RestAPI(
        inputs=schema,
        outputs=schema,
        handler="method.py:run",
    )

    mock = MockAPI(app)
    input_output = {
        "input1": "hello world",
        "input2": 1.0,
        "input4": True,
        "input5": {"hello": "world"},
    }

    output, status = mock.call(**input_output)

    assert output == input_output
    assert status == 200


def test_invalid_inputs():
    app = beam.App(
        name="some_app",
        cpu=1,
        memory="128mi",
    )

    schema = {
        "input1": beam.Types.Float(),
        "input2": beam.Types.Boolean(),
        "input3": beam.Types.Json(),
    }

    app.Trigger.RestAPI(
        inputs=schema,
        outputs=schema,
        handler="method.py:run",
    )

    mock = MockAPI(app)
    input_output = {
        "input1": "Not a float",
        "input2": "Not a boolean",
        "input3": "Not a json",
    }

    output, status = mock.call(**input_output)

    assert output == {
        "errors": [
            "input1:invalid_float_value",
            "input2:invalid_boolean_value",
            "input3:invalid_json_str",
        ]
    }
    assert status == 400

    input_output["input1"] = 1.0
    input_output["input2"] = True
    input_output["input3"] = {"hello": "world"}

    output, status = mock.call(**input_output)

    assert output == input_output
    assert status == 200


def test_valid_loader():
    app = beam.App(
        name="some_app",
        cpu=1,
        memory="128mi",
    )

    schema = {
        "input1": beam.Types.Float(),
        "input2": beam.Types.Boolean(),
        "input3": beam.Types.Json(),
    }

    app.Trigger.RestAPI(
        inputs=schema,
        outputs=schema,
        handler="method.py:run",
        loader="method.py:load",
    )

    input_output = {
        "input1": 1.0,
        "input2": True,
        "input3": {"hello": "world"},
    }

    mock = MockAPI(app)
    output, status = mock.call(**input_output)

    assert mock.loader_output == {"loader_output": "hello world"}
    assert output == input_output
    assert status == 200
