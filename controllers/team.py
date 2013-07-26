@auth.requires_membership('Manager')
def team_project_list():

    response.title = T("Team")
    #recupera o primeiro argumento, se não redireciona
    projectId = request.args(0)
    
    project_row = db(db.Project.id==projectId).select(db.Project.Code)
    if project_row != None:
        response.title = T("Team - Project '" +project_row[0].Code+"'") 

    query = (db.ProjectTeam.ProjectId==projectId)
    left = (db.Team.on(db.ProjectTeam.TeamId==db.Team.id), db.auth_user.on(db.Team.UserId==db.auth_user.id), db.Role.on(db.Team.RoleId==db.Role.id))

    #Define the fields to show on grid.
    fields = (db.auth_user.first_name,
    	db.Role.Name,
    	db.Team.Budget,
    	db.Team.Rate,
    	db.Team.CostValue,
		)

    #Define headers as tuples/dictionaries
    headers = {'auth_user.first_name': 'User',
           'Role.Name': 'Role',
           'Team.Budget':'Budget',
           'Team.Rate':'Rate',
           'Team.CostValue': 'Cost'
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
    form = SQLFORM(db.TeamI).process()
    return dict(form=form)

@auth.requires_membership('Manager')
def team_list():

    response.title = T("Team")

    query = (db.Team)
    left = (db.auth_user.on(db.Team.UserId==db.auth_user.id), db.Role.on(db.Team.RoleId==db.Role.id))

    #Define the fields to show on grid.
    fields = (db.auth_user.first_name,
        db.Role.Name,
        db.Team.Budget,
        db.Team.Rate,
        db.Team.CostValue,
        )

    #Define headers as tuples/dictionaries
    headers = {'auth_user.first_name': 'User',
           'Role.Name': 'Role',
           'Team.Budget':'Budget',
           'Team.Rate':'Rate',
           'Team.CostValue': 'Cost'
           }

    #Let's specify a default sort order on description column in grid
    default_sort_order=[db.auth_user.first_name]

    team = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, left=left, details=False,
    create=True, deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, user_signature=False)
    
    return dict(team=team)