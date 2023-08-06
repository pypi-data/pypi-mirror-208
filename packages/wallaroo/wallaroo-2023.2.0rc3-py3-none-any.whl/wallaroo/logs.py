import datetime
import json
from typing import Any, Dict, List

import requests

from .inference_decode import decode_inference_result, to_nd_array_list
from .version import _user_agent


def fetch_plateau_logs(server: str, topic: str, limit: int = 100):
    headers = {"User-Agent": _user_agent}
    r = requests.get(f"http://{server}/topic/{topic}/", headers=headers)
    metadata = r.json()

    partitions = metadata["partitions"]
    records = []
    n = (limit // len(partitions)) + 1
    for partition, indices in partitions.items():
        end = indices["end"]
        query = {"start": end - n, "limit": n}
        partition_records = requests.get(
            f"http://{server}/topic/{topic}/{partition}/records",
            query,
            headers=headers,
        )
        records.extend(partition_records.json()["records"])

    return LogEntries(LogEntry(json.loads(r)) for r in records[:limit])


class LogEntry(object):
    """Wraps a single log entry.

    This class is highly experimental, is unsupported/untested, and may
    change/disappear in the near future.
    """

    def __init__(self, entry: Dict[str, Any]) -> None:
        self.elapsed = entry["elapsed"]
        self.model_name = entry["model_name"]  # TODO: refer to actual model
        self.model_version = entry["model_version"]  # TODO: refer to actual model

        if len(entry["original_data"]) == 1:
            # We will assume its key and grab its value
            self.input = next(iter(entry["original_data"].values()))
        else:
            # multiple inputs
            self.input = entry["original_data"]

        self.output = to_nd_array_list(decode_inference_result(entry))
        self.validation_failures = entry.get("check_failures") or []
        self.timestamp = datetime.datetime.fromtimestamp(entry["time"] / 1000)
        self.raw = entry
        if "shadow_data" in entry:
            self.shadow_data = entry["shadow_data"]
        else:
            self.shadow_data = {}


class LogEntries(List[LogEntry]):
    """Wraps a list of log entries.

    This class is highly experimental, is unsupported/untested, and may
    change/disappear in the near future.
    """

    def _repr_html_(self) -> str:
        def style(r):
            return "color: red;" if len(r.validation_failures) > 0 else ""

        rows = [
            f"""
        <tr style="{style(r)}">
            <td>{r.timestamp.strftime("%Y-%d-%b %H:%M:%S")}</td>
            <td>{r.output}</td>
            <td>{r.input}</td>
            <td>{len(r.validation_failures)}</td>
        </tr>
        """
            for r in self
        ]
        table = """
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Output</th>
                <th>Input</th>
                <th>Anomalies</th>
            </tr>
            {0}
        </table>
        """.format(
            "\n".join(rows)
        )
        return table


class LogEntriesShadowDeploy(LogEntries):
    def __init__(self, logs: LogEntries):
        self.logs = filter(lambda log: len(log.shadow_data.keys()) > 0, logs)

    def _repr_html_(self) -> str:
        logs = self.logs
        rows: List[str] = []
        for index, result in enumerate(logs):
            rows += """
                    <tr><td colspan='6'>Log Entry {}</td></tr>
                    <tr><td colspan='6'></td></tr>
                    <tr>
			<td>
				<strong><em>Input</em></strong>
			</td>
                        <td colspan='6'>{}</td>
                    </tr>
                """.format(
                index, result.input
            )
            rows += """
                    <tr>
                        <td>Model Type</td>
                        <td>
                            <strong>Model Name</strong>
                        </td>
                        <td>
                            <strong>Output</strong>
                        </td>
                        <td>
                            <strong>Timestamp</strong>
                        </td>
                        <td>
                            <strong>Model Version</strong>
                        </td>
                        <td>
                            <strong>Elapsed</strong>
                        </td>
                    </tr>
                    <tr>
                        <td><strong><em>Primary</em></strong></td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                """.format(
                result.model_name,
                result.output,
                result.timestamp.isoformat(),
                result.model_version,
                result.elapsed,
            )
            for shadow_model, shadow_result in result.shadow_data.items():
                rows += """
                    <tr>
                        <td><strong><em>Challenger</em></strong></td>
                        <td>{}</td>
                        <td>{}</td>
                        <td colspan=3></td>
                    </tr>
                """.format(
                    shadow_model, shadow_result
                )
        return """
                <h2>Shadow Deploy Logs</h2>
                <p>
                    <em>Logs from a shadow pipeline, grouped by their input.</em>
                </p>
                <table>
                    <tbody>
                        {}
                    </tbody>
                <table>
            """.format(
            "".join(rows)
        )
