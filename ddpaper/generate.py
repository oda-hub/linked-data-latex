from __future__ import print_function

from rich.logging import RichHandler
import argparse
from ddpaper.data import setup_yaml
from ddpaper.render import get_latex_jinja_env
from ddpaper.filters import setup_custom_filters
from ddpaper.data import load_data_directory, load_data_ddobject
from ddpaper.render import render_definitions, render_draft, render_update, render_validate

import logging

from nb2workflow.nbadapter import NotebookAdapter



logger = logging.getLogger('ddpaper.generate')


# try:
#     from dataanalysis import core
#     dda_available = True
# except ImportError:
#     logger.warning("no DDA")
#     dda_available = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", default="main.tex")
    parser.add_argument("-o", "--output", default="-")
    parser.add_argument("-d", "--data", default="./data")
    parser.add_argument("--draft", action='store_true', default=False)
    parser.add_argument("--debug", action='store_true', default=False)
    parser.add_argument("--quiet", action='store_true', default=False)
    parser.add_argument("--mode", default='draft', help="draft, macros, update, validate")

    parser.add_argument('-a', dest='assume', metavar='ASSUME', type=str, help='...', nargs='+', action='append',
                        default=[])
    parser.add_argument('-m', dest='modules', metavar='MODULE_NAME', type=str, help='module to load', nargs='+',
                        action='append', default=[])
    parser.add_argument('-l', dest='load', metavar='LOAD', type=str, help='...', nargs='+', action='append',
                        default=[])
    parser.add_argument("-w", "--write-caches",
                        dest="writecaches", action='store_true', default=False)    
    parser.add_argument("-L", "--log-string", dest='logstring', default=None)

    args = parser.parse_args()


    if args.debug:
        level = 'DEBUG'
    else:
        level = 'INFO'

    logging.shutdown()
    logging.basicConfig(
        level=level, 
        # handlers=[RichHandler(highlighter=None, markup=True, level="INFO")],
        # datefmt="[%X]",
        force=True,
        # format="%(message)s"
    )

    
    if args.logstring:
        import odafunction.logs
        odafunction.logs.app_logging.parse_logspec(args.logstring)
        odafunction.logs.app_logging.setup_tree()

        
    # if args.writecaches and dda_available:
    #     core.global_readonly_caches = False

    latex_jinja_env = get_latex_jinja_env()
    setup_custom_filters(latex_jinja_env)

    setup_yaml()

    data = load_data_directory(args.data)
    data = load_data_ddobject(args.modules, args.assume, args.load, data)

    mode = args.mode
    if args.draft:
        if args.mode != "draft":
            logger.error("can not combine --draft and non-draft --mode")
            return

    template_string = open(args.input).read()

    if mode == "draft":
        output = render_draft(latex_jinja_env,
                              template_string,
                              data)
    elif mode == "macros":
        output = render_definitions(latex_jinja_env,
                                    template_string,
                                    data)
    elif mode == "update":
        output = render_update(latex_jinja_env,
                               template_string,
                               data)
    elif mode == "validate":
        output = render_validate(latex_jinja_env,
                                 template_string,
                                 data)
    else:
        logger.error('unknown mode: %s', mode)
        return

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w") as output_file:
            output_file.write(output)


    
    # logging.getLogger().info("starting")
    # import logging_tree
    # logging_tree.printout()
    
    # bind dda, json, sources


if __name__ == '__main__':
    main()
