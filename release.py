#!/usr/bin/env python3
# coding: utf-8
import os
import re
import sys

version_regex = re.compile(r"^__version__ = \".*\"$")


def main():
    if len(sys.argv) < 2:
        print("Le numéro de version est obligatoire: ./release.py 1.0.0'")
        return 2

    version = sys.argv[1]
    print("Releasing version %s" % version)

    module_filename = os.path.join(os.path.dirname(__file__), 'toolbox', '__init__.py')
    # replace __version__
    with open(module_filename, "r+") as f:
        text = f.read()
        f.seek(0)
        result = re.sub(version_regex, f"__version__ = \"{version}\"", text)
        f.write(result)
        f.truncate()

    os.system(f"git add -u && "
              f"git commit -m \"Release {version}\" && "
              f"git tag \"v{version}\" && "
              f"git push origin main --tags && "
              f"git clean -df")


ret = main()
exit(ret)
