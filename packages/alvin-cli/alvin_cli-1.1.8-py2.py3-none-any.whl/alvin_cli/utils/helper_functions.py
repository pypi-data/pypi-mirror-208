import json
import random
import re
import time
from pathlib import Path
from typing import Optional
from typing import Sequence
from typing import Tuple

import pandas as pd
import ruamel.yaml
import typer
import yaml
from alvin_api_client.model.impact_analysis_node_list_response import (
    ImpactAnalysisNodeListResponse,
)
from rich.console import Console
from rich.table import Table

from alvin_cli.config import settings
from alvin_cli.schemas.models import ReportStats
from alvin_cli.utils.common_arguments import BRIGHT_BLUE_COLOR_TYPER
from alvin_cli.utils.common_arguments import BRIGHT_CYAN_COLOR_TYPER
from alvin_cli.utils.common_arguments import BRIGHT_GREEN_COLOR_TYPER
from alvin_cli.utils.common_arguments import BRIGHT_MAGENTA_COLOR_TYPER
from alvin_cli.utils.common_arguments import BRIGHT_RED_COLOR_TYPER
from alvin_cli.utils.common_arguments import BRIGHT_YELLOW_COLOR_TYPER

console = Console()


def __create_entity_url(
    entity_id: str, entity_platform_id: str, entity_type: str
) -> str:
    entity_url = f"{settings.alvin_ui_host}/entity/{entity_platform_id}/{entity_type}/{entity_id}"
    return entity_url


def typer_progress_bar() -> None:
    with typer.progressbar(range(100)) as progress:
        for i in range(4):
            time.sleep(0.1)
            progress.update(25)


def extract_dict(s: str) -> list:
    """Extract all valid dicts from the string."""
    results = []
    s_ = " ".join(s.split("\n")).strip()
    exp = re.compile(r"(\{.*?\})")
    for i in exp.findall(s_):
        try:
            results.append(json.loads(i))
        except json.JSONDecodeError:
            pass
    return results


def handle_api_exception(body: str, status: str) -> None:
    """Handles pretty-printing of default backend ApiException"""

    details = []
    try:
        api_details = json.loads(body).get("detail", [])
        for err in api_details:
            msg = err.get("msg", "<No msg>")
            loc = err.get("loc", [])
            loc = list(filter(lambda x: len(str(x)) > 0, loc))
            if len(loc) > 0:
                loc = ".".join([str(_loc) for _loc in loc])
                msg = f"{msg}: {loc}"
            details.append(msg)
    except json.decoder.JSONDecodeError:
        details.append("Internal Server Error")
    if len(details) == 0:
        details.append("Internal Server Error")

    console.print(f"[bold yellow]Status:[/bold yellow] [bold red]{status}[/bold red]")
    errors = "\n".join(details)
    errors = f"\n{errors}"
    console.print(
        f"[bold blue]Error details:[/bold blue] {errors}",
        style="bold red",
    )


def handle_print_exception(detail: Sequence, status_code: str) -> None:
    """Print status code and error message for the raised exception"""

    console.print(
        f"[bold yellow]The status code returned is \U0001f928 :[/bold yellow] [bold red]{status_code.replace('(', '').replace(')', '')}[/bold red]"
    )
    console.print(
        f"[bold blue]The connection has failed with the following details \U0001f631 :[/bold blue] {detail[0]}",
        style="bold red",
    )


