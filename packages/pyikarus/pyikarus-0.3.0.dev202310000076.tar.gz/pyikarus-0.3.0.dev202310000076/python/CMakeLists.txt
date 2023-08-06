# SPDX-FileCopyrightText: 2022 The Ikarus Developers mueller@ibb.uni-stuttgart.de
# SPDX-License-Identifier: LGPL-3.0-or-later
add_subdirectory(ikarus)
set(CXX_MAX_STANDARD 20)
#configure_file(setup.py.in setup.py)
#  if(SKBUILD)
#    set(PYPI_PACKAGE_NAME "pyikarus")
#  else ()
    set(PYPI_PACKAGE_NAME "ikarus")
#  endif()
message(STATUS "PYPI_PACKAGE_NAME ${PYPI_PACKAGE_NAME}")
dune_python_configure_bindings(
  PATH
  "."
  PACKAGENAME
  ${PYPI_PACKAGE_NAME}
  CMAKE_METADATA_FLAGS
  DUNE_OPTS_FILE
  CXX_MAX_STANDARD
)
if(POLICY CMP0087)
  cmake_policy(SET CMP0087 NEW)
endif()
