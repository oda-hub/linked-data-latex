# from collections import defaultdict

import yaml

from astropy.io.misc import yaml
# yaml.load(stream, Loader=AstropyLoader)

import os
import astropy.units as u

import logging

logger = logging.getLogger('ddpaper.draftdata')

draft_dir = os.environ.get('INTEGRAL_DDCACHE_ROOT', './draftdata')


class DraftData(object):
    def __init__(self, section="results"):
        self.section = section

    @property
    def filename(self):
        return os.path.join(draft_dir, self.section + ".yaml")

    def __enter__(self):        
        try:
            self.data = yaml.load(open(self.filename))
        except Exception as e:
            logger.info("can not open %s due to %s %s, will create a new one", self.filename, e, repr(e))
            self.data = {}
        if self.data is None:
            self.data = {}
        return self.data

    def __exit__(self, _type, value, traceback):
        if self.data is not None:
            yaml.dump(self.data, 
                      open(self.filename, "w"))


def dump_notebook_globals(target, globs):
    from io import StringIO
    from IPython import get_ipython
    ipython = get_ipython()
    s = ipython.magic("who_ls")

    from ddpaper.data import setup_yaml
    setup_yaml()

    with DraftData(target) as t_data:
        logger.info("storing in %s", target)

        for n in s:
            v = globs[n]
            if isinstance(v, u.Quantity):
                logger.info(n, v)

                try:
                    s = StringIO()
                    yaml.dump(v, s)
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
