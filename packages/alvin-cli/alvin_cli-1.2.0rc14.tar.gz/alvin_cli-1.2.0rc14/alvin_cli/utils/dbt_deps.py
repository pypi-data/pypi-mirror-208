from typing import List

from alvin_cli.utils.utils_dbt import SUCCESS_RETURN_CODE
from alvin_cli.utils.utils_dbt import run_dbt_cmd


def prepare_cmd() -> List[str]:
    return ["dbt", "deps"]


def main() -> int:
    return_code = SUCCESS_RETURN_CODE
    cmd = prepare_cmd()

    if cmd:
        return_code = run_dbt_cmd(cmd)

    return return_code


if __name__ == "__main__":
    exit(main())
