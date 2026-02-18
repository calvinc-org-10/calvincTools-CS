
from flask import current_app, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required
from sqlalchemy import text

from calvincTools.cMenu.views import menu_bp
from calvincTools.decorators import superuser_required
from calvincTools.forms import RawSQLForm
from calvincTools.utils import util_bp



@util_bp.route('/sql', methods=['GET', 'POST'])
@superuser_required
def run_sql():
    """
    Django equivalent: fn_cRawSQL
    """
    from ..models import ( db, )

    form = RawSQLForm()
    context = {}

    if form.validate_on_submit():
        sql_query = form.input_sql.data
        try:
            # isz there actually any SQL entered?
            if not sql_query.strip(): # type: ignore
                flash('Please enter a SQL query.', 'warning')
                return render_template('utils/enter_sql.html', form=form)
            # Basic safety check to prevent dangerous operations
            forbidden_statements = ['DROP', 'ALTER', 'TRUNCATE', 'CREATE']
            if any(stmt in sql_query.upper() for stmt in forbidden_statements): # type: ignore
                flash('Forbidden SQL operation detected.', 'danger')
                return render_template('utils/enter_sql.html', form=form)
            if not sql_query.strip().endswith(';'): # type: ignore
                sql_query += ';' # type: ignore
        except Exception as e:
            flash(f'Error processing SQL: {str(e)}', 'danger')
            return render_template('utils/enter_sql.html', form=form)
        # end try


        try:
            result = db.session.execute(text(sql_query)) # type: ignore

            if result.returns_rows: # type: ignore
                # SELECT query
                columns = result.keys()
                rows = [dict(row._mapping) for row in result]

                context['col_names'] = list(columns)
                context['num_records'] = len(rows)
                context['sql_results'] = rows
                context['orig_sql'] = sql_query

                # Optionally save to Excel
                # excel_file = save_to_excel(rows, columns)
                # context['excel_file'] = excel_file

                return render_template('utils/show_sql_results.html', **context)
            else:
                # INSERT/UPDATE/DELETE query
                db.session.commit()
                flash(f'Query executed successfully.  {result.rowcount} rows affected. ', 'success') # type: ignore
                context['col_names'] = f'NO RECORDS RETURNED; {result.rowcount} records affected' # type: ignore
                context['num_records'] = result.rowcount # type: ignore
                return render_template('utils/show_sql_results.html', **context)

        except Exception as e:
            db.session. rollback()
            flash(f'SQL Error: {str(e)}', 'danger')
            return render_template('utils/enter_sql.html', form=form)

    return render_template('utils/enter_sql. html', form=form)


@util_bp.route('/parameters', methods=['GET', 'POST'])
@superuser_required
def edit_parameters():
    """
    Django equivalent: fncParmForm
    """
    from ..models import ( db, cParameters, )

    if request.method == 'POST':
        # Handle form submission
        # Process parameter updates
        for key, value in request.form.items():
            if key.startswith('parm_value_'):
                parm_name = key.replace('parm_value_', '')
                param = cParameters.query.get(parm_name)
                if param and (param.user_modifiable or current_user.is_superuser):
                    param.parm_value = value

        db.session.commit()
        flash('Parameters updated successfully', 'success')
        return redirect(url_for('utils.edit_parameters'))

    # GET request
    parameters = cParameters.query.order_by(cParameters.parm_name).all()
    return render_template('utils/parameters.html', parameters=parameters)


# db and models imported in each method so that the initalized versions are used


@util_bp.route('/greetings', methods=['GET', 'POST'])
@login_required
def greetings():
    """
    Django equivalent:  fn_cGreetings
    """
    from ..models import ( db, cGreetings, )

    if request.method == 'POST':
        # Handle greeting submission
        greeting_text = request.form.get('greeting')
        if greeting_text:
            new_greeting = cGreetings(greeting=greeting_text)
            db.session.add(new_greeting)
            db.session.commit()
            flash('Greeting added successfully', 'success')
        return redirect(url_for('utils.greetings'))

    greetings = cGreetings.query. all()
    return render_template('utils/greetings.html', greetings=greetings)


############################################################
############################################################


@menu_bp.route('/formbrowse/<formname>')
@superuser_required
def form_browse(formname: str) -> ResponseReturnValue:
    urlIndex = 0
    viewIndex = 1

    FormNameToURL_Map = current_app.config['FORMNAME_TO_URL_MAP']

    # theForm = 'Form ' + formname + ' is not built yet.  Calvin needs more coffee.'
    formname = formname.lower()
    if formname in FormNameToURL_Map:
        if FormNameToURL_Map[formname][urlIndex]:
            endpt = FormNameToURL_Map[formname][urlIndex]
            if endpt in current_app.view_functions:
                return redirect(url_for(endpt))
            # endif endpoint exists
        elif FormNameToURL_Map[formname][viewIndex]:
            fn = FormNameToURL_Map[formname][viewIndex]
            if callable(fn):
                return fn()     # type: ignore
                # return redirect(url_for(fn.__name__))
            # endif is callable
        # endif url vs view
    # endif formname in map

    flash(f"Form {formname} not found. This form may not be implemented yet, or there may be a typo in the menu configuration.", "warning")
    notreadyyet_msg = f"Form {formname} is not built yet.  Calvin needs more coffee."
    return render_template("UnderConstruction.html", notreadyyet_msg=notreadyyet_msg)
    # # must be rendered if theForm came from a class-based-view
    # if hasattr(theForm,'render'): theForm = theForm.render()
    # return theForm
# form_browse

@menu_bp.route('/showtable/<tblname>')
@superuser_required
def show_table(tblname):
    # showing a table is nothing more than another form
    return form_browse(tblname)
# show_table

