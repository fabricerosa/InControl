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

    form = FORM(
        LABEL(' '),        
        'Project Type: ', SELECT(_name='projectType', _id="projectType", 
                       _style="width:150px;", 
                       value=session.searchValues['Project']['TypeId'],
                       *optionsTypeAdded),
        '  Project State: ',SELECT(_name='projectState', _id="projectState", 
                       _style="width:150px;", 
                       value=session.searchValues['Project']['StateId'],
                       *optionsStateAdded),
        INPUT(_name='searchText',_value=session.searchValues['Project']['Name'],
              _style='width:200px;',
              _id='searchText', _placeholder='Type the Project name'),
        INPUT(_type='submit',_value=T('Search'), _name='btsearch', _class=''),
        INPUT(_type='submit',_value=T('Clear'), _name='btclear'),
        _id='projectSearch',
        _action=url, _method='post')
    
    return form

def projects_list():

    queries = []
    constraints = None

    #  Get filters
    if not session.searchValues:
        session.searchValues = dict(Project={'TypeId':'', 'StateId':'', 'Name':''})

    projectTypeId = session['searchValues']['Project']['TypeId']
    projectStateId = session['searchValues']['Project']['StateId']
    searchText = session['searchValues']['Project']['Name']
    
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
        session['searchValues']['Project']['Name'] = searchText

    #Define the query object.
    #query=((db.Project.TypeId==db.Project_Type.id) & (db.Project.StateId == db.Project_State.id))

    query = (db.Project)

    if searchText and searchText.strip() != '':
        queries.append(db.Project.Name.contains(searchText))
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

    #links = [lambda row: A('View Team',_href=URL("project","projects_edit",args=[row.id]))]
    links = [lambda row: A(SPAN(_class='icon magnifier'),'Team',_class='w2p_trap button btn',_title='View  Team',
    	_href=URL("team","team_project_list",args=[row.Project.id]))]

    #project = SQLTABLE(db().select(db.Project.ALL),headers='fieldname:capitalize')
    project = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, create=True, 
    	deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, links=links, user_signature=False, left=left, 
        search_widget=searchForms)

    return dict(projects=project)


@auth.requires_membership('Manager')
def projects_edit():
	# create an insert form from the table
    form = SQLFORM(db.Project).process()
    return dict(form=form)

