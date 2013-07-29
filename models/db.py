# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()


## create all tables needed by auth if not custom tables
auth.settings.extra_fields[auth.settings.table_user_name] = [Field('isExternal', 'boolean', default=True)]
auth.define_tables(username=False, signature=False)


## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.actions_disabled=['change_password','request_reset_password','retrieve_username','register']
auth.next = None
auth.settings.login_next = URL('default','dashboard')


auth.messages.logged_in = ''
auth.messages.logged_out = ''


## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

import datetime

if auth.is_logged_in():
    user_id = auth.user.id
else:
    user_id = None

db.define_table(
        'Project_Type',
        Field('Name', required=True),
        Field('isActive', 'boolean', default=True)
        )
if db(db.Project_Type).isempty():
        db.Project_Type.bulk_insert([{'Name':'T&M'}, {'Name':'Agile'}, {'Name':'Product'}, {'Name':'Internal'}])

db.define_table(
        'Project_State',
        Field('Name', required=True),
        Field('isActive', 'boolean', default=True)
        )
if db(db.Project_State).isempty():
        db.Project_State.bulk_insert([{'Name':'Forecast'}, {'Name':'Active'}, {'Name':'Suspended'}, {'Name':'Canceled'}])

db.define_table(
        'Project',
        Field('Description', required=True),
        Field('Code', required=True),
        Field('TypeId', db.Project_Type, required=True),
        Field('StateId', db.Project_State , required=True),
        Field('StartDate', 'datetime', default=request.now),
        Field('EndDate', 'datetime', default=request.now),
        Field('Created_by', db.auth_user, default=user_id),
        Field('Created_on', 'datetime', default=request.now),
        Field('isActive', 'boolean', default=True)
        )

db.define_table('Role', 
        Field('Name', required=True),
        Field('isActive', 'boolean', default=True)
        )

if db(db.Role).isempty():
        db.Role.bulk_insert([{'Name':'DM'}, {'Name':'EM'}, {'Name':'DEV'}, {'Name':'Senior'}, {'Name':'Junior'}, {'Name':'Expert'}])

db.define_table('Team',
        Field('UserId', db.auth_user, required=True),
        Field('RoleId', db.Role, required=True),
        Field('Budget', 'integer',default=''),
        Field('Rate', 'decimal(8,2)',default=''),
        Field('CostValue', 'decimal(8,2)',default='')
        )

db.define_table('ProjectTeam',
        Field('TeamId', db.Team, required=True),
        Field('ProjectId', db.Project, required=True),
        )

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.Project.Description.requires = True
db.Project.Code.requires = True
db.Project.TypeId.requires = IS_IN_DB(db, 'Project_Type.id', 'Project_Type.Name')
db.Project.StateId.requires = IS_IN_DB(db, 'Project_State.id', 'Project_State.Name')
db.Project.Created_by.readable = False
db.Project.Created_by.writable = False
db.Project.Created_on.readable = False
db.Project.Created_on.writable = False
db.Project.id.readable=False
db.Project.Code.searchable=False



db.Team.RoleId.requires = IS_IN_DB(db, 'Role.id', 'Role.Name')

db.ProjectTeam.TeamId.requires = IS_IN_DB(db, 'Team.id', '')
db.ProjectTeam.ProjectId.requires = IS_IN_DB(db, 'Project.id', 'Project.Description')

mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
