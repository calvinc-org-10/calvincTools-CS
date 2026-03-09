from flask import Flask, render_template, abort, current_app
from jinja2.exceptions import TemplateNotFound


def checkTemplate_and_render(template, *args, errmsg=None, **kwargs):
    try:
        # Check if the template exists by trying to get it
        current_app.jinja_env.get_template(f'{template}')
        # If it exists, render the template
        return render_template(f'{template}', *args, **kwargs)
    except TemplateNotFound:
        # If the template is not found, return a 404 error
        showtemplate = 'UnderConstruction.html'
        if errmsg is None:
            errmsg = ""
        notreadyyet_msg = f"Template '{template}' not found.\n{errmsg}"
        cntext = {
            'notreadyyet_msg': notreadyyet_msg,
            }
        return render_template(showtemplate, **cntext), 404
        # abort(404)
    # end try
# checkTemplate_and_render
