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
import webapp2
import json, sys
import utils
from google.appengine.ext import db
from models import *

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')
 
class LoginRequiredHandler(webapp2.RequestHandler):
    def dispatch(self):
        if utils.checkCookie(self.request.get('user'), self.request.cookies.get("PBLOGIN")):
            super(LoginRequiredHandler, self).dispatch()
        else:
            self.abort(403)

class OwnAccountsHandler(LoginRequiredHandler):
    def get(self):
        res = []
        username = self.request.get('user')
        user = User.all().filter("username =", username).get()
        for account_record in StoredAccount.all().filter("user =", user):
          grantees = []
          for shared_account_record in SharedAccount.all().filter("account =", account_record):
            grantees += [shared_account_record.grantee.username] 
          account = {"host_url": account_record.host_url, "host_username": account_record.host_username, "grantees": grantees}
          res += [account]
        resj = json.dumps(res);
        self.response.write(resj)

class GrantedAccountsHandler(LoginRequiredHandler):
    def get(self):
        res = {}
        username = self.request.get('user')
        user = User.all().filter("username =", username).get()
        for shared_account_record in SharedAccount.all().filter("grantee =", user):
            granter = shared_account_record.granter
            if granter.username not in res:
                res[granter.username] = []
            res[granter.username] += [{"host_url": shared_account_record.account.host_url, "host_username": shared_account_record.account.host_username}]
        resj = json.dumps(res);
        self.response.write(resj)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/own_accounts', OwnAccountsHandler),
    ('/granted_accounts', GrantedAccountsHandler)
], debug=True)
