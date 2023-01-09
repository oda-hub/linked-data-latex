import jinja2
import re
import pytest
import requests
import ruamel.yaml as yaml
import pytest

def test_render():
    import ddpaper.render as render

    latex_jinja_env = render.get_latex_jinja_env()

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"\VAR{test_var}",
                        {'test_var':1},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == "1"

def test_render_filter():
    import ddpaper.render as render
    import ddpaper.filters as filters

    latex_jinja_env = render.get_latex_jinja_env()
    filters.setup_custom_filters(latex_jinja_env)

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"\VAR{test_var|latex_exp}",
                        {'test_var':1.4123e-4},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == "1.4$\\times$10$^{-4}$"

def test_render_exception():
    import ddpaper.render as render

    latex_jinja_env = render.get_latex_jinja_env()

    try:
        rendering=render.render_draft(
                            latex_jinja_env,
                            r"\BLOCK{ raise 'problem' }",
                            {'test_var':1},
                            write_header=False,
                        )
    except jinja2.exceptions.TemplateRuntimeError as e:
        assert e.args[0] == "problem"
    else:
        raise Exception("did not raise")



def test_render_call():
    import ddpaper.render as render
    import ddpaper.filters as filters

    latex_jinja_env = render.get_latex_jinja_env()
    filters.setup_custom_filters(latex_jinja_env)

    def gcn_cite(num):
        # s = requests.get('https://gcn-circular-gateway.herokuapp.com/gcn-bib/bynumber/%i'%num).text
        # return re.search('@ARTICLE\{(.*?),', s).groups()[0]
        if int(num) == 100:
            return "Hurley1998_gcn100"
        else:
            return num

    latex_jinja_env.globals['lib'] = dict(gcn=dict(cite=gcn_cite))

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"\VAR{lib.gcn.cite(100)}",
                        {'test_var':1.4123e-4},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == "Hurley1998_gcn100"

def test_render_loaded():
    import ddpaper.render as render
    import ddpaper.filters as filters

    latex_jinja_env = render.get_latex_jinja_env()
    filters.setup_custom_filters(latex_jinja_env)

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"\VAR{local.gcn.cite(100)}",
                        {'test_var':1.4123e-4},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == "Hurley1998_gcn100"

def test_render_loaded_preproc():
    import ddpaper.render as render
    import ddpaper.filters as filters

    latex_jinja_env = render.get_latex_jinja_env()
    filters.setup_custom_filters(latex_jinja_env)

    yaml.dump({r'\\citepgcn{(.*?)}': r'\\VAR{local.gcn.cite(\1)}'}, open('preproc.yaml', 'w'))

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"""
                            \ASSUME{preproc.yaml}
                            \citepgcn{100}
                        """,
                        {'test_var':1.4123e-4},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering.strip() == "Hurley1998_gcn100"



@pytest.mark.skip("ignoring odahub compute")
def test_render_oda():
    import ddpaper.render as render
    import ddpaper.filters as filters

    latex_jinja_env = render.get_latex_jinja_env()
    filters.setup_custom_filters(latex_jinja_env)
    
    yaml.dump({'status': 'oda.evaluate("odahub", "integral-observation-summary", "status", when_utc="2012-11-11T11:11:11")'}, open('load-status.yaml', 'w'))

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"""
                            \LOAD{load-status.yaml}
                            \VAR{status.data.curent_rev | int}
                        """,
                        {},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering.strip() == "1231"
