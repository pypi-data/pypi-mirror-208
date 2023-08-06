from importlib.metadata import version
import typer
from capabilities.config import CONFIG
from rich.console import Console
from rich.pretty import pprint

console = Console(stderr=True)

app = typer.Typer()


def version_callback(value: bool):
    if value:
        typer.echo(version("capabilities"))
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    )
):
    return


@app.command()
def login(api_key: str):
    """Add an api key to the config file for accessing the Capabilities API.

    To get an API key, head over to https://blazon.ai/signin
    """
    CONFIG.persist_secret("api_key", api_key)
    console.print(f"Saved API key for {CONFIG.api_url} to {CONFIG.secrets_file}")


@app.command()
def qa(document: str, question: str):
    """Use the Capabilities QA model to answer a question about a document.

    Args:
        document (str): The document to search. Can be a URL or a path to a local text or pdf file.
        question (str): The question to ask.
    """
    from capabilities.search.loader import create_document
    from capabilities.core import DocumentQA

    doc = create_document(document)
    result = DocumentQA()(doc.get_text(), question)
    pprint(result)
