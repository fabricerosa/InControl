#@auth.requires_signature()
@auth.requires_login()

def projectSearch(fields, url):

    buttons = [INPUT(_type='submit',_value=T('Search'), _name='btsearch', _class=''),
        INPUT(_type='submit',_value=T('Clear'), _name='btclear', _class='')]

    fields =[['description', 'code'],
            ['type_id', 'state_id'],
            ['start_date', 'end_date'],
            ['is_active',None]]

    db.project.type_id.default = session['searchValues']['project']['type_id']
    db.project.state_id.default = session['searchValues']['project']['state_id']
    db.project.description.default = session['searchValues']['project']['description']
    db.project.code.default = session['searchValues']['project']['code']
    db.project.start_date.default = session['searchValues']['project']['start_date']
    db.project.end_date.default = session['searchValues']['project']['end_date']
    db.project.is_active.default = session['searchValues']['project']['is_active']

    form = DIV(SOLIDFORM(db.project, fields=fields, buttons=buttons, comments=False, _id='projectSearch', _action=url, _method='post'), _class='divfilters')

    return form

def projects_list():

    queries = []
    
    if not session.searchValues:
        session.searchValues = dict(project={'description':'', 'code':'', 'type_id':None, 'state_id':None, 'start_date':None, 'end_date':None, 'is_active': True})

    if request.vars['btsearch']:
        
      for i in range(len(request.vars)):            
            if request.vars.items()[i][0] in session['searchValues']['project']:
                if str(request.vars.items()[i][0]).find('_date')!= -1:                   
                    session['searchValues']['project'][request.vars.items()[i][0]] =  str_to_dt(request.vars.items()[i][1])
                else:
                     session['searchValues']['project'][request.vars.items()[i][0]] =  request.vars.items()[i][1]          

    elif request.vars['btclear']:      
        for i in range(len(request.vars)):            
            if request.vars.items()[i][0] in session['searchValues']['project']:
                if str(request.vars.items()[i][0]).find('_date')!= -1 or str(request.vars.items()[i][0]).find('_id')!= -1:
                    session['searchValues']['project'][request.vars.items()[i][0]] =  None
                else:
                     session['searchValues']['project'][request.vars.items()[i][0]] =  ''              

    if auth.has_membership('Manager'):
        query = (db.project) 
    else:
        query= ((db.project.id == db.team.project_id) & (db.team.user_id == auth.user_id))


    if session['searchValues']['project']['description'] and str(session['searchValues']['project']['description']).strip() != '':
        queries.append(db.project.description.contains(session['searchValues']['project']['description']))
    if session['searchValues']['project']['code'] and str(session['searchValues']['project']['code']).strip() != '':
        queries.append(db.project.code.contains(session['searchValues']['project']['code']))
    if session['searchValues']['project']['type_id'] and session['searchValues']['project']['type_id'] > 0:
        queries.append(db.project.type_id==session['searchValues']['project']['type_id'])
    if session['searchValues']['project']['state_id'] and session['searchValues']['project']['state_id'] > 0:
        queries.append(db.project.state_id==session['searchValues']['project']['state_id'])
    if session['searchValues']['project']['start_date'] and session['searchValues']['project']['start_date'] != None:
        queries.append(db.project.start_date==session['searchValues']['project']['start_date'])
    if session['searchValues']['project']['end_date'] and session['searchValues']['project']['end_date'] != None:
        queries.append(db.project.end_date==session['searchValues']['project']['end_date'])
    if session['searchValues']['project']['is_active']:
        queries.append(db.project.is_active==session['searchValues']['project']['is_active'])
    if len(queries) > 0:
        query = reduce(lambda a,b:(a&b),queries)
        
    left = (db.project_state.on(db.project.state_id == db.project_state.id), db.project_type.on(db.project.type_id == db.project_type.id))

    #Define the fields to show on grid.
    fields = (db.project.description,
        db.project.code,
        db.project_type.name,
        db.project_state.name,
        db.project.start_date,
        db.project.end_date,
        db.project.created_by,
        db.project.created_on,
        db.project.is_active)

    #Define headers as tuples/dictionaries
    headers = {
           'project.start_date': 'Start date',
           'project_type.name': 'Type',
           'project_state.name': 'State',
           'project.end_date': 'End date',
           'project.is_active': 'Active' }

    #Let's specify a default sort order on description column in grid
    default_sort_order=[db.project.description]

    searchForms = {'project':projectSearch}
   
    edit_new_args = {'linkto': None, 'col3':{'type_id':A('what is this?', _href='http://www.google.com/search?q=define:name', _target='blank')}, 'comments' : True, 
            'buttons': [ TAG.button('Submit', _type="submit", _class='btn-primary'), ' ', TAG.button('Cancel',_type="button",
            _onClick = "parent.location='%s' " % URL('project', 'projects_list'))]}
         
    links = [lambda row: A(SPAN(_class='team'),'Team',_class='w2p_trap button btn',_title='View  Team',
        _href=URL("team","team_project_list", args=[row.id if len(request.args)>1 else row.project.id]))]

    project = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, create=auth.has_membership('Manager'), details=True, 
        deletable=auth.has_membership('Manager'), editable=auth.has_membership('Manager'), maxtextlength=64, paginate=25, searchable=True, links=links, user_signature=False, left=left, 
        search_widget=searchForms, editargs=edit_new_args,createargs=edit_new_args, onvalidation=validate_end_date)

    title='Project List'
  
    # Define the page tilte
    if len(request.args)>1:       
        if  request.args[-2]=='new' and project.create_form:
            title = T('New Project')
        elif  request.args[-3]=='edit':
            title = T('Edit Project')
        elif  request.args[-3]=='view':
            title = T('Project View')

    return dict(projects=project, titles=title)


def validate_end_date(form):
    if form.vars.end_date <= form.vars.start_date:
        form.errors.end_date = T("end date must be later than start date")


    