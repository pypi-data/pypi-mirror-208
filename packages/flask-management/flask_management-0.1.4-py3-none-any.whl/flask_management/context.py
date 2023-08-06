import subprocess
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, root_validator

from flask_management.constants import PythonVersion


class ProjectContext(BaseModel):
    name: str
    folder_name: Optional[str]
    app_name: Optional[str]

    username: Optional[str] = None
    email: Optional[EmailStr] = None

    python: PythonVersion
    year: Optional[int]

    @root_validator(pre=True)
    def validate_project(cls, values: dict):
        try:
            values["username"] = subprocess.check_output(
                ["git", "config", "--get", "user.name"]
            )
            values["email"] = subprocess.check_output(
                ["git", "config", "--get", "user.email"]
            )
        except subprocess.CalledProcessError:
            ...
        values["folder_name"] = values["name"].lower().replace(" ", "-").strip()
        values["year"] = datetime.today().year
        values["app_name"] = values["folder_name"].replace("-", "_").strip()
        return values

    class Config:
        use_enum_values = True
