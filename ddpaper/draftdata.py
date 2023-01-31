# from collections import defaultdict

from .yaml import yaml

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


def dump_notebook_globals(target, globs, selected=None):
    from io import StringIO
    from IPython import get_ipython
    ipython = get_ipython()
    s = ipython.magic("who_ls")

    with DraftData(target) as t_data:
        logger.info("storing in %s", target)

        for n in s:
            logger.debug("found global %s", n)
            if selected is not None and n not in selected:
                logger.debug("skipping")
            else:
                v = globs[n]
                logger.info("storing %s = %s", n, v)
                
                try:
                    s = StringIO()
                    yaml.dump(v, s)
                    logger.info("%s = %s can be represented as %s", n, v, s.getvalue())
                    t_data[n] = v
                except Exception as e:
                    logger.info("failed to represent %s because of %s", v, e)
                    continue

    return t_data
                
                

def load_globals(target, globs):
    with DraftData(target) as t_data:
        for k, v in t_data.items():
            if k in globs and globs[k] != v:
                logger.warning("overwriting %s = %s with %s", k, repr(globs[k])[:100], repr(v)[:100])
            else:
                logger.info("loading %s = %s", k, repr(v)[:100])
            globs[k] = v    