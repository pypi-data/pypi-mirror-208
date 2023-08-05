import argparse
import os.path
from typing import List
from typing import Optional
from typing import Sequence

from alvin_cli.config import settings
from alvin_cli.utils.utils_dbt import ERROR_RETURN_CODE
from alvin_cli.utils.utils_dbt import SUCCESS_RETURN_CODE
from alvin_cli.utils.utils_dbt import add_dbt_cmd_args
from alvin_cli.utils.utils_dbt import add_dbt_cmd_model_args
from alvin_cli.utils.utils_dbt import add_filenames_args
from alvin_cli.utils.utils_dbt import get_flags
from alvin_cli.utils.utils_dbt import run_dbt_cmd


def prepare_cmd(
    global_flags: Optional[Sequence[str]] = None,
    cmd_flags: Optional[Sequence[str]] = None,
    models: Optional[Sequence[str]] = None,
) -> Optional[List[Optional[str]]]:
    global_flags = get_flags(global_flags)
    cmd_flags = get_flags(cmd_flags)

    dbt_target = settings.dbt_target
    dbt_profiles_dir = settings.dbt_profiles_dir

    cmd = None

    try:
        if dbt_target:
            if models:
                dbt_models = models
                cmd = [
                    "dbt",
                    *global_flags,
                    "compile",
                    "-m",
                    *dbt_models,
                    *cmd_flags,
                    "--target",
                    dbt_target,
                    "--profiles-dir",
                    dbt_profiles_dir,
                ]

            else:
                cmd = [
                    "dbt",
                    *global_flags,
                    "compile",
                    *cmd_flags,
                    "--target",
                    dbt_target,
                    "--profiles-dir",
                    dbt_profiles_dir,
                ]

        else:
            if models:
                dbt_models = models
                cmd = [
                    "dbt",
                    *global_flags,
                    "compile",
                    "-m",
                    *dbt_models,
                    *cmd_flags,
                    "--profiles-dir",
                    dbt_profiles_dir,
                ]
            else:
                cmd = [
                    "dbt",
                    *global_flags,
                    "compile",
                    *cmd_flags,
                    "--profiles-dir",
                    dbt_profiles_dir,
                ]

    except Exception as e:
        if settings.alvin_verbose_log:
            print(f"DEBUG!!! dbt target : {dbt_target}")
            print(f"DEBUG!!! dbt profile dir : {dbt_profiles_dir}")
            print(f"Exception raised is: {e}")

    return cmd


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    add_filenames_args(parser)
    add_dbt_cmd_args(parser)
    add_dbt_cmd_model_args(parser)

    return_code = SUCCESS_RETURN_CODE

    if not settings.dbt_force_compile:
        if os.path.exists("target/manifest.json"):
            print("manifest.json compiled already, using it!")
            return return_code
        else:
            print("manifest.json does not exist, creating a new one!")
    else:
        print("updating manifest.json file, by running dbt compile")

    args = parser.parse_args(argv)

    if not settings.dbt_profiles_dir:
        print("env var DBT_PROFILES_DIR must be set!")
        return ERROR_RETURN_CODE

    cmd = prepare_cmd(
        args.global_flags,
        args.cmd_flags,
        args.models,
    )
    if cmd:
        return_code = run_dbt_cmd(cmd)

    return return_code


if __name__ == "__main__":
    exit(main())
