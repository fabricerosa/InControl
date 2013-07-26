from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'InControl'
settings.subtitle = 'Do iT Lean'
settings.author = 'Do iT Lean'
settings.author_email = 'info@doitlean.com'
settings.keywords = 'doitlean, application, internal'
settings.description = 'Internal Control Application'
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '9ccc16e1-bb27-4ef7-8e05-4bc43337f21f'
settings.email_server = 'localhost'
settings.email_sender = 'info@doitlean.com'
settings.email_login = 'info@doitlean.com'
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
