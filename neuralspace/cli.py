import typer

from neuralspace import constants as K


app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool):
    if value:
        typer.echo(K.APP_NAME)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, '-V', '--version', callback=version_callback, is_eager=True
    ),
):
    '''
    NeuralSpace Voice AI CLI
    '''


@app.command()
def login(api_key: str = typer.Option('', help='Your API key')):
    '''
    Login to NeuralSpace VoiceAI
    '''
    if not api_key:
        api_key = typer.prompt('Enter your API key', hide_input=True)

    typer.echo(f'Logging in with API key: {api_key}')
    typer.echo(f'Saving unencrypted credentials to {K.API_KEY_PATH}')


@app.command()
def stream(lang: str = typer.Option(..., '-l', '--lang', '--language', '--language-id', help='Language code')):
    '''
    Real-time streaming transcription from your microphone
    '''
    typer.echo(f'Streaming with language: {lang}')


@app.command()
def transcribe(file: str = typer.Option(..., '-f', '--file', help='File to transcribe')):
    '''
    File transcription
    '''
    typer.echo(f'Transcribing file: {file}')


if __name__ == '__main__':
    app()
