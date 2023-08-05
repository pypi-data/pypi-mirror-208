import typer


def gettext():
	print("1 = text file, 2 = text entry")
	type = typer.prompt("Pick Option")
	while True:
		if type == "1":
			text, path = openr()
			break	
		elif type == "2":
			text = typer.prompt("Enter Text:")
			path = "null"
			break
		else:
			print("invalid option")
			continue

	return text, path

def openr():
	while True:
		try:
			path = typer.prompt("Enter Path to File")
			f = open(path, "r")
			break
		except:
			print("invalid path. please try again")
			continue
	return f, path