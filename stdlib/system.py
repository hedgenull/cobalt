import os

def ReadFile(path):
    with open(path) as f:
        data = f.read()
    return data

def WriteFile(path, data):
    with open(path, "w") as f:
        f.write(data)

def FileExists(path):
    return "true" if os.path.exists(path) else "false"