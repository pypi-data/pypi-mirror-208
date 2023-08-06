from pydantic import BaseModel


class IntegrationConfig(BaseModel):
    iks_host: str
    iks_port: int
    iks_operator_login: str
    iks_operator_password: str
    log: list[str]  # debug, info, warning, critical