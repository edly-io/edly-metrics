## Edly Metrics

Modular, plugin-style metrics collection framework for engineering teams. Add Python collectors for different metric types (release success, lead time, PR throughput, etc.) and run them via a unified CLI. Supports data sources such as GitLab, GitHub, and Azure DevOps.

### Quick start

1) Install dependencies
```
pip install -r requirements.txt
```

2) Set environment variables (example for GitLab)
```
export GITLAB_TOKEN=... 
export GITLAB_URL=https://git.overhang.io/api/v4
```

3) Run the CLI
```
python metrics_cli.py list
python metrics_cli.py run release_success --date-from 2024-01-01 --date-to 2024-12-31 --output ./files/release_success.csv
```

### Project layout

```
  src/
  __init__.py
  base.py                # Collector interface
  registry.py            # Collector registry and discovery
  config.py              # Config models and loader
  datasources/
    __init__.py
    gitlab.py            # GitLab client wrapper
    github.py            # GitHub client stub
    azure_devops.py      # Azure DevOps client stub
  collectors/
    __init__.py
    release_success.py   # generates release success/failure rate
metrics_cli.py           # Typer-based CLI entry
```

### Adding a new collector

1) Create a new file under `src/collectors/your_collector.py` implementing `Collector`.

2) Register it by calling `registry.register_collector("your_name", YourCollector)`. If you follow the pattern inside `collectors/__init__.py`, import your module there so it self-registers on import.

3) Run it via CLI: `python metrics_cli.py run your_name --output ./files/out.csv`

### Configuration

You can pass CLI flags directly or provide a YAML file with per-collector settings. Use `gitlab_base_url` for GitLab endpoint. Env vars (like tokens) are supported via `python-dotenv` and your shell environment.

### Excel template

If you export to a `.xlsx` file, the framework will use `pandas` and `openpyxl` to write to Excel, which you can paste into your annual review template.