def print_output_format(
    data: Sequence[dict],
    table_title: str,
    output: str,
    save_to_file: bool,
    file_name: str,
) -> None:
    """Deliver the command output in user chosen format
    and save file is needed. The input expected is a list of dictionaries"""

    if len(data):

        if output == "table":
            colors = [
                "cyan",
                "magenta",
                "purple",
                "#FF7F50",
                "white",
                "yellow",
                "#D2691E",
                "#698B69",
                "#79CDCD",
                "#8B814C",
                "#8B8B00",
            ]
            table = Table(expand=True, title=table_title, show_edge=True)

            for column_name in data[0].keys():
                table.add_column(
                    column_name,
                    justify="center",
                    no_wrap=True,
                    max_width=15,
                    style=colors[random.randint(0, len(colors) - 1)],
                )

            for row_data in data:
                table.add_row(*(row_data.values()), end_section=True)

            console.print(table)

            if save_to_file:
                pd.DataFrame(data).to_csv(file_name + ".csv", index=False)
                typer.echo("Saved CSV in current directory")

        elif output == "yaml":
            typer.echo("Data In YAML Format")
            yaml_data = yaml.dump(data, sort_keys=False)
            typer.echo(yaml_data)

            if save_to_file:
                with open(file_name + ".yaml", "w") as f:
                    yaml_file_dump = ruamel.yaml.YAML()
                    yaml_file_dump.indent(sequence=4, offset=2)
                    yaml_file_dump.dump(data, f)
                typer.echo("Saved YAML file in current directory")

        else:
            typer.echo("Data In JSON Format")
            typer.echo(json.dumps(data))

            if save_to_file:
                with open(file_name + ".json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                typer.echo("Saved JSON file in current directory")
    else:
        typer.secho(
            "No data returned, check the entity has data!",
            fg=BRIGHT_MAGENTA_COLOR_TYPER,
        )


def format_response_data(
    fields_to_print: Sequence[str], response_data: Sequence[dict]
) -> list:
    """Generic Function to format and structure data for the print format function"""
    formatted_data_list = []

    for data in response_data:
        formatted_data_dict = {}  # type: ignore
        for field in fields_to_print:
            if field == "entity_link_to_alvin":

                formatted_data_dict[field] = __create_entity_url(
                    entity_id=str(formatted_data_dict.get("id")),
                    entity_platform_id=str(formatted_data_dict.get("platform_id")),
                    entity_type=str(formatted_data_dict.get("entity_type")),
                )
            else:
                formatted_data_dict[field] = str(data.get(field, None))

        formatted_data_list.append(formatted_data_dict)

    return formatted_data_list


def structure_lineage_node_data(
    lineage_node_data: Sequence[dict],
) -> list:
    """Format the Lineage Node Data"""

    node_data_in_list = []
    for data in lineage_node_data:
        entity_data = data["entity_id"]
        entity_id = entity_data["entity_id"]
        entity_name = entity_id.split(".")[-1]
        entity_type = str(entity_data["entity_type"])
        node_data_in_dict = {
            "entityName": entity_name,
            "entityId": entity_id,
            "entityType": entity_type,
        }

        node_data_in_list.append(node_data_in_dict)

    return node_data_in_list


def structure_data_usage_stats(
    usage_data: dict,
) -> Tuple[list, list]:
    """Format the Usage Data"""

    console.print(
        f'[bold blue]Entity Name:[/bold blue] [bold yellow]  {usage_data["entity"]["name"]} [/bold yellow] [bold blue] with start timestamp [/bold blue] [bold yellow] {str(usage_data["start_timestamp"])} [/bold yellow] [bold blue] and end timestamp [/bold blue] [bold yellow] {str(usage_data["end_timestamp"] )}[/bold yellow] '
    )

    user_name_stats = []

    for user_stats in usage_data["user_name_stats"]:
        user_name_stats_dict = {
            "userName": user_stats["user_name"],
            "usageCount": str(user_stats["usage_count"]),
        }
        user_name_stats.append(user_name_stats_dict)

    usage_stats_in_list = []
    usage_stats = usage_data["usage_stats"]

    for data in usage_stats:
        usage_date = str(data["used_date"])
        usage_count = str(data["usage_count"])
        if data["facets"]:
            facet_data = data["facets"]["usage_classification"]
            facet_usage_read = str(facet_data["READ"])
            facet_usage_write = str(facet_data["WRITE"])
        else:
            facet_usage_read = str(0)
            facet_usage_write = str(0)

        usage_stats_in_dict = {
            "usageDate": usage_date,
            "usageCount": usage_count,
            "usageRead": facet_usage_read,
            "usageWrite": facet_usage_write,
        }

        usage_stats_in_list.append(usage_stats_in_dict)

    return usage_stats_in_list, user_name_stats


def print_node_stats_impact_analysis(
    impact_analysis_data: ImpactAnalysisNodeListResponse,
) -> Optional[ReportStats]:

    node_stats = impact_analysis_data.node_stats
    if not node_stats:
        return None

    impact_per_platform = node_stats.impact_per_platform
    impacted_users = node_stats.impacted_users

    total_impacted_users = 0
    if impacted_users:
        total_impacted_users = len(impacted_users)

    total_impacted_assets = 0
    if node_stats.entity_types:
        total_impacted_assets = sum(node_stats.entity_types.values())

    typer.secho(
        "\n------------ Summary of Impacted Entities ------------\n",
        fg=BRIGHT_GREEN_COLOR_TYPER,
    )

    typer.secho(
        f"{total_impacted_assets} assets and {total_impacted_users} people impacted",
        fg=BRIGHT_YELLOW_COLOR_TYPER,
    )

    if node_stats.entity_types:
        typer.secho(
            f'   Impacted Number of Columns : {node_stats.entity_types.get("COLUMN", 0)}',
            fg=BRIGHT_CYAN_COLOR_TYPER,
        )
        typer.secho(
            f'   Impacted Number of Tables : {node_stats.entity_types.get("TABLE", 0)}',
            fg=BRIGHT_YELLOW_COLOR_TYPER,
        )

    if node_stats.impact_status:
        typer.secho(
            f'   Impact Status Direct :  {node_stats.impact_status.get("DIRECT", 0)}',
            fg=BRIGHT_MAGENTA_COLOR_TYPER,
        )
        typer.secho(
            f'   Impact Status Breaking Change : {node_stats.impact_status.get("BREAKING", 0)}',
            fg=BRIGHT_MAGENTA_COLOR_TYPER,
        )
        typer.secho(
            f'   Impact Status Stale : {node_stats.impact_status.get("STALE", 0)}',
            fg=BRIGHT_MAGENTA_COLOR_TYPER,
        )

    if impacted_users:
        typer.secho(
            "   Impacted Users :",
            fg=BRIGHT_CYAN_COLOR_TYPER,
        )
        for user, count in impacted_users.items():
            typer.secho(
                f"       {user} with usage count {count}",
                fg=BRIGHT_BLUE_COLOR_TYPER,
            )

    typer.secho(
        "\n------------ Impact Per Platform Id ------------\n",
        fg=BRIGHT_GREEN_COLOR_TYPER,
    )

    if impact_per_platform:
        for platform, impact in impact_per_platform.items():
            typer.secho(f"{platform}", fg=BRIGHT_YELLOW_COLOR_TYPER)
            for impact_status, count in impact.items():
                typer.secho(f"   {impact_status} : {count}", fg=BRIGHT_BLUE_COLOR_TYPER)

    return ReportStats(
        impact_per_platform=impact_per_platform,
        impacted_users=impacted_users,
        total_impacted_assets=total_impacted_assets,
        total_impacted_users=total_impacted_users,
    )


def structure_impact_analysis_data(
    impact_analysis_data: ImpactAnalysisNodeListResponse,
) -> list:
    """Format the Impact Analysis Data, returns list of dicts"""

    structured_data_list = []
    impact_analysis_response = impact_analysis_data.impact_analysis_response
    query_entities = impact_analysis_response.query_entities

    if query_entities:
        for impacted_entity in query_entities:
            structured_data_dict = {
                "entityType": str(impacted_entity.entityType),
                "entityId": impacted_entity.entityId,
            }
            structured_data_list.append(structured_data_dict)

    return structured_data_list


def read_config_from_json(config: Path) -> Optional[dict]:
    if config is None:
        typer.secho("No config file", fg=BRIGHT_RED_COLOR_TYPER)
        raise typer.Abort()
    if config.is_file():
        text = config.read_text()
        try:
            json_data = json.loads(text)
            return json_data
        except ValueError:
            typer.secho(
                "Not valid config file, make sure the data is in correct JSON format",
                fg=BRIGHT_RED_COLOR_TYPER,
            )
            raise typer.Abort()

    elif config.is_dir():
        typer.secho(
            "Config is a directory, will use all its config files",
            fg=BRIGHT_BLUE_COLOR_TYPER,
        )
    elif not config.exists():
        typer.secho("The config doesn't exist", fg=BRIGHT_MAGENTA_COLOR_TYPER)
    raise typer.Abort()


def typer_secho_raise(text: str, color: str) -> None:
    if color == "CYAN":
        c = BRIGHT_CYAN_COLOR_TYPER

    elif color == "MAGENTA":
        c = BRIGHT_MAGENTA_COLOR_TYPER

    elif color == "RED":
        c = BRIGHT_RED_COLOR_TYPER

    elif color == "BLUE":
        c = BRIGHT_BLUE_COLOR_TYPER

    elif color == "GREEN":
        c = BRIGHT_GREEN_COLOR_TYPER

    typer.secho(
        text,
        fg=c,
    )
