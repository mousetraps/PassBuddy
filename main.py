#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from distutils.command.config import config
import webapp2

from myapp.views.login import *
from myapp.views.core import *
from myapp.views.home import *
from myapp.views.manage import *
from myapp.views.share import *
from myapp.views.proxy import *

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
    }

app = webapp2.WSGIApplication([
    webapp2.Route('/', handler=SplashHandler, name='home'),
    webapp2.Route('/login', handler=LoginHandler, name='login'),
    webapp2.Route('/loginGuest', handler=LoginGuestHandler, name='loginGuest'),
    webapp2.Route('/mirror', handler=MirrorHandler, name='mirror'),
    webapp2.Route('/manage', handler=ManageHandler, name='manage'),
    webapp2.Route('/share', handler=ShareHandler, name='share'),
    webapp2.Route('/logout', handler=LogoutHandler, name='logout'),
    webapp2.Route('/table', handler=ManagedTableHandler, name='table'),
    webapp2.Route('/sharedTable', handler=SharedTableHandler, name='sharedTable'),
    webapp2.Route('/logs', handler=LogsHandler, name='logs'),
    webapp2.Route('/detect_login_form', handler=DetectLoginFormHandler, name='detect_login_form'),
    webapp2.Route('/decrypt', handler=DecryptPasswordHandler, name='decrypt'),
    webapp2.Route('/how-it-works', handler=SplashHandler, handler_method='how_it_works')
], debug=True, config=config)
