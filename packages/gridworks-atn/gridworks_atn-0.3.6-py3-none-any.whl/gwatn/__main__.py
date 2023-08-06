"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Gridworks Atn Spaceheat."""


if __name__ == "__main__":
    main(prog_name="gridworks-atn")  # pragma: no cover
