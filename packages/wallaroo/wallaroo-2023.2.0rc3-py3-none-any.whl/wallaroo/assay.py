from typing import Optional, List, TYPE_CHECKING, Any, Dict

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import gql  # type: ignore
from .object import *
from .inference_decode import dict_list_to_dataframe
from .wallaroo_ml_ops_api_client.api.assay import assays_set_active
from .wallaroo_ml_ops_api_client.models.assays_set_active_json_body import (
    AssaysSetActiveJsonBody,
)

if TYPE_CHECKING:
    from .client import Client


class Assay(Object):
    """An Assay represents a record in the database. An assay contains
    some high level attributes such as name, status, active, etc. as well
    as the sub objects Baseline, Window and Summarizer which specify how
    the Baseline is derived, how the Windows should be created and how the
    analysis should be conducted."""

    def __init__(self, client: Optional["Client"], data: Dict[str, Any]) -> None:
        self.client = client
        assert client is not None
        super().__init__(gql_client=client._gql_client, data=data)

    def _fill(self, data: Dict[str, Any]) -> None:
        for required_attribute in ["id"]:
            if required_attribute not in data:
                raise RequiredAttributeMissing(
                    self.__class__.__name__, required_attribute
                )
        self._id = data["id"]

        for k in [
            "active",
            "status",
            "name",
            "warning_threshold",
            "alert_threshold",
            "pipeline_name",
        ]:
            if k in data:
                setattr(self, f"_{k}", data[k])

    def _fetch_attributes(self) -> Dict[str, Any]:
        return self._gql_client.execute(
            gql.gql(
                """
            query GetAssay($id: bigint) {
              assay(where: {id: {_eq: $id}}) {
                id
                name
                active
                status
                warning_threshold
                alert_threshold
                pipeline_name
              }
            }
            """
            ),
            variable_values={
                "id": self._id,
            },
        )["assay"]

    def turn_on(self):
        """Sets the Assay to active causing it to run and backfill any
        missing analysis."""

        ret = assays_set_active.sync(
            client=self.client.mlops(),
            json_body=AssaysSetActiveJsonBody(self._id, True),
        )
        self._active = True
        return ret

    def turn_off(self):
        """Disables the Assay. No further analysis will be conducted until the assay
        is enabled."""
        ret = assays_set_active.sync(
            client=self.client.mlops(),
            json_body=AssaysSetActiveJsonBody(self._id, False),
        )
        self._active = False
        return ret

    def set_alert_threshold(self, threshold: float):
        """Sets the alert threshold at the specified level. The status in the AssayAnalysis
        will show if this level is exceeded however currently alerting/notifications are
        not implemented."""
        res = self._gql_client.execute(
            gql.gql(
                """
            mutation SetActive($id: bigint!, $alert_threshold: Float!) {
                update_assay_by_pk(pk_columns: {id: $id}, _set: {alert_threshold: $alert_threshold}) {
                    id
                    active
                }
            }
            """
            ),
            variable_values={"id": self._id, "alert_threshold": threshold},
        )["update_assay_by_pk"]
        self._alert_threshold = threshold
        return res

    def set_warning_threshold(self, threshold: float):
        """Sets the warning threshold at the specified level. The status in the AssayAnalysis
        will show if this level is exceeded however currently alerting/notifications are
        not implemented."""

        res = self._gql_client.execute(
            gql.gql(
                """
            mutation SetActive($id: bigint!, $warning_threshold: Float!) {
                update_assay_by_pk(pk_columns: {id: $id}, _set: {warning_threshold: $warning_threshold}) {
                    id
                    active
                }
            }
            """
            ),
            variable_values={"id": self._id, "warning_threshold": threshold},
        )["update_assay_by_pk"]
        self._warning_threshold = threshold
        return res


