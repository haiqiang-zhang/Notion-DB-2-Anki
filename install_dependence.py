import subprocess

subprocess.check_call(["pip3", "install", "--upgrade", "pip"])
subprocess.check_call(["pip3", "install", "--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org", "mypy", "aqt[qt6]"])