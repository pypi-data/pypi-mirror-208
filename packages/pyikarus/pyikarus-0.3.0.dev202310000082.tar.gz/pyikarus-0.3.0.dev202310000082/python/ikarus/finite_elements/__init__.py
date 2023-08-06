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


def linearElasticElement(basis, element, youngsMod, nu,volumeLoad=None,bp=None,neumannBoundaryLoad=None) :
    if not ((bp is None and neumannBoundaryLoad is None) or (bp is not None and neumannBoundaryLoad is not None)):
        raise TypeError("If you provide a boundary patch you should also provide a boundary load!")

    generator = MySimpleGenerator("LinearElastic", "Ikarus::Python")
    element_type = f"Ikarus::LinearElastic<{basis.cppTypeName},Ikarus::FErequirements<Eigen::Ref<Eigen::VectorXd>>,true>"

    includes = []
    includes += ["ikarus/finiteElements/mechanics/linearElastic.hh"]
    includes += ["ikarus/python/finiteElements/linearElastic.hh"]
    moduleName = "linearElastic_" + hashIt(element_type)
    module = generator.load(
        includes=includes,
        typeName=element_type,
        moduleName=moduleName
    )
    # https://pybind11.readthedocs.io/en/stable/advanced/functions.html#allow-prohibiting-none-arguments
    if volumeLoad is None:
        return module.LinearElastic(basis, element, youngsMod, nu)
    elif (bp is None and neumannBoundaryLoad is None):
        return module.LinearElastic(basis, element, youngsMod, nu,volumeLoad)
    else :
        return module.LinearElastic(basis, element, youngsMod, nu,volumeLoad,bp,neumannBoundaryLoad)


def nonLinearElasticElement(basis, element, material,volumeLoad=None,bp=None,neumannBoundaryLoad=None) :
    if not ((bp is None and neumannBoundaryLoad is None) or (bp is not None and neumannBoundaryLoad is not None)):
        raise TypeError("If you provide a boundary patch you should also provide a boundary load!")

    generator = MySimpleGenerator("NonLinearElastic", "Ikarus::Python")
    element_type = f"Ikarus::NonLinearElastic<{basis.cppTypeName},  {material.cppTypeName} ,Ikarus::FErequirements<Eigen::Ref<Eigen::VectorXd>>,true>"

    includes = []
    includes += ["ikarus/finiteElements/mechanics/nonLinearElastic.hh"]
    includes += ["ikarus/python/finiteElements/nonLinearElastic.hh"]
    moduleName = "nonLinearElastic_" + hashIt(element_type)
    module = generator.load(
        includes=includes,
        typeName=element_type,
        moduleName=moduleName
    )
    # https://pybind11.readthedocs.io/en/stable/advanced/functions.html#allow-prohibiting-none-arguments
    if volumeLoad is None:
        return module.NonLinearElastic(basis, element, material)
    elif bp is None and neumannBoundaryLoad is None:
        return module.NonLinearElastic(basis, element, material,volumeLoad)
    else :
        return module.NonLinearElastic(basis, element, material,volumeLoad,bp,neumannBoundaryLoad)