def meta_df(assay_result: Dict, index_name) -> pd.DataFrame:
    """Creates a dataframe for the meta data in the baseline or window excluding the
    edge information.
    :param assay_result: The dict of the raw asset result"""
    return pd.DataFrame(
        {
            k: [assay_result[k]]
            for k in assay_result.keys()
            if k not in ["edges", "edge_names", "aggregated_values", "aggregation"]
        },
        index=[index_name],
    )


def edge_df(window_or_baseline: Dict) -> pd.DataFrame:
    """Creates a dataframe specifically for the edge information in the baseline or window.
    :param window_or_baseline: The dict from the assay result of either the window or baseline
    """

    data = {
        k: window_or_baseline[k]
        for k in ["edges", "edge_names", "aggregated_values", "aggregation"]
    }
    return pd.DataFrame(data)


class AssayAnalysis(object):
    """The AssayAnalysis class helps handle the assay analysis logs from the Plateau
    logs.  These logs are a json document with meta information on the assay and analysis
    as well as summary information on the baseline and window and information on the comparison
    between them."""

    def __init__(self, raw: Dict[str, Any]):
        self.assay_id = 0
        self.name = ""
        self.raw = raw
        self.iopath = ""
        self.score = 0.0
        self.status = ""
        self.alert_threshold = None
        self.warning_threshold = None
        self.window_summary: Dict[str, Any] = {}
        for k, v in raw.items():
            setattr(self, k, v)

    def compare_basic_stats(self) -> pd.DataFrame:
        """Creates a simple dataframe making it easy to compare a baseline and window."""
        r = self.raw
        baseline = r["baseline_summary"]
        window = r["window_summary"]

        bs_df = meta_df(baseline, "Baseline")
        ws_df = meta_df(window, "Window")
        df = pd.concat([bs_df, ws_df])

        text_cols = ["start", "end"]
        tdf = df[text_cols]
        df = df.drop(text_cols, axis=1)

        df.loc["diff"] = df.loc["Window"] - df.loc["Baseline"]
        df.loc["pct_diff"] = df.loc["diff"] / df.loc["Baseline"] * 100.0
        return pd.concat([df.T, tdf.T])

    def baseline_stats(self) -> pd.DataFrame:
        """Creates a simple dataframe with the basic stats data for a baseline."""
        r = self.raw
        baseline = r["baseline_summary"]
        bs_df = meta_df(baseline, "Baseline")
        return bs_df.T

    def compare_bins(self) -> pd.DataFrame:
        """Creates a simple dataframe to compare the bin/edge information of baseline and window."""
        r = self.raw
        is_baseline_run = r["status"] == "BaselineRun"

        baseline = r["baseline_summary"]
        window = r["window_summary"]
        bs_df = edge_df(baseline)
        ws_df = edge_df(window)
        bs_df.columns = [f"b_{c}" for c in bs_df.columns]  # type: ignore
        ws_df.columns = [f"w_{c}" for c in ws_df.columns]  # type: ignore
        if is_baseline_run:
            df = bs_df
        else:
            df = pd.concat([bs_df, ws_df], axis=1)
            df["diff_in_pcts"] = df["w_aggregated_values"] - df["b_aggregated_values"]
        return df

    def baseline_bins(self) -> pd.DataFrame:
        """Creates a simple dataframe to with the edge/bin data for a baseline."""
        r = self.raw

        baseline = r["baseline_summary"]
        bs_df = edge_df(baseline)
        bs_df.columns = [f"b_{c}" for c in bs_df.columns]  # type: ignore
        return bs_df.fillna(np.inf)

    def chart(self, show_scores=True):
        """Quickly create a chart showing the bins, values and scores of an assay analysis.
        show_scores will also label each bin with its final weighted (if specified) score.
        """
        r = self.raw
        is_baseline_run = r["status"] == "BaselineRun"
        baseline = r["baseline_summary"]
        window = r["window_summary"]

        summarizer = r["summarizer"]
        es = summarizer["bin_mode"]
        vk = baseline["aggregation"]
        metric = summarizer["metric"]
        num_bins = summarizer["num_bins"]
        weighted = True if summarizer["bin_weights"] is not None else False
        score = r["score"]
        scores = r["scores"]
        index = r["bin_index"]

        print(f"baseline mean = {baseline['mean']}")
        if not is_baseline_run:
            print(f"window mean = {window['mean']}")
        print(f"baseline median = {baseline['median']}")
        if not is_baseline_run:
            print(f"window median = {window['median']}")
        print(f"bin_mode = {es}")
        print(f"aggregation = {vk}")
        print(f"metric = {metric}")
        print(f"weighted = {weighted}")
        if not is_baseline_run:
            print(f"score = {score}")
            print(f"scores = {scores}")
            print(f"index = {index}")

        title = f"{num_bins} {es} {vk} {metric}={score:5.3f} bin#={index} Weighted={weighted} {window['start']}"

        if (
            len(baseline["aggregated_values"])
            == len(window["aggregated_values"])
            == len(baseline["edge_names"])
        ):
            if vk == "Edges":
                fig, ax = plt.subplots()
                for n, v in enumerate(baseline["aggregated_values"]):
                    plt.axvline(x=v, color="blue", alpha=0.5)
                    plt.text(v, 0, f"e{n}", color="blue")
                for n, v in enumerate(window["aggregated_values"]):
                    plt.axvline(x=v, color="orange", alpha=0.5)
                    plt.text(v, 0.1, f"e{n}", color="orange")
            else:
                fig, ax = plt.subplots()

                last = "Min"
                bin_begin = "["
                bin_end = ")"
                edge_names = []
                for idx, (n, e) in enumerate(
                    zip(baseline["edge_names"], baseline["edges"])
                ):
                    if e is not None:
                        next = f"{e:.1E}"
                        name = f"{n}\n{bin_begin}{last}, {next}{bin_end}"
                        last = next
                    else:
                        name = f"{n}\n({last}, Max]"
                    edge_names.append(name)
                    if idx >= 1:
                        bin_begin = "("
                    bin_end = "]"

                bar1 = plt.bar(
                    edge_names,
                    baseline["aggregated_values"],
                    alpha=0.50,
                    label=f"Baseline ({baseline['count']})",
                )
                if not is_baseline_run:
                    bar2 = plt.bar(
                        edge_names,
                        window["aggregated_values"],
                        alpha=0.50,
                        label=f"Window ({window['count']})",
                    )
                if len(edge_names) > 7:
                    ax.set_xticklabels(labels=edge_names, rotation=45)

                if show_scores and not is_baseline_run:
                    for i, bar in enumerate(bar1.patches):
                        ax.annotate(
                            f"{scores[i]:.4f}",
                            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                            ha="center",
                            va="center",
                            size=9,
                            xytext=(0, 8),
                            textcoords="offset points",
                        )
                plt.legend()
            ax.set_title(title)
            plt.xticks(rotation=45)
            plt.show()
        else:
            print(title)
            print(
                len(baseline["aggregated_values"]),
                len(window["aggregated_values"]),
                len(baseline["edge_names"]),
                len(window["edge_names"]),
            )
            print(baseline["aggregated_values"])
            print(window["aggregated_values"])
            print(baseline["edge_names"])
            print(window["edge_names"])
            return r


