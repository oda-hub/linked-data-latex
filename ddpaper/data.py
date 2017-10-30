from __future__ import print_function

import glob
import yaml
import sys
from dataanalysis import core, importing
core.global_readonly_caches=True


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

    for ddobject, in ddobjects:
        data[ddobject]=core.AnalysisFactory.byname(ddobject).get().export_data(include_class_attributes=True)
        print("loading",ddobject,"with",data[ddobject].keys())

    return data


def data_assertion(data):
    try:
        import assert_data
        assert_data.assert_draft_data(data)
    except ImportError:
        print("no data assertion: all data is meaningfull")
