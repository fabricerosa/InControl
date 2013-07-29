#@auth.requires_signature()
#@auth.requires_login()
@auth.requires_membership('Manager')

def emptySearchWidget(fields, url):
    form = FORM()
    
    return form

def projectSearch(fields, url):

    #  Build drop-down list for project type
    projectTypes = db(db.Project_Type.id > 0).select(orderby=db.Project_Type.Name)
    optionsType = [OPTION(projectTypes[i].Name, 
                      _value=str(projectTypes[i].id)) for i in range(len(projectTypes))]
    optionsTypeAdded=optionsType[:]
    optionsTypeAdded.insert(0, OPTION('- All -', _value='0'))

    #  Build drop-down list for project state
    projectStates = db(db.Project_State.id > 0).select(orderby=db.Project_State.Name)
    optionsState = [OPTION(projectStates[i].Name, 
                      _value=str(projectStates[i].id)) for i in range(len(projectStates))]
    optionsStateAdded=optionsState[:]
    optionsStateAdded.insert(0, OPTION('- All -', _value='0'))

    form = FORM(DIV(
        LABEL(' '),        
        'Project Type: ', SELECT(_name='projectType', _id="projectType", 
                       _style="width:150px;", 
                       value=session.searchValues['Project']['TypeId'],
                       *optionsTypeAdded),
        '  Project State: ',SELECT(_name='projectState', _id="projectState", 
                       _style="width:150px;", 
                       value=session.searchValues['Project']['StateId'],
                       *optionsStateAdded),
        INPUT(_name='searchText',_value=session.searchValues['Project']['Description'],
              _style='width:200px;',
              _id='searchText', _placeholder='Type the Project name'),
        INPUT(_type='submit',_value=T('Search'), _name='btsearch', _class=''),
        INPUT(_type='submit',_value=T('Clear'), _name='btclear', _class=''), _id="filters", _class='divfilters'),
        _id='projectSearch',
        _action=url, _method='post')
    
    return form

def identification(row):
    ident= row.Project.id   
    return ident


def projects_list():

    queries = []
    constraints = None

    if not session.searchValues:
        session.searchValues = dict(Project={'TypeId':'', 'StateId':'', 'Description':''})

    #  Get filters
    projectTypeId = session['searchValues']['Project']['TypeId']
    projectStateId = session['searchValues']['Project']['StateId']
    searchText = session['searchValues']['Project']['Description']
    
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
        session['searchValues']['Project']['TypeId'] = projectTypeId
        session['searchValues']['Project']['StateId'] = projectStateId
        session['searchValues']['Project']['Description'] = searchText

    #Define the query object.
    #query=((db.Project.TypeId==db.Project_Type.id) & (db.Project.StateId == db.Project_State.id))

    query = (db.Project)

    if searchText and searchText.strip() != '':
        queries.append(db.Project.Description.contains(searchText) | db.Project.Code.contains(searchText))
    if projectTypeId and projectTypeId > 0:
        queries.append(db.Project.TypeId==projectTypeId)
    if projectStateId and projectStateId > 0:
        queries.append(db.Project.StateId==projectStateId)
    if len(queries) > 0:
        query = reduce(lambda a,b:(a&b),queries)
        
    left = (db.Project_State.on(db.Project.StateId == db.Project_State.id), db.Project_Type.on(db.Project.TypeId == db.Project_Type.id))

    #Define the fields to show on grid.
    fields = (db.Project.Description,
        db.Project.Code,
        db.Project_Type.Name,
        db.Project_State.Name,
        db.Project.StartDate,
        db.Project.EndDate,
        db.Project.Created_by,
        db.Project.Created_on,
        db.Project.isActive)

    #Define headers as tuples/dictionaries
    headers = {
           'Project.StartDate': 'Start date',
           'Project_Type.Name': 'Type',
           'Project_State.Name': 'State',
           'Project.EndDate': 'End date',
           'Project.isActive': 'Active' }

    #Let's specify a default sort order on description column in grid
    default_sort_order=[db.Project.Description]

    searchForms = {'Project':projectSearch}

    if len(request.args)>1 and request.args[-3]=='edit':
        formargs={'linkto': None, 'col3':{'Code':A('what is this?', _href='http://www.google.com/search?q=define:name', _target='blank')}, 'comments' : True, 
        'buttons': [ TAG.button('Submit', _type="submit", _class='btn-primary'), ' ', TAG.button('Cancel',_type="button",_onClick = "parent.location='%s' " % URL('project', 'projects_list'))]}
    elif len(request.args)>1 and request.args[-3]=='view':
        formargs={}

    #links = [lambda row: A('View Team',_href=URL("project","projects_edit",args=[row.id]))]
    links = [lambda row: A(SPAN(_class='team'),'Team',_class='w2p_trap button btn',_title='View  Team',
        _href=URL("team","team_project_list", args=[row.id if len(request.args)>1 else row.Project.id]))]

    #project = SQLTABLE(db().select(db.Project.ALL),headers='fieldname:capitalize')
    project = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, create=True, details=True, 
        deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, links=links, user_signature=False, left=left, 
        search_widget=searchForms, formargs = formargs)

    title='Project List'
  
    if len(request.args)>1:
        print request.args[-3]

    if  len(request.args)>1 and request.args[-2]=='new' and project.create_form:
        title = 'New Project'
    elif  len(request.args)>1 and request.args[-3]=='edit':
        title = 'Edit Project'
    elif  len(request.args)>1 and request.args[-3]=='view':
        title = 'Project View'

    return dict(projects=project, titles=title)