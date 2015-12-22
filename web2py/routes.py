# -*- coding: utf-8 -*-

default_application = 'scoreboard'    # ordinarily set in base routes.py
default_controller = 'default'  # ordinarily set in app-specific routes.py
default_function = 'index'   # ordinarily set in app-specific routes.py

BASE = ''  # optional prefix for incoming URLs

routes_in = (
    # do not reroute admin unless you want to disable it
    (BASE + '/admin', '/admin/default/index'),
    (BASE + '/admin/$anything', '/admin/$anything'),

    # do not reroute real applications
    (BASE + '/scoreboard/$anything' ,'/scoreboard/$anything'),

    # route everything else to /scoreboard
    (BASE + '/$anything', '/scoreboard/$anything'),

    # reroute favicon and robots, use exable for lack of better choice
    ('/favicon.png', '/scoreboard/static/images/favicon.png'),
    ('/favicon.ico', '/scoreboard/static/images/favicon.ico'),
    ('/robots.txt', '/scoreboard/static/robots.txt'),

    # remove the BASE prefix
    (BASE + '/$anything', '/$anything'),
)

# routes_out, like routes_in translates URL paths created with the web2py URL()
# function in the same manner that route_in translates inbound URL paths.

routes_out = (
    # do not reroute admin unless you want to disable it
    ('/admin/$anything', BASE + '/admin/$anything'),

    # do not reroute /scoreboard/admin
    ('/scoreboard/admin/$anything', BASE + '/scoreboard/admin/$anything'),

    # hide unnecessary /scoreboard path link
    ('/scoreboard/$anything' ,BASE + '/$anything'),

    # do other stuff
    (r'/app(?P<any>.*)', r'\g<any>'),

    # restore the BASE prefix
    ('/$anything', BASE + '/$anything'),
)
