import os
import sys

import requests
import toml
from dateutil import parser
from packaging import version

if __name__ == "__main__":
    package_name = "akerbp.mlpet"  # KEEP THIS UP TO DATE

    response = requests.get(f"https://pypi.org/pypi/{package_name}/json").json()
    latest_release = max(
        (
            (parser.parse(v[-1]["upload_time_iso_8601"]), k)
            for k, v in response["releases"].items()
        )
    )[1]

    with open(os.path.abspath("pyproject.toml"), "r") as f:
        project_file = toml.load(f)
    local_version = project_file["project"]["version"]

    if version.parse(local_version) <= version.parse(latest_release):
        print(
            f"Local version {local_version} is older than/the same version as the latest release {latest_release}!"
        )
        sys.exit(1)
    else:
        print(f"Local version {local_version} is up to date")
        sys.exit(0)
