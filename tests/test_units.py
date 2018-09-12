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
                        input_template_string="\VAR{test_var|u('erg')|round(15)}",
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == b"1.602177e-09"


    ddict = {'test_var': {'m/s': 10}}

    rendering = render.render_draft(
        latex_jinja_env,
        ddict,
        input_template_string="\VAR{test_var|u('km/hour')|int}",
        write_header=False,
    )

    print("rendering", rendering)

    assert rendering == b"36"


def test_units_unpickle():
    from ddpaper.data import setup_yaml

    from astropy import units as u
    import yaml

    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    setup_yaml()

    s=StringIO()
    r=dict(var=1*u.keV)
    yaml.dump(r,s)
    s.seek(0)
    rr=yaml.load(s)

    print(r)
    print(rr)

    assert r==rr


    import ddpaper.render as render

    latex_jinja_env = render.get_latex_jinja_env()

    ddict={'test_var':1*u.keV,'duration':1*u.s}

    rendering=render.render_draft(
                        latex_jinja_env,
                        ddict,
                        input_template_string="\VAR{test_var|u('erg')|round(15)}",
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == b"1.602177e-09"

    rendering=render.render_draft(
                        latex_jinja_env,
                        ddict,
                        input_template_string="\VAR{(test_var/duration)|u('erg/year')|round(5)}",
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == b"0.05056"
