import typer

import decrypt

import encrypt

app = typer.Typer()
app.add_typer(decrypt.app, name="decrypt")
app.add_typer(encrypt.app, name="encrypt")

