#@auth.requires_signature()
#@auth.requires_login()
@auth.requires_membership('Manager')

def emptySearchWidget(fields, url):
    form = FORM()
    
    return form

def projectSearch(fields, url):

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
        _action=url, _method='post')
    
    return form

def identification(row):
    ident= row.project.id   
    return ident


def projects_list():

    queries = []
    constraints = None

    if not session.searchValues:
        session.searchValues = dict(project={'type_id':'', 'state_id':'', 'description':''})

    #  Get filters
    projectTypeId = session['searchValues']['project']['type_id']
    projectStateId = session['searchValues']['project']['state_id']
    searchText = session['searchValues']['project']['description']
    
    if request.vars['btsearch']:
        projectTypeId = request.vars.projectType
        projectStateId = request.vars.projectState
        searchText = request.vars.searchText
        try:
            projectTypeId = int(projectTypeId)
        except:
            projectTypeId = None

        try:
            projectStateId = int(projectStateId)
        except:
            projectStateId = None

    elif request.vars['btclear']:
        projectTypeId = None
        projectStateId = None
        searchText = ''

    if request.vars['btsearch'] or request.vars['btclear']:
        session['searchValues']['project']['type_id'] = projectTypeId
        session['searchValues']['project']['state_id'] = projectStateId
        session['searchValues']['project']['description'] = searchText

    #Define the query object.
    #query=((db.Project.TypeId==db.Project_Type.id) & (db.Project.StateId == db.Project_State.id))
    if auth.has_membership('Manager'):
        query = (db.project) 
    else:
        query= ((db.project.id == db.team.project_id) & (db.team.user_id == auth.user_id))

    if searchText and searchText.strip() != '':
        queries.append(db.project.description.contains(searchText) | db.project.code.contains(searchText))
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

    if len(request.args)>1: 
        if request.args[-2]=='new':
            formargs={'linkto': None, 'col3':{'code':A('what is this?', _href='http://www.google.com/search?q=define:name', _target='blank')}, 'comments' : True, 
            'buttons': [ TAG.button('Submit', _type="submit", _class='btn-primary'), ' ', TAG.button('Cancel',_type="button",
            _onClick = "parent.location='%s' " % URL('project', 'projects_list'))], '_style':'border:1px solid #cccccc'}
        elif request.args[-3]=='edit':
            formargs={'linkto': None, 'col3':{'Code':A('what is this?', _href='http://www.google.com/search?q=define:name', _target='blank')}, 'comments' : True, 
            'buttons': [ TAG.button('Submit', _type="submit", _class='btn-primary'), ' ', TAG.button('Cancel',_type="button",
            _onClick = "parent.location='%s' " % URL('project', 'projects_list'))], '_style':'border:1px solid #cccccc'}
        else:
            formargs={'_style':'border:1px solid #cccccc'}
    else : 
        formargs={}

    #links = [lambda row: A('View Team',_href=URL("project","projects_edit",args=[row.id]))]
    links = [lambda row: A(SPAN(_class='team'),'Team',_class='w2p_trap button btn',_title='View  Team',
        _href=URL("team","team_project_list", args=[row.id if len(request.args)>1 else row.project.id]))]

    #project = SQLTABLE(db().select(db.Project.ALL),headers='fieldname:capitalize')
    project = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, create=auth.has_membership('Manager'), details=True, 
        deletable=False, editable=auth.has_membership('Manager'), maxtextlength=64, paginate=25, searchable=True, links=links, user_signature=False, left=left, 
        search_widget=searchForms, formargs = formargs, onvalidation=validate_end_date)

    title='Project List'
  
    if len(request.args)>1:       
        if  request.args[-2]=='new' and project.create_form:
            title = 'New Project'
        elif  request.args[-3]=='edit':
            title = 'Edit Project'
        elif  request.args[-3]=='view':
            title = 'Project View'

    return dict(projects=project, titles=title)


def validate_end_date(form):
    if form.vars.end_date <= form.vars.start_date:
        form.errors.end_date = "end date must be later than start date"
    