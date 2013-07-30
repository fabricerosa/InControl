@auth.requires_membership('Manager')
def team_project_list():

    response.title = T("Team")
    #recupera o primeiro argumento, se não redireciona
    projectId=None
    if len(request.args) == 1:
        projectId = request.args(0)
        if projectId != None:
            project_row = db(db.project.id==projectId).select(db.project.code)
        if project_row != None:
            response.title = T("Team - Project '" +project_row[0].code+"'") 
        query = (db.team.project_id==projectId)
    else:
        query = (db.team)

    if request.args(-2) == 'new' or request.args(-3) == 'edit':
        db.team.project_id.readable=True
        db.team.project_id.writable=False
        db.team.project_id.default = request.args(0,cast=int) or redirect(URL('default','error'))

        
    left = (db.auth_user.on(db.team.user_id==db.auth_user.id), db.role.on(db.team.role_id==db.role.id), db.project.on(db.team.project_id==db.project.id))

    #Define the fields to show on grid.
    fields = (db.auth_user.first_name,
    	db.role.name,
    	db.team.budget,
    	db.team.rate,
    	db.team.cost_value,
		)

    #Define headers as tuples/dictionaries
    headers = {'auth_user.first_name': 'User',
           'role.name': 'Role',
           'team.budget':'Budget',
           'team.rate':'Rate',
           'team.costValue': 'Cost'
           }

    #Let's specify a default sort order on description column in grid
    default_sort_order=[db.auth_user.first_name]

    team = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, left=left, details=True,
        create=True, deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, user_signature=False,
        args=[projectId], onvalidation=check_user)

    
    # newMember = A(SPAN(_class='icon plus icon-plus'),'New Member',_class='w2p_trap button btn',_title='New Member',
    #     _href=URL("team","team_project_edit", args=[projectId]))

    return dict(team=team)
    
@auth.requires_membership('Manager')
def team_project_edit():
    #record = dict(ProjectTeam={'ProjectId':request.args(0), 'TeamId':None})
    form = SQLFORM(db.team)
    return dict(form=form)

@auth.requires_membership('Manager')
def team_edit():
    form = SQLFORM(db.team).process()
    return dict(form=form)

@auth.requires_membership('Manager')
def team_list():

    response.title = T("Team")

    query = (db.team)

    left = (db.auth_user.on(db.team.user_id==db.auth_user.id), db.role.on(db.team.role_id==db.role.id), db.project.on(db.team.project_id==db.project.id))

    #Define the fields to show on grid.
    fields = (db.auth_user.first_name,
        db.role.name,
        db.team.budget,
        db.project.description,
        db.team.rate,
        db.team.cost_value
        )

    #Define headers as tuples/dictionaries
    headers = {'auth_user.first_name': 'User',
           'role.name': 'Role',
           'team.budget':'Budget',
           'team.rate':'Rate',
           'team.cost_value': 'Cost',
           'project.description':'Project'
           }

    #Let's specify a default sort order on description column in grid
    default_sort_order=[db.auth_user.first_name]

    team = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, left=left, details=False,
    create=True, deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, user_signature=False)
    
    return dict(team=team)

def check_user(form):
    query = db.team.user_id == form.vars.user_id
    query &= db.team.project_id == form.vars.project_id
    if db(query).count():
        form.errors.user = "user already exists in this project"
        response.flash = "user already exists in this project"