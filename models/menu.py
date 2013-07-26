response.title = settings.title
response.subtitle = settings.subtitle
response.logo = A('Do iT Lean',
                  _class="brand",_href=URL('default','index'))
response.logoBanner = IMG(_src=URL('static','images/LogoBanner.png'), _alt="Banner")
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Dashboard'),URL('default','dashboard')==URL(),URL('default','dashboard'),[]),
(T('Projects'),URL('project','projects_list')==URL(),URL('project','projects_list'),[]),
(T('Team'),URL('team','team_list')==URL(),URL('team','team_list'),[]),
]