class AssayAnalysisList(object):
    """Helper class primarily to easily create a dataframe from a list
    of AssayAnalysis objects."""

    def __init__(self, raw: List[AssayAnalysis]):
        self.raw = raw

    def __getitem__(self, index):
        return self.raw[index]

    def __len__(self):
        return len(self.raw)

    def to_dataframe(self) -> pd.DataFrame:
        """Creates and returns a summary dataframe from the assay results."""
        return pd.DataFrame(
            [
                {
                    "assay_id": a.assay_id,
                    "name": a.name,
                    "iopath": a.iopath,
                    "score": a.score,
                    "start": a.window_summary["start"],
                    "min": a.window_summary["min"],
                    "max": a.window_summary["max"],
                    "mean": a.window_summary["mean"],
                    "median": a.window_summary["median"],
                    "std": a.window_summary["std"],
                    "std": a.window_summary["std"],
                    "warning_threshold": a.warning_threshold,
                    "alert_threshold": a.alert_threshold,
                    "status": a.status,
                }
                for a in self.raw
            ]
        )

    def to_full_dataframe(self) -> pd.DataFrame:
        """Creates and returns a dataframe with all values including inputs
        and outputs from the assay results."""

        return dict_list_to_dataframe([a.raw for a in self.raw])

    def chart_df(self, df: Union[pd.DataFrame, pd.Series], title: str, nth_x_tick=None):
        """Creates a basic chart of the scores from dataframe created from assay analysis list"""

        if nth_x_tick is None:
            if len(df) > 10:
                nth_x_tick = len(df) / 10
            else:
                nth_x_tick = 1

        plt.scatter(df.start, df.score, color=self.__pick_colors(df.status))
        plt.title(title)

        old_ticks = plt.xticks()[0]
        new_ticks = [t for i, t in enumerate(old_ticks) if i % nth_x_tick == 0]  # type: ignore
        plt.xticks(ticks=new_ticks, rotation=90)

        plt.grid()
        plt.show()

    def chart_scores(self, title: Optional[str] = None, nth_x_tick=4):
        """Creates a basic chart of the scores from an AssayAnalysisList"""
        if title is None:
            title = f"Model Insights Score"
        ardf = self.to_dataframe()
        if ardf.shape == (0, 0):
            raise ValueError("No data in this AssayAnalysisList.")

        self.chart_df(ardf, title, nth_x_tick=nth_x_tick)

    def chart_iopaths(
        self,
        labels: Optional[List[str]] = None,
        selected_labels: Optional[List[str]] = None,
        nth_x_tick=None,
    ):
        """Creates a basic charts of the scores for each unique iopath of an AssayAnalysisList"""

        iadf = self.to_dataframe()
        if iadf.shape == (0, 0):
            raise ValueError("No io paths in this AssayAnalysisList.")

        for i, iopath in enumerate(iadf["iopath"].unique()):
            if selected_labels is None or (
                labels is not None and labels[i] in selected_labels
            ):
                tempdf = iadf[iadf["iopath"] == iopath]
                if labels:
                    label = (
                        f"Model Insights Score on '{labels[i]}' ({iopath}) vs Baseline"
                    )
                else:
                    label = f"Model Insights Score on '{iopath}' vs Baseline"

                self.chart_df(tempdf, label, nth_x_tick=nth_x_tick)

    def __status_color(self, status: str):
        if status == "Ok":
            return "green"
        elif status == "Warning":
            return "orange"
        else:
            return "red"

    def __pick_colors(self, s):
        return [self.__status_color(status) for status in s]


class Assays(List[Assay]):
    """Wraps a list of assays for display in an HTML display-aware environment like Jupyter."""

    def _repr_html_(self) -> str:
        def row(assay) -> str:
            return (
                "<tr>"
                + f"<td>{assay._name}</td>"
                + f"<td>{assay._active}</td>"
                + f"<td>{assay._status}</td>"
                + f"<td>{assay._warning_threshold}</td>"
                + f"<td>{assay._alert_threshold}</td>"
                + f"<td>{assay._pipeline_name}</td>"
                + "</tr>"
            )

        fields = [
            "name",
            "active",
            "status",
            "warning_threshold",
            "alert_threshold",
            "pipeline_name",
        ]

        if self == []:
            return "(no assays)"
        else:
            return (
                "<table>"
                + "<tr><th>"
                + "</th><th>".join(fields)
                + "</th></tr>"
                + ("".join([row(assay) for assay in self]))
                + "</table>"
            )
