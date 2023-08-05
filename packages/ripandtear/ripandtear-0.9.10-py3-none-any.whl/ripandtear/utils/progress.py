from pathlib import Path

from rich import padding
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, DownloadColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn, BarColumn
from rich.style import Style

dir_name = Path.cwd().stem

search_message = Progress(TextColumn("{task.description}"))

search_info = Progress(SpinnerColumn(),
                       TextColumn("[progress.description]{task.description}"),
                       BarColumn(bar_width=None),
                       "{task.completed}")

file_category_progress = Progress("{task.description}",
                                  BarColumn(bar_width=None,
                                            complete_style='chartreuse2'),
                                  "[progress.percentage]{task.percentage:>3.1f}%",
                                  "[progress.completed]{task.completed} out of {task.total}")

file_progress = Progress(SpinnerColumn(),
                         "{task.description}",
                         BarColumn(bar_width=None,
                                   complete_style=Style(color='chartreuse2')),
                         "[progress.percentage]{task.percentage:>3.1f}%",
                         "-",
                         DownloadColumn(),
                         "-",
                         TransferSpeedColumn(),
                         "-",
                         TimeRemainingColumn(),)


async def search_table():

    search_table = Table.grid(expand=True)

    search_table.add_row(Panel.fit(
        search_message, title="Search Messages", border_style='green', padding=(1, 1)))

    search_table.add_row(Panel.fit(
        search_info, title=f"Searching for {dir_name}", border_style='green', padding=(1, 1)))

    return search_table


async def download_table():

    progress_table = Table.grid(expand=True)

    progress_table.add_row(Panel.fit(
        file_category_progress, title=f"Downloading {dir_name}", border_style='green', padding=(1, 1)))

    progress_table.add_row(
        Panel.fit(file_progress, title="Files Being Downloaded", border_style='green', padding=(1, 1)))
    return progress_table
