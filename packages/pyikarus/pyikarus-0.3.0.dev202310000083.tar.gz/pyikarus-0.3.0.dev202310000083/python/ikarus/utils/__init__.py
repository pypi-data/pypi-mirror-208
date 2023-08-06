# SPDX-FileCopyrightText: 2022 The Ikarus Developers mueller@ibb.uni-stuttgart.de
# SPDX-License-Identifier: LGPL-3.0-or-later

from dune.generator.generator import SimpleGenerator
from dune.common.hashit import hashIt
import dune

def decoratePre(pre):
    def wrappedPre(*args, **kwargs):
        preamble = pre(*args, **kwargs)
        newPreamble = ""
        newPreamble += "#define DUNE_LOCALFEFUNCTIONS_USE_EIGEN 1\n"
        newPreamble += "#define EIGEN_DEFAULT_TO_ROW_MAJOR 1\n" #needed to have conforming Matrix storage between eigen and numpy otherwise references are not working
        newPreamble += preamble
        return newPreamble

    return wrappedPre


myAttributes = vars(SimpleGenerator).copy()
myAttributes["pre"] = decoratePre(myAttributes["pre"])
MySimpleGenerator = type("MySimpleGenerator", (object,), myAttributes)

def boundaryPatch(gridView,booleanVector) :
    dune.generator.addToFlags(pre="-DCMAKE_PREFIX_PATH=$ENV{CMAKE_PREFIX_PATH}")
    generator = MySimpleGenerator("BoundaryPatch", "Ikarus::Python")
    element_type = f"BoundaryPatch<{gridView.cppTypeName}>"

    includes = []
    includes += ["dune/fufem/boundarypatch.hh"]
    includes += ["ikarus/python/utils/boundarypatch.hh"]
    includes += gridView._includes
    moduleName = "boundaryPatch_" + hashIt(element_type)
    module = generator.load(
        includes=includes,
        typeName=element_type,
        moduleName=moduleName
    )
    return module.BoundaryPatch(gridView,booleanVector)
