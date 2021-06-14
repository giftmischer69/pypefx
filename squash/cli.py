from squash.shell import Shell


def main():
    sh = Shell(debug=True)
    sh.cmdloop()
