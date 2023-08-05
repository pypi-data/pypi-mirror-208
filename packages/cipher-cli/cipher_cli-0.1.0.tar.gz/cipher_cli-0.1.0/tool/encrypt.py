import typer
from rich import print
from rich.progress import track
import time
import text
import ciphers

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.command()
def caesar():
    print("Casear Cipher\n\n")
    time.sleep(1)
    f, path = text.gettext()
    key = int(typer.prompt("Enter key:"))
    total = 0
    for value in track(range(100), description="Processing..."):
        time.sleep(0.01)
        total += 1
    print("Encryption complete.")
    print(f"with key {key} caesar cipher encyrption result.\n")
    result = ciphers.caesar(f,key)
    print(result)
    if path != "null":
        with open("Output.txt", "w") as result_file:
            result_file.write(result)
            result_file.close()
    typer.Exit()

@app.callback()
def callback():
    pass
