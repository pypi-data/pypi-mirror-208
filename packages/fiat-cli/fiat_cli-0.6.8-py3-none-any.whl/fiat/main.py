import typer

from .apps import dashboard, metastore, computing, job, juicefs, envd, devs

app = typer.Typer()
app.add_typer(dashboard.app, name="dash", help="🎅 Fiat Dashboard commands.")
app.add_typer(metastore.app, name="metastore", help="👾 Fiat Metastore commands.")
app.add_typer(computing.app, name="ray", help="🚢 Fiat Computing server commands.")
app.add_typer(job.app, name="job", help="📦 Fiat Job Submission commands.")
app.add_typer(juicefs.app, name="dfs", help="🗄  Fiat DFS configuration commands.")
app.add_typer(envd.app, name="env", help="🧑‍💻 Fiat Envd management commands.")
app.add_typer(devs.app, name="dev", help="🤹 Fiat Dagster utilities commands.")


if __name__ == "__main__":
    app()
