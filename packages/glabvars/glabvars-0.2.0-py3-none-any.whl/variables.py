from pydantic import BaseModel


class GLVariable(BaseModel):
    """Gitlab CI variable"""

    key: str
    value: str
    protected: bool
    variable_type: str = "env_var"
    masked: bool
    raw: bool
    environment_scope: str

    @property
    def gcl_type(self):
        """Type string to be used in YAML config"""
        return "variable" if self.variable_type == "env_var" else "file"


class GCLVariable(BaseModel):
    """Gitlab-CI-Local variable"""

    type: str
    values: dict[str, str]


class GLGroup(BaseModel):
    """Gitlab group"""

    id: int
    full_path: str
