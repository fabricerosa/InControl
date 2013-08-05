@auth.requires_membership('Manager')
def entity_list():


    query = (db.entity)

    #left = (db.auth_user.on(db.team.user_id==db.auth_user.id), db.role.on(db.team.role_id==db.role.id), db.project.on(db.team.project_id==db.project.id))
    left = None

    #Define the fields to show on grid.
    fields = (db.entity.name, db.entity.nif)

    #Define headers as tuples/dictionaries
    headers = {'entity.name': 'Name',
           'db.entity.nif':'NIF'
           }
    
    default_sort_order=[db.entity.name]

    entities = SQLFORM.grid(query=query, fields=fields, headers=headers, orderby=default_sort_order, left=left, details=False,
    create=True, deletable=False, editable=True, maxtextlength=64, paginate=25, searchable=True, user_signature=False)
    
    return dict(entities=entities)