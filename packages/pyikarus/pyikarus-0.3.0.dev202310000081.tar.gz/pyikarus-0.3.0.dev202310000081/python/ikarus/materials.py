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

def materialConstructorDecorator(func):
    def wrapper(emodul,nu):
        generator = MySimpleGenerator(func.__name__, "Ikarus::Python")
        element_type = f"Ikarus::"+func.__name__+"<double>"

        includes = []
        includes += ["ikarus/finiteElements/mechanics/materials.hh"]
        includes += ["ikarus/python/finiteElements/materials/material.hh"]
        moduleName = func.__name__+"_" + hashIt(element_type)
        module = generator.load(
            includes=includes,
            typeName=element_type,
            moduleName=moduleName
        )

        # dispatcher = { 'NeoHooke' : NeoHooke, 'StVenantKirchhoff' : StVenantKirchhoff}


        return eval("module."+func.__name__+"(emodul,nu)")
    return wrapper


@materialConstructorDecorator
def StVenantKirchhoff(emodul,nu) :
    return materialConstructorDecorator

@materialConstructorDecorator
def NeoHooke(emodul,nu) :
    return materialConstructorDecorator
