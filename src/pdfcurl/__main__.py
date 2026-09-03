"""Interface for ``python -m heliotrapi``."""

import click

from ._version import __version__

__all__ = ["main"]


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, message="%(version)s")
@click.pass_context
def main(
    ctx: click.Context,
) -> None:

    if ctx.invoked_subcommand is None:
        print("Please invoke subcommand!")


@main.command(name="serve")
@click.pass_context
def serve(ctx: click.Context):

    import uvicorn

    from pdfcurl.server import start_api

    uvicorn.run(
        start_api(),
        factory=False,
        host="localhost",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()
