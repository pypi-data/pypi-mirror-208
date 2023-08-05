import typer
from rich import print
from rich.progress import track
import time
import ciphers
import text

app = typer.Typer()


@app.callback()
def callback():
   pass

@app.command()
def caesar():
    print("Casear Cipher\n\n")
    time.sleep(1)
    f, path = text.gettext()
    key = int(typer.prompt("Enter ENCYRPTION key:"))
    key = -(key)
    total = 0
    for value in track(range(100), description="Processing..."):
        time.sleep(0.01)
        total += 1
    print("Decryption complete.")
    print(f"with Encryption key {(-(key))} caesar cipher decyrption result.\n")
    result = ciphers.caesar(f,key)
    print(result)
    if path != "null":
        with open("Output.txt", "w") as result_file:
            result_file.write(result)
            result_file.close()
    typer.Exit()