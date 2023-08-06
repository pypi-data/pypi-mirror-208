import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import setup

pkg_name = "wdmtoolbox"

version = open("VERSION", encoding="ascii").readline().strip()

if sys.argv[-1] == "publish":
    subprocess.run(shlex.split("cleanpy ."), check=True)
    subprocess.run(shlex.split("python setup.py sdist"), check=True)
    subprocess.run(
        shlex.split(f"twine upload --skip-existing dist/{pkg_name}-{version}.tar.gz"),
        check=True,
    )
    subprocess.run(
        shlex.split(f"twine upload --skip-existing dist/{pkg_name}-{version}*.whl"),
        check=True,
    )
    sys.exit()

if os.path.exists("build_meson"):
    shutil.rmtree("build_meson")
subprocess.run(shlex.split("meson setup build_meson"), check=True)
subprocess.run(shlex.split("meson compile -C build_meson"), check=True)
for libname in Path("build_meson").glob("*.so"):
    basename = os.path.basename(libname)
    shutil.copy(libname, Path(f"src/wdmtoolbox/{basename}"))

setup()
