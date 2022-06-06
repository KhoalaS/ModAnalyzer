import os

for root, dirs, files in os.walk(os.path.relpath("org_classes/jars")):
    for file in files:
        print(file)
