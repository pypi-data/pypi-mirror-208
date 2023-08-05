import json
import beam
import pytest

from beam.types import PythonVersion
from beam.utils.parse import compose_cpu, compose_memory
from beam.exceptions import BeamSerializationError


def valid_reconstruction(app: beam.App):
    dumped_app = app.dumps()
    dumped_json = json.dumps(dumped_app)
    app_from_dumped_config = beam.App.from_config(json.loads(dumped_json))
    return app_from_dumped_config.dumps() == dumped_app


def test_basic_app_reconstruction():
    app = beam.App(
        name="some_app",
        cpu="4000m",
        memory="128mi",
        gpu=1,
        python_packages=["pytorch"],
        python_version=PythonVersion.Python37,
        workspace="./some_folder",
    )

    assert valid_reconstruction(app)


REQUIREMENTS_FILE_CONTENT = """

torch
numpy==1.19.5

scikit-learn

"""


def test_python_packages_from_requirements_file(tmp_path):
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(REQUIREMENTS_FILE_CONTENT)
    assert requirements_path.read_text() == REQUIREMENTS_FILE_CONTENT

    app = beam.App(
        name="some_app",
        cpu="4000m",
        memory="128mi",
        gpu=1,
        python_packages=str(requirements_path),
        python_version=PythonVersion.Python37,
        workspace="./some_folder",
    )

    assert len(app.Spec.python_packages) == 3
    assert ["torch", "numpy==1.19.5", "scikit-learn"] == app.Spec.python_packages

    assert valid_reconstruction(app)


def test_valid_schedule_expressions():
    app1 = beam.App(
        name="some_app",
        cpu=1,
        memory="128mi",
        gpu=1,
    )

    app1.Trigger.Schedule(
        when="* * * * *",
        handler="method.py:run",
    )

    assert valid_reconstruction(app1)

    app1 = beam.App(
        name="some_app",
        cpu=1,
        memory="128mi",
        gpu=1,
    )

    app1.Trigger.Schedule(
        when="every 5m",
        handler="method.py:run",
    )

    assert valid_reconstruction(app1)

    app2 = beam.App(
        name="some_app",
        cpu=1,
        memory="128mi",
        gpu=1,
    )

    app2.Trigger.Schedule(
        when="every",
        handler="method.py:run",
    )

    with pytest.raises(BeamSerializationError):
        valid_reconstruction(app2)


def test_multiple_triggers_should_fail_build():
    app = beam.App(
        name="some_app",
        cpu=1,
        memory="128mi",
        gpu=1,
    )

    app.Trigger.Schedule(
        when="* * * * *",
        handler="test.py:app",
    )

    with pytest.raises(ValueError):
        app.Trigger.Webhook(
            inputs={
                "some_input": beam.Types.String(),
            },
            handler="test.py:app",
        )


def test_compose_cpu():
    assert compose_cpu(1) == "1000m"
    assert compose_cpu(1.999) == "1999m"
    assert compose_cpu("1000m") == "1000m"


def test_compose_memory():
    assert compose_memory("10gi") == "10Gi"
    assert compose_memory("10 gi ") == "10Gi"
    assert compose_memory("10 Gi ") == "10Gi"

    # Raises if Gi is > 256
    with pytest.raises(ValueError):
        compose_memory("10000Gi")

    assert compose_memory("256mi") == "256Mi"
    assert compose_memory("256 mi ") == "256Mi"
    assert compose_memory("256 Mi ") == "256Mi"

    # Raises if Mi is < 128 or >= 1000
    with pytest.raises(ValueError):
        compose_memory("127Mi")

    with pytest.raises(ValueError):
        compose_memory("1000Mi")

    # Test invalid formats
    with pytest.raises(ValueError):
        compose_memory("1000ti")

    with pytest.raises(ValueError):
        compose_memory("1000.0")

    with pytest.raises(ValueError):
        compose_memory("1000")

    with pytest.raises(ValueError):
        compose_memory("2 gigabytes")


def test_cpu_in_app_config():
    config = {"name": "some_app", "memory": "128mi"}

    app1 = beam.App(
        **config,
        cpu=4,
    )

    app2 = beam.App(
        **config,
        cpu="4000m",
    )

    assert valid_reconstruction(app1)
    assert valid_reconstruction(app2)
    assert app1.dumps() == app2.dumps()

    app3 = beam.App(
        **config,
        cpu=1,
    )

    app4 = beam.App(**config, cpu="1000m")

    assert valid_reconstruction(app3)
    assert valid_reconstruction(app4)
    assert app3.dumps() == app4.dumps()
