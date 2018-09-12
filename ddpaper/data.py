from __future__ import print_function

import glob
import yaml
import sys
import re

try:
    from dataanalysis import core, importing
    from dataanalysis.displaygraph import dotify_hashe

    core.global_readonly_caches=True
except ImportError:
    print("WARNING: no DDA")

import astropy.units as u
import astropy.constants as const

import pydot



def load_data_directory(rootdir="./data",data=None):
    if data is None:
        data={}

    for fn in glob.glob(rootdir+"/*.yaml"):
        key=fn.replace(rootdir+"/","").replace(".yaml","")
        data[key]=yaml.load(open(fn))
        print("rootdir",rootdir)
        print("loading data",fn,key)
    return data


def load_data_ddobject(modules, assume, ddobjects, data=None):
#    app.jinja_env.globals.update(clever_function=clever_function)

    for m, in modules:
        print("importing", m)

        sys.path.append(".")
        module, name = importing.load_by_name(m)
        globals()[name] = module

    if len(assume) > 0:
        assumptions = ",".join([a[0] for a in assume])
        print(assumptions)
        core.AnalysisFactory.WhatIfCopy('commandline', eval(assumptions))

    if data is None:
        data = {}

    graph=pydot.Dot(graph_type='digraph', splines='ortho' )
    doc_root="Paper"
    graph.add_node(pydot.Node(doc_root, style="filled", fillcolor="green", shape="box"))

    for ddobject, in ddobjects:
        obj=core.AnalysisFactory.byname(ddobject)
        obj.datafile_restore_mode = 'url_in_object'
        obj=obj.get()
        data[ddobject]=obj.export_data(include_class_attributes=True)
        print("loading",ddobject,"with",data[ddobject].keys())

        graph,root_node=dotify_hashe(obj._da_locally_complete,graph=graph,return_root=True)
        graph.add_edge(pydot.Edge(root_node, doc_root))

    graph.write_png("paper_hashe.png")

    return data

class DynUnitDict(object):

    def __init__(self,data):
        self.raw_data=data

    def interpret_unit(self,item):
        try:
            requested_unit=u.Unit(item)
        except ValueError:
            raise

        for key,value  in self.raw_data.items():
            try:
                available_unit = u.Unit(key)
                return value * available_unit.to(requested_unit)
            except ValueError:
                continue


    def __getitem__(self, item):
        if item in self.raw_data:
            return DynUnitDict(self.raw_data[item])
        else:
            return self.interpret_unit(item)


def setup_yaml():

    def quantity_constructor(loader, node):
        value = loader.construct_scalar(node)
        value, unit = re.search("(.*?)__(.*)", value).groups()
        return u.Quantity(value, unit=u.Unit(unit))

    def quantity_representer(dumper, data):
        return dumper.represent_scalar(u'!Quantity', u'%.5lg__%s' % (data.value, data.unit.to_string()))

    def unit_representer(dumper, data):
        return dumper.represent_scalar(u'!Quantity', u'%.5lg__%s' % (1., data.unit.to_string()))

    def const_representer(dumper, data):
        return dumper.represent_scalar(u'!Quantity', u'%.5lg__%s' % (data.value, data.unit.to_string()))

    yaml.add_representer(u.Quantity, quantity_representer)
    yaml.add_representer(const.Constant, quantity_representer)
    yaml.add_representer(u.Unit, unit_representer)
    yaml.add_constructor('!Quantity', quantity_constructor)



def data_assertion(data):
    try:
        import assert_data
        assert_data.assert_draft_data(data)
    except ImportError:
        print("no data assertion: all data is meaningfull")
