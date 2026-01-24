import datetime
import os

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from sqlalchemy import text

from ..database import cTools_db

from ..models import cParameters, cGreetings
from ..forms import RawSQLForm
from ..decorators import superuser_required

util_bp = Blueprint('utils', __name__, url_prefix='/utils')


@util_bp.route('/sql', methods=['GET', 'POST'])
@superuser_required
def run_sql():
    """
    Django equivalent: fn_cRawSQL
    """
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
            result = cTools_db.session.execute(text(sql_query)) # type: ignore
            
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
                cTools_db.session.commit()
                flash(f'Query executed successfully.  {result.rowcount} rows affected. ', 'success') # type: ignore
                context['col_names'] = f'NO RECORDS RETURNED; {result.rowcount} records affected' # type: ignore
                context['num_records'] = result.rowcount # type: ignore
                return render_template('utils/show_sql_results.html', **context)
                
        except Exception as e:
            cTools_db.session. rollback()
            flash(f'SQL Error: {str(e)}', 'danger')
            return render_template('utils/enter_sql.html', form=form)
    
    return render_template('utils/enter_sql. html', form=form)


@util_bp.route('/parameters', methods=['GET', 'POST'])
@superuser_required
def edit_parameters():
    """
    Django equivalent: fncParmForm
    """
    if request.method == 'POST': 
        # Handle form submission
        # Process parameter updates
        for key, value in request.form.items():
            if key.startswith('parm_value_'):
                parm_name = key.replace('parm_value_', '')
                param = cParameters.query.get(parm_name)
                if param and (param.user_modifiable or current_user.is_superuser):
                    param.parm_value = value
        
        cTools_db.session.commit()
        flash('Parameters updated successfully', 'success')
        return redirect(url_for('utils.edit_parameters'))
    
    # GET request
    parameters = cParameters.query.order_by(cParameters.parm_name).all()
    return render_template('utils/parameters.html', parameters=parameters)


@util_bp.route('/greetings', methods=['GET', 'POST'])
@login_required
def greetings():
    """
    Django equivalent:  fn_cGreetings
    """
    if request.method == 'POST':
        # Handle greeting submission
        greeting_text = request.form.get('greeting')
        if greeting_text:
            new_greeting = cGreetings(greeting=greeting_text)
            cTools_db.session.add(new_greeting)
            cTools_db.session.commit()
            flash('Greeting added successfully', 'success')
        return redirect(url_for('utils.greetings'))
    
    greetings = cGreetings.query. all()
    return render_template('utils/greetings.html', greetings=greetings)