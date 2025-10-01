"""
This is temporary code to get the WIP metrics for the team.
"""
import json
from typing import List
import pandas as pd
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import github3
import requests
from bs4 import BeautifulSoup

# TODO: implement a function to get all statuses.
def get_status_events(
    issue: github3.issues.Issue, log_file: str = "status_events.log"  # type: ignore
) -> List[dict[str, str | datetime]]:  # type: ignore
    """
    Get the status events for a given issue if the status is of interest.

    Args:
        issue (github3.issues.Issue): A GitHub issue.

    """
    in_progress = "In progress"
    status_events = []
    print(f"Getting source content for {issue.issue.title}...\n")

    html_content = requests.get(issue.issue.html_url)._content
    soup = BeautifulSoup(html_content, "html.parser")
    script_tag = soup.find(
        "script",
        {"type": "application/json", "data-target": "react-app.embeddedData"},
    )
    json_data = {}
    out_data = {
        "issue_url": issue.issue.html_url,
        "assignee": [],
    }
    if script_tag:
        json_data = json.loads(script_tag.string)

    if json_data:
        for edge in json_data["payload"]["preloadedQueries"][0]["result"]["data"]["repository"]["issue"]["frontTimelineItems"]["edges"]:
            node = edge["node"]

            if "status" in node:

                # Handle moved out
                if node.get("previousStatus") and node["previousStatus"] in in_progress:
                    created_at = datetime.strptime(node["createdAt"], "%Y-%m-%dT%H:%M:%SZ").replace(
                        tzinfo=timezone.utc
                    )
                    status_events.append(
                        {"createdAt": created_at, "event": "unstatused", "statusName": node["previousStatus"]}
                    )
                    out_data[f"moved out to {node['status']}"] = str(created_at)

                # Handle moved in
                if node["status"] in in_progress:
                    created_at = datetime.strptime(node["createdAt"], "%Y-%m-%dT%H:%M:%SZ").replace(
                        tzinfo=timezone.utc
                    )
                    status_events.append(
                        {"createdAt": created_at, "event": "statused", "statusName": node["status"]}
                    )
                    out_data[f"moved in to {node['status']}"] = str(created_at)

            elif "assignee" in node:
                out_data["assignee"].append(node["assignee"]["login"])

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(out_data) + "\n")

    return out_data

INPUT_FILE = "status_events.log" 
OUTPUT_FILE = "out/wip.csv"

def load_issues(filename):
    issues = []
    with open(filename, "r") as f:
        for line in f:
            if line.strip():
                issues.append(json.loads(line))
    return issues

def week_start(date: datetime) -> datetime:
    """Return the Monday of the week for a given datetime (UTC-aware)."""
    monday = date - timedelta(days=date.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

def expand_intervals(issues):
    """Expand issue intervals into weekly buckets per assignee."""
    weekly_counts = defaultdict(lambda: defaultdict(int))

    for issue in issues:
        assignees = issue.get("assignee", [])
        start_str = issue.get("moved in to In progress")
        end_str = None

        # choose the earliest "moved out ..." field as end if exists
        out_keys = [k for k in issue.keys() if k.startswith("moved out")]
        if out_keys:
            end_str = min(issue[k] for k in out_keys)

        if not start_str:
            continue

        start = datetime.fromisoformat(start_str).astimezone(timezone.utc)
        end = datetime.fromisoformat(end_str).astimezone(timezone.utc) if end_str else datetime.now(timezone.utc)

        current = week_start(start)
        while current <= end:
            for assignee in assignees:
                weekly_counts[current][assignee] += 1
            current += timedelta(weeks=1)

    return weekly_counts


def main():
    issues = load_issues(INPUT_FILE)
    weekly_counts = expand_intervals(issues)

    # collect all assignees
    assignees = sorted({a for counts in weekly_counts.values() for a in counts})

    # create dataframe
    rows = []
    for week, counts in sorted(weekly_counts.items()):
        row = {"week start": week.strftime("%Y-%m-%d")}
        for assignee in assignees:
            row[assignee] = counts.get(assignee, 0)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved weekly data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
