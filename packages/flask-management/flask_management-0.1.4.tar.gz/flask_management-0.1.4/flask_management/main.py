import os
from typing import TypeVar

import typer
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter
from pydantic.main import BaseModel

from flask_management.constants import PythonVersion
from flask_management.constants import TEMPLATES_DIR
from flask_management.context import ProjectContext

ContextType = TypeVar("ContextType", bound=BaseModel)
app = typer.Typer(
    add_completion=False,
    help="Managing flask projects made easy!",
    name="Manage Flask",
)


def fill_template(template_name: str, context: ContextType):
    try:
        cookiecutter(
            os.path.join(TEMPLATES_DIR, template_name),
            extra_context=context.dict(),
            no_input=True,
        )
    except OutputDirExistsException:
        typer.echo(f"Folder '{context.folder_name}' already exists. 😞")
    else:
        typer.echo(f"Flask {template_name} created successfully! 🎉")


def generate_project(context: ProjectContext):
    fill_template("project", context)


@app.command(help="Creates a flask project with the given name.")
def startproject(
    name: str,
    python: PythonVersion = typer.Option(PythonVersion.THREE_DOT_EIGHT),
):
    context = ProjectContext(
        name=name,
        python=python
    )
    generate_project(context)
