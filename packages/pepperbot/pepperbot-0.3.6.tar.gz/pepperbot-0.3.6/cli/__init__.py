import typer

app = typer.Typer()


@app.command()
def init(
    name: str = typer.Argument(..., help="Your name"),
    template: str = typer.Option("default", help="The template to use"),
):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
