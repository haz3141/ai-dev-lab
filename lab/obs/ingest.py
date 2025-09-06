#!/usr/bin/env python3
"""
Audit Log Ingestion and Analysis

Processes JSONL audit logs to compute metrics and generate reports.
"""

import argparse
import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any


class AuditIngester:
    """Processes audit logs and computes metrics."""

    def __init__(self, log_path: str = "logs/"):
        self.log_path = log_path
        self.events = []

    def load_events(self, pattern: str = "*.jsonl") -> list[dict[str, Any]]:
        """Load events from JSONL files matching pattern."""
        events = []

        # Find all matching files
        search_pattern = os.path.join(self.log_path, pattern)
        files = glob.glob(search_pattern)

        if not files:
            print(f"No files found matching pattern: {search_pattern}")
            return events

        print(f"Loading events from {len(files)} files...")

        for file_path in files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            event = json.loads(line)
                            events.append(event)
                        except json.JSONDecodeError as e:
                            print(f"Warning: Invalid JSON in {file_path}:{line_num}: {e}")
                            continue
            except FileNotFoundError:
                print(f"Warning: File not found: {file_path}")
                continue
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

        self.events = events
        print(f"Loaded {len(events)} events")
        return events

    def compute_error_rate(self, tool_name: str | None = None) -> float:
        """Compute error rate for all tools or specific tool."""
        if not self.events:
            return 0.0

        filtered_events = self.events
        if tool_name:
            filtered_events = [e for e in self.events if e.get("tool_name") == tool_name]

        if not filtered_events:
            return 0.0

        error_count = sum(1 for e in filtered_events if e.get("error") is not None)
        total_count = len(filtered_events)

        return (error_count / total_count) * 100 if total_count > 0 else 0.0

    def compute_latency_percentiles(self, tool_name: str | None = None) -> dict[str, float]:
        """Compute latency percentiles (p50, p95, p99)."""
        if not self.events:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        filtered_events = self.events
        if tool_name:
            filtered_events = [e for e in self.events if e.get("tool_name") == tool_name]

        latencies = []
        for event in filtered_events:
            duration_ms = event.get("duration_ms")
            if duration_ms is not None and isinstance(duration_ms, int | float):
                latencies.append(duration_ms)

        if not latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        latencies.sort()
        n = len(latencies)

        return {
            "p50": latencies[int(n * 0.5)],
            "p95": latencies[int(n * 0.95)],
            "p99": latencies[int(n * 0.99)],
        }

    def get_top_failing_tools(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get tools with highest error rates."""
        tool_stats = defaultdict(lambda: {"total": 0, "errors": 0})

        for event in self.events:
            tool_name = event.get("tool_name", "unknown")
            tool_stats[tool_name]["total"] += 1
            if event.get("error") is not None:
                tool_stats[tool_name]["errors"] += 1

        failing_tools = []
        for tool_name, stats in tool_stats.items():
            if stats["total"] > 0:
                error_rate = (stats["errors"] / stats["total"]) * 100
                failing_tools.append(
                    {
                        "tool_name": tool_name,
                        "total_requests": stats["total"],
                        "error_count": stats["errors"],
                        "error_rate": error_rate,
                    }
                )

        # Sort by error rate descending
        failing_tools.sort(key=lambda x: x["error_rate"], reverse=True)
        return failing_tools[:limit]

    def get_request_volume(self, hours: int = 24) -> dict[str, int]:
        """Get request volume by hour for the last N hours."""
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=hours)

        hourly_counts = defaultdict(int)

        for event in self.events:
            try:
                event_time = datetime.fromisoformat(
                    event.get("timestamp", "").replace("Z", "+00:00")
                )
                if event_time >= cutoff:
                    hour_key = event_time.strftime("%Y-%m-%d %H:00")
                    hourly_counts[hour_key] += 1
            except (ValueError, TypeError):
                continue

        return dict(hourly_counts)

    def get_user_activity(self) -> dict[str, Any]:
        """Get user activity statistics."""
        unique_users = set()
        unique_sessions = set()
        user_requests = defaultdict(int)
        session_requests = defaultdict(int)

        for event in self.events:
            user_id = event.get("user_id")
            session_id = event.get("session_id")

            if user_id:
                unique_users.add(user_id)
                user_requests[user_id] += 1

            if session_id:
                unique_sessions.add(session_id)
                session_requests[session_id] += 1

        return {
            "unique_users": len(unique_users),
            "unique_sessions": len(unique_sessions),
            "total_requests": len(self.events),
            "avg_requests_per_user": len(self.events) / len(unique_users) if unique_users else 0,
            "avg_requests_per_session": (
                len(self.events) / len(unique_sessions) if unique_sessions else 0
            ),
        }

    def generate_summary_report(self) -> str:
        """Generate a markdown summary report."""
        if not self.events:
            return "# Audit Log Summary\n\nNo events found.\n"

        # Compute metrics
        overall_error_rate = self.compute_error_rate()
        latency_percentiles = self.compute_latency_percentiles()
        top_failing = self.get_top_failing_tools(5)
        request_volume = self.get_request_volume(24)
        user_activity = self.get_user_activity()

        # Generate report
        report = f"""# Audit Log Summary

**Generated**: {datetime.utcnow().isoformat()}Z
**Total Events**: {len(self.events):,}
**Time Range**: Last 24 hours

## Error Metrics

- **Overall Error Rate**: {overall_error_rate:.2f}%
- **Total Requests**: {len(self.events):,}

## Performance Metrics

- **Latency p50**: {latency_percentiles['p50']:.2f}ms
- **Latency p95**: {latency_percentiles['p95']:.2f}ms
- **Latency p99**: {latency_percentiles['p99']:.2f}ms

## Top Failing Tools

| Tool | Total Requests | Errors | Error Rate |
|------|----------------|--------|------------|
"""

        for tool in top_failing:
            report += (
                f"| {tool['tool_name']} | {tool['total_requests']:,} | "
                f"{tool['error_count']:,} | {tool['error_rate']:.2f}% |\n"
            )

        report += f"""
## User Activity

- **Unique Users**: {user_activity['unique_users']:,}
- **Unique Sessions**: {user_activity['unique_sessions']:,}
- **Avg Requests/User**: {user_activity['avg_requests_per_user']:.1f}
- **Avg Requests/Session**: {user_activity['avg_requests_per_session']:.1f}

## Request Volume (Last 24h)

| Hour | Requests |
|------|----------|
"""

        for hour, count in sorted(request_volume.items()):
            report += f"| {hour} | {count:,} |\n"

        return report

    def save_report(self, output_path: str = "audit_summary.md"):
        """Save summary report to file."""
        report = self.generate_summary_report()
        with open(output_path, "w") as f:
            f.write(report)
        print(f"Report saved to: {output_path}")


def main():
    """Main entry point for the ingest script."""
    parser = argparse.ArgumentParser(description="Process audit logs and generate metrics")
    parser.add_argument("--path", default="logs/", help="Path to log files")
    parser.add_argument("--pattern", default="*.jsonl", help="File pattern to match")
    parser.add_argument("--output", default="audit_summary.md", help="Output report file")
    parser.add_argument("--tool", help="Filter by specific tool name")
    parser.add_argument("--hours", type=int, default=24, help="Hours of data to analyze")

    args = parser.parse_args()

    # Initialize ingester
    ingester = AuditIngester(args.path)

    # Load events
    events = ingester.load_events(args.pattern)

    if not events:
        print("No events found. Exiting.")
        return

    # Generate and save report
    ingester.save_report(args.output)

    # Print key metrics to console
    print("\nKey Metrics:")
    print(f"  Total Events: {len(events):,}")
    print(f"  Error Rate: {ingester.compute_error_rate():.2f}%")

    latencies = ingester.compute_latency_percentiles()
    print(f"  Latency p95: {latencies['p95']:.2f}ms")

    top_failing = ingester.get_top_failing_tools(3)
    if top_failing:
        tool_name = top_failing[0]["tool_name"]
        error_rate = top_failing[0]["error_rate"]
        print(f"  Top Failing Tool: {tool_name} ({error_rate:.2f}%)")


if __name__ == "__main__":
    main()
