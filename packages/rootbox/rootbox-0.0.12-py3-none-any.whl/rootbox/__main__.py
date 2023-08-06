import typer

from .cli import cmd_exec, cmd_lxc, cmd_pull, cmd_run, cmd_start, main

app = typer.Typer(short_help="Utility to manage rootbox containers")

app.command(help="Start a managed container instance")(cmd_start.start)
app.command(help="Execute a command in an existing instance")(cmd_exec.exec)
app.command(help="Pull an image into the local cache")(cmd_pull.pull)
app.command(help="Run a command in an ephemeral instance")(cmd_run.run)
app.add_typer(
    cmd_lxc.app, name="lxc", help="Get information about available LCX images"
)

app.callback()(main.rootbox)


def main():
    app()


if __name__ == "__main__":
    app()
