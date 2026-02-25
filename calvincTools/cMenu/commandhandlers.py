
from flask import (
    current_app, flash, redirect, render_template, request, url_for
    )
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required
from sqlalchemy import text

from calvincTools.decorators import superuser_required, permission_required
from calvincTools.forms import RawSQLForm

# db and models imported in each method so that the initalized versions are used


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
            # is there actually any SQL entered?
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

                context['colNames'] = list(columns)
                context['nRecs'] = len(rows)
                context['SQLresults'] = rows
                context['OrigSQL'] = sql_query

                # Optionally save to Excel - WRITEMEWRITEMEWRITEME!!!!
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

    return render_template('utils/enter_sql.html', form=form)
# run_sql

# @superuser_required
@permission_required('EditParm')
def edit_parameters():
    """
    Django equivalent: fncParmForm

    Handle Parameter management (GET and POST).
    Displays all existing Parameters plus a blank form for new entries.
    
    GET: Display all records + blank forms
    POST: Save/update all parameters from the form, then redirect back to GET to show updated list.
    """
    from ..models import ( db, cParameters, )
    from .forms import (
        cParameterEditForm, cParameterItemForm, 
        cParameterEditForm_SU, cParameterItemForm_SU, 
        )
    
    SuperMan = current_user.is_superuser

    blank_formline_count = request.args.get('blank_formline_count', 1, type=int)
    flds_to_update = ['parm_name', 'parm_value', 'user_modifiable', 'comments'] if SuperMan else ['parm_name', 'parm_value', 'comments']   # only superusers can edit parm_name (?) and user_modifiable
    flds_form_labels = ['Parameter Name', 'Parameter Value', 'User Modifiable', 'Comments'] if SuperMan else ['Parameter Name', 'Parameter Value', 'Comments']
    has_id_field = False   # cParameterItemForm has no id field, so we set this to False to prevent the template from trying to render it

    formclass = cParameterEditForm_SU if SuperMan else cParameterEditForm
    itemformclass = cParameterItemForm_SU if SuperMan else cParameterItemForm
    
    if request.method == 'GET':
        # Get all existing parameters to display in the form
        existing_parms = cParameters.query.all() if SuperMan else cParameters.query.filter(cParameters.user_modifiable == True).all()
        
        # Create form with existing users
        form = formclass()
        
        # Clear default entry so we can control the list explicitly
        while len(form.parameters) > 0:
            form.parameters.pop_entry()
        
        # Populate form with existing users
        for parm in existing_parms:
            form.parameters.append_entry({
                # "pk": parm.id,
                "parm_name": parm.parm_name,
                "parm_value": parm.parm_value,
                "user_modifiable": parm.user_modifiable,
                "comments": parm.comments,
            })
        
        # Add blank users for new entries
        blank_rec = cParameters()  # type: ignore
        for _ in range(blank_formline_count):
            form.parameters.append_entry(blank_rec)
        
        templt = 'utils/cParameters.html'
        contxt = {
            'form': form,
            'fields_to_update': dict(zip(flds_to_update, flds_form_labels)),
            'has_id_field': has_id_field,   # cParameterItemForm has no id field, so we set this to False to prevent the template from trying to render it
            'prototype_blank_form': itemformclass(prefix=form.parameters.name + '-N-'),  # create a prototype blank form with the correct prefix for dynamic addition in the template
            'blank_formline_count': blank_formline_count,
            }
        return render_template(templt, **contxt)
    
    elif request.method == 'POST':
        form = formclass()
        
        if form.validate_on_submit():
            try:
                # Get all user IDs from the request to identify which ones are new/existing
                parameters_in_form = []
                # for user_data in form.parameters.data:
                #     if user_data.get("pk"):
                #         parameters_in_form.append(user_data["pk"])
                
                # Process each user in the form
                for i, parm_form in enumerate(form.parameters.entries):      #pylint: disable=unused-variable
                    data_from_form = {}
                    # pk = getattr(parm_form.pk, 'data', None)
                    # TODO: use flds_to_update to loop through and build data_from_form instead of hardcoding each field
                    data_from_form['parm_name'] = getattr(parm_form.parm_name, 'data', '')
                    data_from_form['parm_value'] = getattr(parm_form.parm_value, 'data', '')
                    data_from_form['user_modifiable'] = getattr(parm_form.user_modifiable, 'data', True)
                    data_from_form['comments'] = getattr(parm_form.comments, 'data', '')
                    
                    record_needs_saving = False
                    
                    # Skip blank entries (no parm_name provided)
                    if not data_from_form['parm_name'].strip():
                        continue
                    
                    # Check if this is an existing user or new user
                    parm = cParameters.query.filter(cParameters.parm_name == data_from_form['parm_name']).first()    # type: ignore
                    
                    if parm:
                        # remove if requested
                        if parm_form.Remove.data:
                            db.session.delete(parm)
                            flash(f'Parameter "{parm.parm_name}" removed successfully.', 'success')
                            continue
                        
                        # # make sure parm name hasn't been changed to a duplicate of another existing parm
                        # existing_parm_with_same_name = cParameters.query.filter(cParameters.parm_name == data_from_form['parm_name'], cParameters.id != parm.id).first()    # type: ignore
                        # if existing_parm_with_same_name:
                        #     flash(f'Error: Parameter name "{data_from_form['parm_name']}" already exists. Please choose a different name.', 'danger')
                        #     return redirect(url_for('utils.edit_parameters'))
                        
                        # Update existing parm
                        for fld in flds_to_update:
                            if data_from_form[fld] != getattr(parm, fld):
                                setattr(parm, fld, data_from_form[fld])
                                record_needs_saving = True
                                flash(f'Parameter "{parm.parm_name}", {fld} updated successfully.', 'success')
                    else:
                        # Create new parm
                        parm = cParameters(**{key:val for key, val in data_from_form.items() if key in flds_to_update})
                        record_needs_saving = True
                        flash(f'Parameter "{parm.parm_name}" created successfully.', 'success')
                    # if parm exists or new parm created
                    
                    if record_needs_saving:
                        db.session.add(parm)
                
                db.session.commit()
                # flash('All parms saved successfully!', 'success')
                return redirect(url_for('utils.edit_parameters'))
            # endfor each user in form
            
            except Exception as e:      #pylint: disable=broad-exception-caught
                db.session.rollback()
                flash(f'Error saving users: {str(e)}', 'danger')
                return redirect(url_for('utils.edit_parameters'))
            # endtry
        else:
            flash('Form validation failed. Please check your entries.', 'danger')

        templt = 'utils/cParameters.html'
        contxt = {
            'form': form,
            'fields_to_update': dict(zip(flds_to_update, flds_form_labels)),
            'has_id_field': has_id_field,   # cParameterItemForm has no id field, so we set this to False to prevent the template from trying to render it
            'prototype_blank_form': itemformclass(prefix=form.parameters.name + '-N-'),  # create a prototype blank form with the correct prefix for dynamic addition in the template
            'blank_formline_count': blank_formline_count,
            }
        return render_template(templt, **contxt)
        # endif form.validate_on_submit()
    else:
        flash('Invalid request method.', 'danger')
        return redirect(url_for('utils.edit_parameters'))
    # endif request.method == 'GET' vs 'POST'
