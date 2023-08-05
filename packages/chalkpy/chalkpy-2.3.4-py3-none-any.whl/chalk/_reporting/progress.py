import time
import uuid
from datetime import datetime, timedelta
from functools import cached_property
from typing import Dict, Iterable, Optional, cast

from rich import box, get_console
from rich.console import Group
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TaskID, TextColumn, TimeElapsedColumn
from rich.style import Style
from rich.table import Table
from rich.text import Text

from chalk._reporting.models import BatchOpKind, BatchOpStatus, BatchReport
from chalk._reporting.rich.color import PASTELY_CYAN, SHADOWY_LAVENDER, UNDERLYING_CYAN
from chalk._reporting.rich.live import ChalkLive
from chalk.client import ChalkOfflineQueryException
from chalk.utils.log_with_context import get_logger

_logger = get_logger(__name__)

_kind_to_display_type = {
    BatchOpKind.RECOMPUTE: "Dataset Recompute",
    BatchOpKind.OFFLINE_QUERY: "Offline Query",
}


class ProgressService:
    def __init__(self, operation_id: uuid.UUID, client: "ChalkAPIClientImpl", caller_method: Optional[str] = None):
        """
        :param operation_id: The ID of the operation that the ProgressService
            is polling for. This is commonly a `DatasetRevision` ID.
        :param client: A ChalkClient instance
        :param caller_method: Passed only if the caller is a Dataset method. When we call Dataset methods,
            the ProgressService is implicitly called, so we want to explain to the user that their method
            will be executed once the ProgressService finishes polling for the operation to complete.
        """
        self.operation_id = operation_id
        self.client = client
        self.caller_method = f"`{caller_method}()`" if caller_method else None

    @cached_property
    def resolver_progress(self) -> Progress:
        return Progress(
            TextColumn("  "),
            TextColumn("{task.description}"),
            BarColumn(
                finished_style=Style(color=PASTELY_CYAN),
                style=Style(color=SHADOWY_LAVENDER),
                complete_style=Style(color=UNDERLYING_CYAN),
            ),
            MofNCompleteColumn(),
            TextColumn("runs", style=Style(color=PASTELY_CYAN)),
            TimeElapsedColumn(),
        )

    @cached_property
    def main_progress(self) -> Progress:
        return Progress(
            TextColumn("{task.description}"),
            SpinnerColumn(style=Style(color=SHADOWY_LAVENDER)),
            TimeElapsedColumn(),
        )

    @cached_property
    def explainer_text(self) -> Text:
        explainer_text = Text(
            f"The `DatasetRevision` is still being computed. {self.caller_method} will execute once computation is complete.",
            style=Style(color=PASTELY_CYAN),
        )
        return explainer_text

    @cached_property
    def enclosure_panel(self) -> Panel:
        progress_bar_group = Group(self.main_progress, self.resolver_progress)

        panel_content_table = Table.grid()
        if self.caller_method is not None:
            panel_content_table.add_row(Padding(self.explainer_text, (0, 0, 1, 0)))
        panel_content_table.add_row(progress_bar_group)

        enclosure_panel = Panel.fit(
            panel_content_table, title="chalk", border_style=Style(color=PASTELY_CYAN), box=box.ROUNDED, padding=(1, 2)
        )

        return enclosure_panel

    def handle_resolver_update(self, batch_report: BatchReport, fqn_to_task_id: Dict) -> None:
        for resolver_report in batch_report.resolvers:
            fqn = resolver_report.resolver_fqn
            if fqn not in fqn_to_task_id:
                short_name = fqn.split(".")[-1]
                fqn_to_task_id[fqn] = self.resolver_progress.add_task(
                    description=f"[ {short_name} ]",
                    total=resolver_report.progress.total,
                )

        for resolver_report in batch_report.resolvers:
            fqn = resolver_report.resolver_fqn
            resolver_task_id = fqn_to_task_id[fqn]

            rows_done_new = resolver_report.progress.computed + resolver_report.progress.failed
            self.resolver_progress.update(resolver_task_id, completed=rows_done_new)

    def handle_success(self, main_task_id: TaskID, operation_display_type: str) -> None:
        self.enclosure_panel.title = "chalk ■"
        self.main_progress.update(main_task_id, description=f"{operation_display_type} completed", completed=1)

    def get_failing_resolver(self, batch_report: BatchReport) -> Optional[str]:
        """
        :return: The name of the resolver that failed, or None if no resolver failed.
        """
        for resolver in batch_report.resolvers:
            if resolver.status == BatchOpStatus.FAILED:
                return resolver.resolver_fqn

    def handle_and_raise_error(
        self,
        batch_report: BatchReport,
        main_task_id: TaskID,
        operation_display_type: str,
    ) -> None:
        panel = self.enclosure_panel
        main_progress = self.main_progress
        progress_table = cast(Table, self.enclosure_panel.renderable)

        self.handle_explainer_text_if_erring()
        panel.border_style = Style(color="red")
        main_progress.update(
            main_task_id,
            description=f"Error occurred while executing resolvers for {operation_display_type}",
        )
        error_message = (
            batch_report.error.message
            if batch_report.error
            else "Unfortunately the cause of this error is unknown. Please contact Chalk for support."
        )

        failing_resolver = self.get_failing_resolver(batch_report)
        stacktrace = batch_report.error and batch_report.error.exception and batch_report.error.exception.stacktrace
        table_contents = [
            ("Revision ID", str(self.operation_id)),
            *([("Failing Resolver", failing_resolver)] if failing_resolver else []),
            ("Error Message", error_message),
            *([("Stacktrace", stacktrace)] if stacktrace else []),
        ]
        error_box = Table(
            box=box.SQUARE,
            show_lines=True,
            show_header=False,
            style=Style(color="red"),
            row_styles=[Style(color="red")] * len(table_contents),
        )

        for row in table_contents:
            error_box.add_row(
                *row,
            )

        progress_table.add_row(Padding(Text(""), (0, 0, 1, 0)))
        progress_table.add_row(error_box)

        raise ChalkOfflineQueryException(errors=[batch_report.error] if batch_report.error else None)

    def handle_explainer_text_if_erring(self):
        if self.caller_method:
            self.explainer_text._text = [
                f"The computation for this `DatasetRevision` has failed. {self.caller_method} cannot be executed."
            ]
            self.explainer_text.style = Style(color="red")

    def handle_explainer_text_if_successful(self):
        if self.caller_method:
            self.explainer_text._text = [
                f"The computation for this `DatasetRevision` has completed. {self.caller_method} will be executed."
            ]
            self.explainer_text.style = Style(color="red")

    def poll_report(self) -> Iterable[BatchReport]:
        first_missing_report_dt = None
        poll_interval_seconds = 1
        report_polling_timeout = timedelta(minutes=1)

        while first_missing_report_dt is None or datetime.now() < first_missing_report_dt + report_polling_timeout:
            time.sleep(poll_interval_seconds)
            batch_report = self.client._get_batch_report(self.operation_id)
            if batch_report is None:
                first_missing_report_dt = first_missing_report_dt or datetime.now()
            else:
                first_missing_report_dt = None
                yield batch_report
        else:
            raise TimeoutError(f"Timed out waiting for status report of operation with ID {self.operation_id}")

    def await_operation(self, show_progress: bool = False) -> None:
        if show_progress and get_console().is_dumb_terminal:
            _logger.warning("Progress display is not supported in dumb terminals. Progress will not be shown.")
            show_progress = False

        if show_progress:
            fqn_to_task_id = {}
            initial_description = "Initializing progress report"
            main_task_id = self.main_progress.add_task(description=initial_description, total=1)
            main_task = self.main_progress._tasks[main_task_id]

            with ChalkLive(self.enclosure_panel, auto_refresh=True):
                for batch_report in self.poll_report():
                    operation_display_type = _kind_to_display_type.get(batch_report.operation_kind, "Operation")

                    # Update main progress text
                    if main_task.description == initial_description:
                        self.main_progress.update(
                            main_task_id, description=f"Executing resolvers for {operation_display_type}"
                        )

                    self.handle_resolver_update(batch_report=batch_report, fqn_to_task_id=fqn_to_task_id)

                    if batch_report.status == BatchOpStatus.COMPLETED:
                        self.handle_success(main_task_id=main_task_id, operation_display_type=operation_display_type)
                        break

                    if batch_report.status == BatchOpStatus.FAILED:
                        self.handle_and_raise_error(
                            batch_report=batch_report,
                            main_task_id=main_task_id,
                            operation_display_type=operation_display_type,
                        )
                        break  # should have raised but just in case
        else:
            for batch_report in self.poll_report():
                if batch_report.status == BatchOpStatus.FAILED:
                    raise ChalkOfflineQueryException(errors=[batch_report.error] if batch_report.error else None)
                if batch_report.status == BatchOpStatus.COMPLETED:
                    break
