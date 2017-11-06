# from collections import defaultdict

import dataanalysis.core as da
import yaml
import os
import astropy.units as u

draft_dir = os.environ.get('INTEGRAL_DDCACHE_ROOT', './draftdata')


class DraftData(da.DataAnalysis):
    def __init__(self, section="results"):
        self.section = section

    def __enter__(self):
        try:
            self.data = yaml.load(open(draft_dir + "/" + self.section + ".yaml"))
        except:
            self.data = {}
        if self.data is None:
            self.data = {}
        return self.data

    def __exit__(self, type, value, traceback):
        if self.data is not None:
            yaml.dump(self.data, open(draft_dir + "/" + self.section + ".yaml", "w"))


def dump_notebook_globals(target):
    from IPython import get_ipython
    ipython = get_ipython()
    s = ipython.magic("who_ls")

    with DraftData(target) as t_data:

        for n in s:
            v = globals()[n]
            if isinstance(v, u.Quantity):
                print(n, v)
                t_data[n] = {v.unit.to_string().replace(" ", "").strip(): v.value}

            if isinstance(v, float):
                print(n, v)
                t_data[n] = v

