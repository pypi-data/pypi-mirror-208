import os
from typing import Optional

from dotenv import load_dotenv

from alvin_cli.config.loader import load_cfg_file
from alvin_cli.schemas.models import CamelBaseModel


class Settings(CamelBaseModel):
    alvin_api_host: str
    alvin_ui_host: str
    alvin_api_token: str
    git_compare_branch: Optional[str] = "main"
    alvin_platform_id: Optional[str]
    dbt_root_dir: Optional[str]
    root_dir: Optional[str]
    dbt_profiles_dir: Optional[str] = "."
    dbt_target: Optional[str] = None
    dialect: Optional[str]
    debug: Optional[bool] = True
    alvin_verbose_log: Optional[bool] = False
    dbt_force_compile: Optional[bool] = False
    dbt_run_deps: Optional[bool] = False

    def __init__(self) -> None:

        cfg_file = load_cfg_file()

        if not cfg_file:
            load_dotenv(f"{os.getcwd()}/.env")
            kwargs = {
                "alvin_api_host": os.getenv("ALVIN_API_HOST")
                if "ALVIN_API_HOST" in os.environ
                else "https://app.alvin.ai",
                "alvin_ui_host": os.getenv("ALVIN_UI_HOST")
                if "ALVIN_UI_HOST" in os.environ
                else "https://app.alvin.ai",
                "alvin_api_token": os.getenv("ALVIN_API_TOKEN")
                if "ALVIN_API_TOKEN" in os.environ
                else "",
                "alvin_platform_id": os.getenv("ALVIN_PLATFORM_ID")
                if "ALVIN_PLATFORM_ID" in os.environ
                else "",
                "git_compare_branch": "main",
                "dbt_root_dir": os.getenv("DBT_ROOT_DIR")
                if "DBT_ROOT_DIR" in os.environ
                else "",
                "dbt_target": os.getenv("DBT_TARGET")
                if "DBT_TARGET" in os.environ
                else "",
                "root_dir": os.getenv("ROOT_DIR") if "ROOT_DIR" in os.environ else "",
                "dbt_profiles_dir": os.getenv("DBT_PROFILES_DIR")
                if "DBT_PROFILES_DIR" in os.environ
                else ".",
                "dialect": os.getenv("DIALECT") if "DIALECT" in os.environ else "ansi",
                "debug": True,
                "alvin_verbose_log": os.getenv("ALVIN_VERBOSE_LOG")
                if "ALVIN_VERBOSE_LOG" in os.environ
                else False,
                "dbt_force_compile": os.getenv("DBT_FORCE_COMPILE")
                if "DBT_FORCE_COMPILE" in os.environ
                else False,
                "dbt_run_deps": os.getenv("DBT_RUN_DEPS")
                if "DBT_RUN_DEPS" in os.environ
                else False,
            }
        else:
            kwargs = cfg_file
        super(Settings, self).__init__(**kwargs)
