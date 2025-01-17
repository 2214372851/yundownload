import time
from rich.progress import Progress, BarColumn, DownloadColumn,TransferSpeedColumn, SpinnerColumn, TimeRemainingColumn, TimeElapsedColumn, TransferSpeedColumn

with Progress(
        "[progress.description]{task.description}",
        SpinnerColumn(finished_text="[green]✔"),
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        "[yellow]⏱",
        TimeElapsedColumn(),
        "[cyan]⏳",
        TimeRemainingColumn()
) as progress:
    description = "[red]Loading"
    task = progress.add_task(description, total=1000)
    for p in range(1, 1001):
        if p != 1000:
            description = "[red]Loading"
        else:
            description = "[green]Finished"
        progress.update(task, completed=p, description=description)
        time.sleep(0.02)
