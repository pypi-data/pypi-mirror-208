// SPDX-FileCopyrightText: 2022 The Ikarus Developers mueller@ibb.uni-stuttgart.de
// SPDX-License-Identifier: LGPL-3.0-or-later

#pragma once

#include <dune/functions/functionspacebases/lagrangebasis.hh>
#include <dune/functions/functionspacebases/powerbasis.hh>
#include <dune/grid/yaspgrid.hh>
#include <dune/python/common/typeregistry.hh>
#include <dune/python/pybind11/eigen.h>
#include <dune/python/pybind11/functional.h>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/stl.h>

#include <ikarus/finiteElements/feRequirements.hh>
#include <ikarus/utils/basis.hh>

namespace Ikarus::Python {

  // Python wrapper for the FVAssembler C++ class
  template <class Basis, class... options>
  void registerBasis(pybind11::handle scope, pybind11::class_<Basis, options...> cls) {
    using pybind11::operator""_a;

    using GridView    = typename Basis::GridView;
    using PreBasis    = typename Basis::PreBasis;
    using UntouchedBasis    = typename Basis::UntouchedBasis;
    using FlatBasis    = typename Basis::FlatBasis;

    cls.def(pybind11::init([](const UntouchedBasis& gb) {
              return new Basis(gb.preBasis());
            }));

//    pybind11::module scopedf = pybind11::module::import("dune.functions");
//
//    typedef Dune::Python::LocalViewWrapper< UntouchedBasis > LocalViewWrapper;
//    auto includes = Dune::Python::IncludeFiles{"dune/python/functions/globalbasis.hh"};
//    auto lv = Dune::Python::insertClass< LocalViewWrapper >( scopedf, "LocalViewWrapper",
//                                                             Dune::Python::GenerateTypeName("Dune::Python::LocalViewWrapperWrapper", Dune::MetaType<UntouchedBasis>()),
//                                                             includes).first;
//    lv.def( "bind", &LocalViewWrapper::bind );
//    lv.def( "unbind", &LocalViewWrapper::unbind );
//    lv.def( "index", [] ( const LocalViewWrapper &localView, int index ) { return localView.index( index ); });
//    lv.def( "__len__", [] ( LocalViewWrapper &self ) -> int { return self.size(); } );
//
//    Dune::Python::Functions::registerTree<typename LocalViewWrapper::Tree>(lv);
//    lv.def("tree", [](const LocalViewWrapper& view) { return view.tree(); });
//
//    auto basisName =Dune::className<UntouchedBasis>();
//    auto entry = Dune::Python::insertClass<UntouchedBasis>(scopedf, "DefaultGlobalBasis", pybind11::buffer_protocol(),
//                                                        Dune::Python::GenerateTypeName(basisName),Dune::Python::IncludeFiles{"dune/python/functions/globalbasis.hh"}
//    );
//    if (entry.second)
//      Dune::Python::registerGlobalBasis(scopedf,entry.first);
//
//    typedef Dune::Python::LocalViewWrapper< FlatBasis > LocalViewWrapperF;
//    auto includesF = Dune::Python::IncludeFiles{"dune/python/functions/globalbasis.hh"};
//    auto lvF = Dune::Python::insertClass< LocalViewWrapperF >( scopedf, "LocalViewWrapper",
//                                                             Dune::Python::GenerateTypeName("Dune::Python::LocalViewWrapperWrapper", Dune::MetaType<FlatBasis>()),
//                                                             includesF).first;
//    lvF.def( "bind", &LocalViewWrapperF::bind );
//    lvF.def( "unbind", &LocalViewWrapperF::unbind );
//    lvF.def( "index", [] ( const LocalViewWrapperF &localView, int index ) { return localView.index( index ); });
//    lvF.def( "__len__", [] ( LocalViewWrapperF &self ) -> int { return self.size(); } );
//
//    Dune::Python::Functions::registerTree<typename LocalViewWrapperF::Tree>(lvF);
//    lvF.def("tree", [](const LocalViewWrapperF& view) { return view.tree(); });
//
//    auto basisNameF =Dune::className<FlatBasis>();
//    auto entryF = Dune::Python::insertClass<FlatBasis>(scopedf, "DefaultGlobalBasis", pybind11::buffer_protocol(),
//                                                           Dune::Python::GenerateTypeName(basisNameF),Dune::Python::IncludeFiles{"dune/python/functions/globalbasis.hh"}
//    );
//    if (entryF.second)
//      Dune::Python::registerGlobalBasis(scopedf,entryF.first);


    cls.def(
        "flat",
        [](Basis& self) {
          return self.flat();
        },
        pybind11::return_value_policy::reference);

    cls.def(
        "untouched",
        [](Basis& self) {
          return self.untouched();
        },
        pybind11::return_value_policy::reference);

  }

}  // namespace Ikarus::Python
