import typer

from flask_management.constants import PythonVersion
from flask_management.context import ProjectContext
from flask_management.generator import generate_project

app = typer.Typer(
    add_completion=False,
    help="Managing flask projects made easy!",
    name="Manage Flask",
)


@app.command(help="Creates a flask project.")
def startproject(
    name: str,
    python: PythonVersion = typer.Option(PythonVersion.THREE_DOT_EIG),
):
    context = ProjectContext(
        name=name,
        python=python
    )
    generate_project(context)
