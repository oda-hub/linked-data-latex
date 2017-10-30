
def test_render():
    import ddpaper.render as render

    latex_jinja_env = render.get_latex_jinja_env()

    rendering=render.render_draft(
                        latex_jinja_env,
                        {'test_var':1},
                        input_template_string="\VAR{test_var}",
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == b"1"

def test_render_filter():
    import ddpaper.render as render
    import ddpaper.filters as filters

    latex_jinja_env = render.get_latex_jinja_env()
    filters.setup_custom_filters(latex_jinja_env)

    rendering=render.render_draft(
                        latex_jinja_env,
                        {'test_var':1.4123e-4},
                        input_template_string="\VAR{test_var|latex_exp}",
                        write_header=False,
                    )

    print("rendering",rendering)

    assert rendering == b"1.4$\\times$10$^{-4}$"