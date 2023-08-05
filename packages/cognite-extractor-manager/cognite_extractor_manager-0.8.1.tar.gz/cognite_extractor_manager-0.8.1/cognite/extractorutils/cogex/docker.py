import os
import subprocess
import sys
from time import time
from typing import List, Tuple

from cognite.extractorutils.cogex._common import get_pyproject
from cognite.extractorutils.cogex.io import errorprint, headerprint, lineprint

_dockerfile_template = """
FROM {docker_base}
{preamble}
RUN set -ex && pip install --upgrade pip && pip install poetry pipx
ENV PATH /root/.local/bin:$PATH

RUN mkdir -p {installdir}
WORKDIR {installdir}

COPY pyproject.toml ./
COPY poetry.lock ./
{copy_packages}

RUN pipx install .

WORKDIR {workdir}

ENTRYPOINT [ "{entrypoint}" ]
"""


def _get_python_version() -> Tuple[int, int, int]:
    raw_version = (
        subprocess.check_output(["poetry", "run", "python", "-V"]).decode("ascii").replace("Python", "").strip()
    )
    print(f"Detected python version {raw_version}")
    raw_parts = raw_version.split(".")
    return int(raw_parts[0]), int(raw_parts[1]), int(raw_parts[2])


def _get_entrypoint() -> str:
    pyproject = get_pyproject()
    scripts = pyproject["tool"]["poetry"].get("scripts", [])

    if len(scripts) == 0:
        raise ValueError("No scripts found in [tool.poetry.scripts], can't deduce entrypoint")
    elif len(scripts) > 1:
        try:
            entrypoint = pyproject["tool"]["cogex"]["docker"]["entrypoint"]
        except KeyError:
            raise ValueError(
                "Multiple scripts found in [tool.poetry.scripts], "
                "please specify which is the entrypoint in 'entrypoint' under [tool.cogex.docker]"
            )

        if entrypoint not in scripts:
            raise ValueError(f"Given entrypoint {entrypoint} is not listed under [tool.poetry.scripts]")

        return entrypoint
    else:
        entrypoint = list(scripts.keys())[0]

    print(f"Using entrypoint '{entrypoint}' ({scripts[entrypoint].split(':')[0]})")
    return entrypoint


def _get_packages() -> List[str]:
    pyproject = get_pyproject()

    try:
        packages = [
            os.path.join(package["from"], package["include"]) for package in pyproject["tool"]["poetry"]["packages"]
        ]
    except KeyError:
        packages = [pyproject["tool"]["poetry"]["name"].replace("-", "_")]

    return packages


def _get_docker_base() -> str:
    try:
        base = get_pyproject()["tool"]["cogex"]["docker"]["base-image"]

    except KeyError:
        python_version = _get_python_version()
        base = f"python:{python_version[0]}.{python_version[1]}-slim"

    print(f"Using base image {base}")
    return base


def create_dockerfile() -> None:
    headerprint("Generating Dockerfile")
    packages = _get_packages()
    pyproject = get_pyproject()

    try:
        dockerconfig = pyproject["tool"]["cogex"]["docker"]
    except KeyError:
        raise ValueError("No [tool.cogex.docker] section in pyproject")

    preamble = dockerconfig.get("preamble", "")
    if preamble:
        print("Including preamble")

    copy_statements = ["COPY {} {}".format(p, p) for p in packages]

    if "readme" in pyproject["tool"]["poetry"]:
        copy_statements.append(f"COPY {pyproject['tool']['poetry']['readme']} {pyproject['tool']['poetry']['readme']}")
    copy_packages = "\n".join(copy_statements)

    installdir = dockerconfig.get("install-dir", pyproject["tool"]["poetry"]["name"].replace(" ", "_"))
    workdir = dockerconfig.get("work-dir", installdir)

    with open(f"build{os.path.sep}Dockerfile", "w") as dockerfile:
        dockerfile.write(
            _dockerfile_template.format(
                docker_base=_get_docker_base(),
                preamble=preamble,
                workdir=workdir,
                installdir=installdir,
                copy_packages=copy_packages,
                entrypoint=_get_entrypoint(),
            ).lstrip()
        )
    print(f"Dockerfile created at build{os.path.sep}Dockerfile")


def build_docker_image() -> None:
    start_time = time()

    pyproject = get_pyproject()
    try:
        tags = [
            tag.format(version=pyproject["tool"]["poetry"]["version"])
            for tag in get_pyproject()["tool"]["cogex"]["docker"]["tags"]
        ]
    except KeyError:
        raise ValueError("No docker tags listed in 'tags' under [tool.cogex.docker]")

    create_dockerfile()

    headerprint("Building Docker image")
    formatted_tags = " ".join([f"-t {tag}" for tag in tags])
    if os.system(f"docker build . -f build{os.path.sep}Dockerfile {formatted_tags}"):
        lineprint("red")
        errorprint("Build failed")
        print()
        sys.exit(1)

    lineprint()
    headerprint("Build done")
    print(f"Created docker images: {', '.join(tags)}")
    print(f"Total build time: {time() - start_time:.1f} s")
    print()
