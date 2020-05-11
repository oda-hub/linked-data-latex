# from collections import defaultdict

import ruamel.yaml as yaml
import os
import astropy.units as u

import logging

logger = logging.getLogger('ddpaper.draftdata')

draft_dir = os.environ.get('INTEGRAL_DDCACHE_ROOT', './draftdata')


class DraftData(object):
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

    def __exit__(self, _type, value, traceback):
        if self.data is not None:
            yaml.dump(self.data, open(draft_dir + "/" + self.section + ".yaml", "w"))


def dump_notebook_globals(target,globs):
    from io import StringIO
    from IPython import get_ipython
    ipython = get_ipython()
    s = ipython.magic("who_ls")

    from ddpaper.data import setup_yaml
    setup_yaml()

    with DraftData(target) as t_data:
        logger.info("storing in %s",target)

        for n in s:
            v = globs[n]
            if isinstance(v, u.Quantity):
                logger.info(n, v)


                try:
                    s=StringIO.StringIO()
                    yaml.dump(v,s)
                    t_data[n] = v
                except:
                    continue

            #    t_data[n] = {
            #        v.unit.to_string(): v.value,
            #        v.unit.to_string().replace(" ", "").strip(): v.value,
            #        "object_type":"astropy units",
            #    }

            if isinstance(v, float):
                logger.info(n, v)
                t_data[n] = v

