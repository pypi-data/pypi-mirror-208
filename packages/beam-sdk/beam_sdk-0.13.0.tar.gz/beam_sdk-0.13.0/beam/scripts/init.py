import os
import argparse
import pathlib
import shutil
import jinja2
import random

from .build import build

templates_path = os.path.join(
    pathlib.Path(__file__).parent.parent.resolve(), "templates"
)


def create_template(name: str, **kwargs):
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
    template = environment.get_template("base.jinja")
    rendered_template = template.render(name=name, **kwargs)

    app_path = os.path.join(os.getcwd(), "app.py")

    if os.path.exists(app_path):
        app_path = f"{name}"

        while os.path.exists(f"{app_path}.py"):
            random_int = random.randint(0, 9)
            app_path = f"{app_path}{random_int}"
        
        app_path = os.path.join(os.getcwd(), f"{app_path}.py")

    with open(app_path, "w") as f:
        f.write(rendered_template)

    try:
        os.environ["SKIP_VALIDATION"] = "1"
        build(app_path)
    except BaseException as e:
        os.remove(app_path)
        raise e

    print(f"{app_path.replace(os.getcwd(), '.')}")

def parse_args():
    parser = argparse.ArgumentParser(description="Create a new app")
    parser.add_argument("--name", type=str, help="Name of the app")
    parser.add_argument("--cpu", type=int, help="CPU", default=1)
    parser.add_argument("--memory", type=str, help="Memory", default="2Gi")
    parser.add_argument("--trigger", type=str, help="Trigger")

    return parser.parse_args()


if __name__ == "__main__":
    parsed_args = parse_args()
    create_template(**vars(parsed_args))

    if parsed_args.trigger:
        shutil.copyfile(
            os.path.join(templates_path, "run.py"), os.path.join(os.getcwd(), "run.py")
        )
