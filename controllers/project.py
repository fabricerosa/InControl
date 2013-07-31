#@auth.requires_signature()
#@auth.requires_login()
@auth.requires_membership('Manager')

def projectSearch(fields, url):

    buttons = [INPUT(_type='submit',_value=T('Search'), _name='btsearch', _class=''),
        INPUT(_type='submit',_value=T('Clear'), _name='btclear', _class='')]

    db.project.type_id.default = session['searchValues']['project']['type_id']
    db.project.state_id.default = session['searchValues']['project']['state_id']
    db.project.description.default = session['searchValues']['project']['description']
    db.project.code.default = session['searchValues']['project']['code']
    db.project.start_date.default = session['searchValues']['project']['start_date']
    db.project.end_date.default = session['searchValues']['project']['end_date']
    db.project.is_active.default = session['searchValues']['project']['is_active']

    '''db.project.start_date.default = None
    db.project.end_date.default = None'''


    form = SQLFORM(db.project, buttons=buttons, comments=False, _id='projectSearch', _action=url, _method='post', _style='background-color: #FAFAFA; padding: 10px; margin-top: 10px;')

    return form

'''
    #  Build drop-down list for project type
    projectTypes = db(db.project_type.id > 0).select(orderby=db.project_type.name)
    optionsType = [OPTION(projectTypes[i].name, 
                      _value=str(projectTypes[i].id)) for i in range(len(projectTypes))]
    optionsTypeAdded=optionsType[:]
    optionsTypeAdded.insert(0, OPTION('- All -', _value='0'))

    #  Build drop-down list for project state
    projectStates = db(db.project_state.id > 0).select(orderby=db.project_state.name)
    optionsState = [OPTION(projectStates[i].name, 
                      _value=str(projectStates[i].id)) for i in range(len(projectStates))]
    optionsStateAdded=optionsState[:]
    optionsStateAdded.insert(0, OPTION('- All -', _value='0'))

    form = FORM(DIV(
        LABEL(' '),        
        'Project Type: ', SELECT(_name='projectType', _id="projectType", 
                       _style="width:150px;", 
                       value=session.searchValues['project']['type_id'],
                       *optionsTypeAdded),
        '  Project State: ',SELECT(_name='projectState', _id="projectState", 
                       _style="width:150px;", 
                       value=session.searchValues['project']['state_id'],
                       *optionsStateAdded),
        INPUT(_name='searchText',_value=session.searchValues['project']['description'],
              _style='width:200px;',
              _id='searchText', _placeholder='Type the Project name'),
        INPUT(_type='submit',_value=T('Search'), _name='btsearch', _class=''),
        INPUT(_type='submit',_value=T('Clear'), _name='btclear', _class=''), _id="filters", _class='divfilters'),
        _id='projectSearch',
        _action=url, _method='post')'''
    
   


def projects_list():

    queries = []
    constraints = None

    if not session.searchValues:
        session.searchValues = dict(project={'description':'', 'code':'', 'type_id':None, 'state_id':None, 'start_date':None, 'end_date':None, 'is_active': True})

    #  Get filters
    projectTypeId = session['searchValues']['project']['type_id']
    projectStateId = session['searchValues']['project']['state_id']
    description = session['searchValues']['project']['description']
    code = session['searchValues']['project']['code']
    start_date = session['searchValues']['project']['start_date']
    end_date = session['searchValues']['project']['end_date']
    is_active = session['searchValues']['project']['is_active']
    
    if request.vars['btsearch']:
        description = request.vars.description
        code = request.vars.code        
        start_date = (request.vars.start_date)
        end_date = (request.vars.end_date)
        is_active = request.vars.is_active

        try:
            projectTypeId = int(request.vars.type_id)
        except:
            projectTypeId = None

        try:
            projectStateId = int(request.vars.state_id)
        except:
            projectStateId = None



    elif request.vars['btclear']:
        projectTypeId = None
        projectStateId = None
        description = ''
        code = ''
        start_date = None
        end_date = None
        is_active = True


    if request.vars['btsearch'] or request.vars['btclear']:
        session['searchValues']['project']['type_id'] = projectTypeId
        session['searchValues']['project']['state_id'] = projectStateId
        session['searchValues']['project']['description'] = description
        session['searchValues']['project']['code'] = code        
        session['searchValues']['project']['start_date'] = str_to_dt(start_date)
        session['searchValues']['project']['end_date'] = str_to_dt(end_date)
        session['searchValues']['project']['is_active'] = is_active

    query = (db.project)

    if description and description.strip() != '':
        queries.append(db.project.description.contains(description))
    if code and code.strip() != '':
        queries.append(db.project.code.contains(code))
    if projectTypeId and projectTypeId > 0:
        queries.append(db.project.type_id==projectTypeId)
    if projectStateId and projectStateId > 0:
        queries.append(db.project.state_id==projectStateId)
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
            _onClick = "parent.location='%s' " % URL('project', 'projects_list'))], '_style':'border:1px solid #cccccc'}
        
    viewargs = {'_style':'border:1px solid #cccccc'}
   
    links = [lambda row: A(SPAN(_class='team'),'Team',_class='w2p_trap button btn',_title='View  Team',
        _href=URL("team","team_project_list", args=[row.id if len(request.args)>1 else row.project.id]))]

    project = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, create=True, details=True, 
        deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, links=links, user_signature=False, left=left, 
        search_widget=searchForms, editargs=edit_new_args,createargs=edit_new_args, viewargs=viewargs, onvalidation=validate_end_date)

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

def str_to_dt(dte):
    dte = str(dte)
    dte = string.strip(dte)
    if len(dte) == 10:
        y = int(dte[0:4])
        m = int(dte[5:7])
        d = int(dte[9:])
        return datetime.date(y, m, d) 
    