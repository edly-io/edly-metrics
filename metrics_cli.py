#!/usr/bin/env python3
from typing import Optional

import typer

from src.registry import registry
from src.config import AppConfig, load_config

app = typer.Typer(help="Edly Metrics - run plugin collectors for engineering metrics")


@app.command(name="list")
def list_collectors():
    """List available collectors."""
    names = registry.list_collectors()
    for name in names:
        typer.echo(name)


@app.command()
def run(
    name: str = typer.Argument(..., help="Collector name, e.g., release_success"),
    output: str = typer.Option("./files/out.csv", help="Output file path (.csv or .xlsx)"),
    config: Optional[str] = typer.Option("./config.example.yml", help="Path to YAML/JSON config file"),
    date_from: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
    date_to: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
    gitlab_base_url: Optional[str] = typer.Option(None, help="Override GitLab API base URL"),
):
    """Run a collector and export results."""
    cfg: AppConfig = load_config(config_path=config, overrides={
        "date_from": date_from,
        "date_to": date_to,
        "gitlab_base_url": gitlab_base_url,
        "output": output,
    })

    collector_cls = registry.get_collector(name)
    if collector_cls is None:
        typer.secho(f"Collector not found: {name}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    collector = collector_cls(cfg)
    df = collector.collect()
    collector.export(df, output)
    typer.secho(f"Exported {len(df)} rows to {output}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()


