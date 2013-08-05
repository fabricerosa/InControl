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

import string
import datetime
from datetime import timedelta
from plugin_solidform import SOLIDFORM
from plugin_tablecheckbox import TableCheckbox
from plugin_solidtable import SOLIDTABLE
from gluon.contrib.populate import populate

import os     

if auth.is_logged_in():
    user_id = auth.user.id
else:
    user_id = None

db.define_table(
        'project_type',
        Field('name', required=True),
        Field('is_active', 'boolean', default=True), 
        format="%(name)s")
if db(db.project_type).isempty():
        db.project_type.bulk_insert([{'name':'T&M'}, {'name':'Agile'}, {'name':'Product'}, {'name':'Internal'}])

db.define_table(
        'project_state',
        Field('name', required=True),
        Field('is_active', 'boolean', default=True),
        format="%(name)s")
if db(db.project_state).isempty():
        db.project_state.bulk_insert([{'name':'Forecast'}, {'name':'Active'}, {'name':'Suspended'}, {'name':'Canceled'}])

db.define_table(
        'project',
        Field('description', required=True),
        Field('code', required=True, comment='Ex: P_...'),
        Field('odd'),
        Field('type_id', 'reference project_type', required=True),
        Field('state_id', 'reference project_state', required=True),
        Field('total', 'decimal(8,2)', default=0),
        Field('billing_amount', 'decimal(8,2)', default=0),
        Field('recognize_amount', 'decimal(8,2)', default=0),
        Field('anticipated_costs', 'decimal(8,2)', default=0),
        Field('real_costs', 'decimal(8,2)', default=0),
        Field('start_date', 'date', default=request.now, length=10),
        Field('end_date', 'date', default=request.now + timedelta(days=1), length=10),
        Field('created_by', 'reference auth_user', default=user_id),
        Field('created_on', 'datetime', default=request.now),
        Field('is_active', 'boolean', default=True),
        format="%(description)s"
        )

db.define_table(
        'address',
        Field('street_name', required=True),
        Field('locality', required=True),
        Field('postal_code', required=True),
        Field('created_by', 'reference auth_user', default=user_id),
        Field('created_on', 'datetime', default=request.now),        
        format="%(locality)s")

db.define_table(
        'contact',
        Field('email'),
        Field('fax'),
        Field('phone'),
        Field('created_by', 'reference auth_user', default=user_id),
        Field('created_on', 'datetime', default=request.now),        
        )

ENTITY_TYPE = {"client": T("Client"), "provider": T("Provider"), "partner": T("Partner"), "mix": T("Mix")}

db.define_table(
        'entity',
        Field('name', required=True),
        Field('short_name'),
        Field('nif', required=True),
        Field('country_id', 'reference country'),
        Field("entity_type", requires=IS_IN_SET(ENTITY_TYPE), default="client", writable=False),
        Field('address_id', 'reference address'),
        Field('contact_id', 'reference contact'),
        Field('is_active', 'boolean', default=True),
        Field('created_by', 'reference auth_user', default=user_id),
        Field('created_on', 'datetime', default=request.now),        
        format="%(name)s")

db.define_table(
        'acknowledgment_type',
        Field('name', required=True),
        Field('is_active', 'boolean', default=True),
        format="%(name)s")
if db(db.acknowledgment_type).isempty():
        db.acknowledgment_type.bulk_insert([{'name':'Cost'}, {'name':'Profit'}])

db.define_table(
        'acknowledgment',
        Field('type_id', 'reference acknowledgment_type', required=True),
        Field('entity_id', 'reference entity', required=True),
        Field('cost_value', 'decimal(8,2)', default=user_id),
        Field('created_by', 'reference auth_user', default=user_id),
        Field('created_on', 'datetime', default=request.now),
        )

TRANSACTION_TYPE = {"debit": T("Debit"), "credit": T("Credit")}
TRANSACTION_STATE = {"real": T("Real"), "forecast": T("Forecast")}
db.define_table(
        'project_transaction',
        Field('acknowledgment_id', 'reference acknowledgment', required=True),
        Field("transaction_type", requires=IS_IN_SET(TRANSACTION_TYPE), default="credit", writable=False, required=True),
        Field('project_id', 'reference project', required=True),
        Field('reference_date', 'datetime', default=request.now),
        Field('net_value', 'decimal(8,2)', default=user_id),
        Field('vat_value', 'decimal(8,2)', default=user_id),
        Field("transaction_state", requires=IS_IN_SET(TRANSACTION_STATE), default="forecast", writable=False, required=True),
        Field('created_by', 'reference auth_user', default=user_id),
        Field('created_on', 'datetime', default=request.now),
        )


db.define_table(
        'project_billing',
        Field('project_id', 'reference project', required=True),
        Field('client_id', 'reference entity', required=True),
        Field('description', required=True),
        Field('created_by', 'reference auth_user', default=user_id),
        Field('created_on', 'datetime', default=request.now)
        )

db.define_table('role', 
        Field('name', required=True),
        Field('is_active', 'boolean', default=True),
        format="%(name)s")
if db(db.role).isempty():
        db.role.bulk_insert([{'name':'DM'}, {'name':'EM'}, {'name':'DEV'}, {'name':'Senior'}, {'name':'Junior'}, {'name':'Expert'}, {'name':'License'}, {'name':'Costs'}])

db.define_table('team',
        Field('user_id', 'reference auth_user', required=True),
        Field('project_id', 'reference project', required=True),
        Field('role_id', 'reference role', required=True),
        Field('budget', 'integer',default=0),
        Field('rate', 'decimal(8,2)',default=0),
        Field('cost_value', 'decimal(8,2)',default=0),
        )

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.project.description.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'project.description')]
db.project.code.requires = IS_NOT_EMPTY()
db.project.type_id.requires = IS_IN_DB(db, 'project_type.id', 'project_type.name', error_message='enter a value')
db.project.state_id.requires = IS_IN_DB(db, 'project_state.id', 'project_state.name', error_message='enter a value')
db.project.start_date.requires = IS_DATE_IN_RANGE(minimum=request.now.date(), maximum=datetime.date(2099,12,31), format="%Y-%m-%d",error_message="start date must be later than today")
db.project.created_by.readable = False
db.project.created_by.writable = False
db.project.created_on.readable = False
db.project.created_on.writable = False
db.project.id.readable=False
db.project.code.searchable=False
db.project.code.represent = lambda code,row: code.capitalize()

db.team.role_id.requires = IS_IN_DB(db, 'role.id', 'role.name')
db.team.project_id.requires = IS_IN_DB(db, 'project.id', 'project.description')


mail.settings.server = settings.email_server
mail.settings.sender = settings.email_sender
mail.settings.login = settings.email_login
