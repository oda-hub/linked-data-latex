import ddpaper.data


def test_units():
    print(ddpaper.data.DynUnitDict({'keV':1.})['erg'])

    print(ddpaper.data.DynUnitDict({'m/s': 10.})['km/hour'])


def test_render_units():
    import ddpaper.render as render

    latex_jinja_env = render.get_latex_jinja_env()

    ddict={'test_var':{'keV':1}}

    rendering=render.render_draft(
                        latex_jinja_env,
                        ddict,
                        input_template_string="\VAR{test_var|u('erg')}",
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == b"1.602176565e-09"


    ddict = {'test_var': {'m/s': 10}}

    rendering = render.render_draft(
        latex_jinja_env,
        ddict,
        input_template_string="\VAR{test_var|u('km/hour')|int}",
        write_header=False,
    )

    print("rendering", rendering)

    assert rendering == b"36"