# edit_parameters

@login_required
def edit_greetings() -> ResponseReturnValue:
    """
    Handle Greetings management (GET and POST).
    Displays all existing Greetings plus a blank form for new entries.
    
    GET: Display all records + blank forms
    POST: Save/update all parameters from the form, then redirect back to GET to show updated list.
    """
    from ..models import ( db, cGreetings, )
    from .forms import (
        cGreetingsEditForm, cGreetingsItemForm,
        )
    
    # SuperMan = current_user.is_superuser  # nobody cares for this form!

    blank_formline_count = request.args.get('blank_formline_count', 1, type=int)
    flds_to_update = ['greeting', ]
    flds_form_labels = ['Greeting', ]
    has_id_field = True

    formclass = cGreetingsEditForm
    itemformclass = cGreetingsItemForm
    
    if request.method == 'GET':
        # Get all existing parameters to display in the form
        existing_greets = cGreetings.query.all()
        
        # Create form with existing users
        form = formclass()
        
        # Clear default entry so we can control the list explicitly
        while len(form.greetings) > 0:
            form.greetings.pop_entry()
        
        # Populate form with existing users
        for greeting in existing_greets:
            form.greetings.append_entry({
                "pk": greeting.id,
                "greeting": greeting.greeting,
            })
        
        # Add blank users for new entries
        blank_rec = cGreetings()  # type: ignore
        for _ in range(blank_formline_count):
            form.greetings.append_entry(blank_rec)
        
        templt = 'utils/cGreetings.html'
        contxt = {
            'form': form,
            'fields_to_update': dict(zip(flds_to_update, flds_form_labels)),
            'has_id_field': has_id_field,   # cParameterItemForm has no id field, so we set this to False to prevent the template from trying to render it
            'prototype_blank_form': itemformclass(prefix=form.greetings.name + '-N-'),  # create a prototype blank form with the correct prefix for dynamic addition in the template
            'blank_formline_count': blank_formline_count,
            }
        return render_template(templt, **contxt)
    
    elif request.method == 'POST':
        form = formclass()
        
        if form.validate_on_submit():
            try:
                # Get all user IDs from the request to identify which ones are new/existing
                records_in_form = []
                for form_record in form.greetings.data:
                    if form_record.get("pk"):
                        records_in_form.append(form_record["pk"])
                
                # Process each user in the form
                for i, item_form in enumerate(form.greetings.entries):      #pylint: disable=unused-variable
                    data_from_form = {}
                    pk = getattr(item_form.pk, 'data', None)
                    # TODO: use flds_to_update to loop through and build data_from_form instead of hardcoding each field
                    data_from_form['greeting'] = getattr(item_form.greeting, 'data', '')
                    
                    record_needs_saving = False
                    
                    # # Skip blank entries (no parm_name provided)
                    # if not data_from_form['parm_name'].strip():
                    #     continue
                    
                    # Check if this is an existing user or new user
                    greeting = None
                    if pk:
                        greeting = cGreetings.query.get(pk)
                    
                    if greeting:
                        # remove if requested
                        if item_form.Remove.data or not data_from_form['greeting'].strip():
                            db.session.delete(greeting)
                            flash(f'Greeting "{pk}" removed successfully.', 'success')
                            continue

                        # dup greetings will be caught by hand, won't enforce it here (for now)
                        # # make sure parm name hasn't been changed to a duplicate of another existing parm
                        # existing_parm_with_same_name = cParameters.query.filter(cParameters.parm_name == data_from_form['parm_name'], cParameters.id != parm.id).first()    # type: ignore
                        # if existing_parm_with_same_name:
                        #     flash(f'Error: Parameter name "{data_from_form['parm_name']}" already exists. Please choose a different name.', 'danger')
                        #     return redirect(url_for('utils.edit_parameters'))
                        
                        # Update existing parm
                        for fld in flds_to_update:
                            if data_from_form[fld] != getattr(greeting, fld):
                                setattr(greeting, fld, data_from_form[fld])
                                record_needs_saving = True
                                flash(f'Greeting "{pk}" updated successfully.', 'success')
                    else:
                        # Create new parm
                        greeting = cGreetings(**{key:val for key, val in data_from_form.items() if key in flds_to_update})
                        record_needs_saving = True
                        flash(f'Parameter "{greeting.greeting}" created successfully.', 'success') # type: ignore
                    # if parm exists or new parm created
                    
                    if record_needs_saving:
                        db.session.add(greeting)
                
                db.session.commit()
                # flash('All parms saved successfully!', 'success')
                return redirect(url_for('utils.edit_greetings'))
            # endfor each user in form
            
            except Exception as e:      #pylint: disable=broad-exception-caught
                db.session.rollback()
                flash(f'Error saving records: {str(e)}', 'danger')
                return redirect(url_for('utils.edit_greetings'))
            # endtry
        else:
            flash('Form validation failed. Please check your entries.', 'danger')

        templt = 'utils/cGreetings.html'
        contxt = {
            'form': form,
            'fields_to_update': dict(zip(flds_to_update, flds_form_labels)),
            'has_id_field': has_id_field,   # cParameterItemForm has no id field, so we set this to False to prevent the template from trying to render it
            'prototype_blank_form': itemformclass(prefix=form.greetings.name + '-N-'),  # create a prototype blank form with the correct prefix for dynamic addition in the template
            'blank_formline_count': blank_formline_count,
            }
        return render_template(templt, **contxt)
        # endif form.validate_on_submit()
    else:
        flash('Invalid request method.', 'danger')
        return redirect(url_for('utils.edit_greetings'))
    # endif request.method == 'GET' vs 'POST'
# edit_greetings


############################################################
############################################################

@login_required
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

@superuser_required
def show_table(tblname):
    # showing a table is nothing more than another form
    return form_browse(tblname)
# show_table

