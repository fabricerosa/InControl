@auth.requires_membership('Manager')
def team_project_list():

    response.title = T("Team")
    #recupera o primeiro argumento, se não redireciona
    projectId = request.args(0)

    project_row = db(db.project.id==projectId).select(db.project.code)
    if project_row != None:
        response.title = T("Team - Project '" +project_row[0].code+"'") 

    query = (db.project_team.project_id==projectId)

    left = (db.team.on(db.project_team.team_id==db.team.id), db.auth_user.on(db.team.user_id==db.auth_user.id), db.role.on(db.team.role_id==db.role.id))

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

    team = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, left=left, details=False,
        create=False, deletable=False, editable=False, maxtextlength=64, paginate=25, searchable=True, user_signature=False)
    
    if not team:
        print "sadfsf"
    	team = 'No team to show'
    
    return dict(team=team)


@auth.requires_membership('Manager')
def team_edit():
    form = SQLFORM(db.team).process()
    return dict(form=form)

@auth.requires_membership('Manager')
def team_list():

    response.title = T("Team")

    query = (db.team)

    left = (db.auth_user.on(db.team.user_id==db.auth_user.id), db.role.on(db.team.role_id==db.role.id))

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
           'team.cost_value': 'Cost'
           }

    #Let's specify a default sort order on description column in grid
    default_sort_order=[db.auth_user.first_name]

    team = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, left=left, details=False,
    create=True, deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, user_signature=False)
    
    return dict(team=team)