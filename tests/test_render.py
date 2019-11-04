import jinja2
import re
import requests
import yaml

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
        s = requests.get('https://gcn-circular-gateway.herokuapp.com/gcn-bib/bynumber/%i'%num).text
        return re.search('@ARTICLE\{(.*?),', s).groups()[0]

    latex_jinja_env.globals['oda']=dict(gcn=dict(cite=gcn_cite))

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"\VAR{oda.gcn.cite(100)}",
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

    yaml.dump({r'\\citepgcn{(.*?)}': r'\VAR{local.gcn.cite(\1)}'}, open('preproc.yaml', 'w'))

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"""
                            \PREPROC{preproc.yaml}
                            \citepgcn{100}
                        """,
                        {'test_var':1.4123e-4},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering.strip() == "Hurley1998_gcn100"

def test_render_loaded_assume():
    import ddpaper.render as render
    import ddpaper.filters as filters

    latex_jinja_env = render.get_latex_jinja_env()
    filters.setup_custom_filters(latex_jinja_env)

    rendering=render.render_draft(
                        latex_jinja_env,
                        r"""
                            \PREPROC{\\citepgcn{(.*?)}{\\VAR{local.gcn.cite(\1)}}
                            \citepgcn{100}
                        """,
                        {'test_var':1.4123e-4},
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering.strip() == "Hurley1998_gcn100"
