# SPDX-FileCopyrightText: 2022 The Ikarus Developers mueller@ibb.uni-stuttgart.de
# SPDX-License-Identifier: LGPL-3.0-or-later
# this file is modified from dumux https://git.iws.uni-stuttgart.de/dumux-repositories/dumux/-/blob/master/setup.py

try:
    from dune.packagemetadata import metaData
except ImportError:
    from packagemetadata import metaData
from skbuild import setup

# When building a new package, update the version numbers below and run:
# acess docker container with mounted repo to /tmp/Ikarus
# docker run -v C:\Users\Alex\Documents\Ikarus:/tmp/Ikarus --pull missing -u root ikarusproject/ikarus-dev:latest --entrypoint= --rm --user root
# build _ikarus
# cd /tmp/Ikarus
#  /dune/dune-common/build-cmake/run-in-dune-env pip install twine scikit-build
# git config --global --add safe.directory /tmp/Ikarus
# /dune/dune-common/build-cmake/run-in-dune-env python setup.py sdist
# > /dune/dune-common/build-cmake/run-in-dune-env python -m twine upload dist/* --verbose
# install locally:  /dune/dune-common/build-cmake/run-in-dune-env pip install -v --log logfile --verbose  pyikarus
# and check
# apt update
# apt install nano
# cat << EOF > ~/.pypirc
# The current working directory is: $PWD
# You are logged in as $(whoami)
# EOF
# nano ~/.pypirc
# python -m venv /dune/dune-common/build-cmake/dune-env/
# source /dune/dune-common/build-cmake/dune-env/bin/activate
# pip install ikarus  --no-build-isolation

ikarusVersion = "0.3.0.dev202310000071" #+ datetime.today().time().strftime("%H%M%S")
duneVersion = "2.9.0"

metadata = metaData(duneVersion)[1]
metadata["version"] = ikarusVersion

# refactor sicne ikarus pypi package already exists
print(metadata)
metadata["name"] = "pyikarus"
#for key in metadata["packages"]:
#    key.replace("ikarus","pyikarus")

# from setuptools import setup, find_packages
print(metadata)

setup(**metadata)
