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
import json, hashlib, random, string, os
import utils
import jinja2
from models import *

ON_DEV = False

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CheckLoginHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.username = utils.checkCookie(self.request.cookies.get("PBLOGIN"))
        super(CheckLoginHandler, self).dispatch()

class LoginRequiredHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.username = utils.checkCookie(self.request.cookies.get("PBLOGIN"))
        if self.username != None:
            super(LoginRequiredHandler, self).dispatch()
        else:
            self.abort(403)

class MainHandler(CheckLoginHandler):
    def get(self):
        #self.response.write('Hello world!')
        template_file = "index.html" if self.username != None else "login.html"
        template = jinja_environment.get_template(template_file)
        self.response.out.write(template.render({}))

class RegisterHandler(webapp2.RequestHandler):
    SALT_LENGTH = 20
    def post(self):
        username = self.request.get("username")
        exists = User.all().filter("username =", username).get()
        if exists != None:
            self.response.write(json.dumps({"status": "ERROR", "error": "There is already a user with that username. Choose another."}))
            return
        pwhash = self.request.get("password")
        user = User()
        user.username = username
        user.salt = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(self.SALT_LENGTH))
        h = hashlib.sha256()
        h.update(user.salt + pwhash)
        user.pw_hsh = h.hexdigest()
        user.token = utils.generateCookie(username)
        user.put()
        self.response.set_cookie("PBLOGIN", user.token, max_age=utils.cookieExpiration(), secure=not(ON_DEV))
        self.response.write(json.dumps({"status": "OK"}))

class LoginHandler(webapp2.RequestHandler):
    def post(self):
        username = self.request.get("username")
        user = User.all().filter("username =", username).get()
        if user == None:
            self.response.write(json.dumps({"status": "ERROR", "error": "There is no user with that username."}))
            return
        pwhash = self.request.get("password")
        h = hashlib.sha256()
        h.update(user.salt + pwhash)
        if user.pw_hsh != h.hexdigest():
            self.response.write(json.dumps({"status": "ERROR", "error": "Incorrect password."}))
            return
        newcookie = utils.generateCookie(username)
        user.token = newcookie
        user.put()
        expiration = utils.cookieExpiration()
        self.response.set_cookie("PBLOGIN", user.token, max_age=expiration, secure=not(ON_DEV))
        self.response.write(json.dumps({"status": "OK"}))

class LogoutHandler(LoginRequiredHandler):
    def get(self):
        self.response.delete_cookie("PBLOGIN")
        self.redirect("/")

class OwnAccountsHandler(LoginRequiredHandler):
    def get(self):
        res = []
        #username = self.request.get('user')
        username = self.username
        user = User.all().filter("username =", username).get()
        if user == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with your username! Are you logged in?"}))
            return
        for account_record in StoredAccount.all().filter("user =", user):
          grantees = []
          for shared_account_record in SharedAccount.all().filter("account =", account_record):
            grantees += [shared_account_record.grantee.username] 
          account = {"host_url": account_record.host_url, "host_username": account_record.host_username, "grantees": grantees}
          res += [account]
        resj = json.dumps({"status": "OK", "username": username, "accounts": res});
        self.response.write(resj)

class GrantedAccountsHandler(LoginRequiredHandler):
    def get(self):
        res = {}
        #username = self.request.get('user')
        username = self.username
        user = User.all().filter("username =", username).get()
        if user == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with your username! Are you logged in?"}))
            return
        for shared_account_record in SharedAccount.all().filter("grantee =", user):
            granter = shared_account_record.granter
            if granter.username not in res:
                res[granter.username] = []
            res[granter.username] += [{"host_url": shared_account_record.account.host_url, "host_username": shared_account_record.account.host_username}]
        resj = json.dumps({"status": "OK", "username": username, "accounts": res});
        self.response.write(resj)

class AddAccountHandler(LoginRequiredHandler):
    def post(self):
        username = self.username
        user = User.all().filter("username =", username).get()
        if user == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with your username! Are you logged in?"}))
            return
        account = StoredAccount()
        account.user = user
        account.host_url = self.request.get("host_url")
        account.host_username = self.request.get("host_username")
        account.host_password = self.request.get("host_password")
        account.put()
        resj = json.dumps({"status": "OK", "username": username})
        self.response.write(resj)

class RemoveAccountHandler(LoginRequiredHandler):
    def post(self):
        username = self.username
        user = User.all().filter("username =", username).get()
        if user == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with your username! Are you logged in?"}))
            return
        host_url = self.request.get("host_url")
        host_username = self.request.get("host_username")
        account = StoredAccount.all().filter("user =", user).filter("host_url =", host_url).filter("host_username =", host_username).get()
        if account == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "No such account exists."}))
            return
        # May have to worry about other users performing queries
        # involving these accounts that are being deleted /while/ they
        # are being deleted... be careful.
        for shared_account in SharedAccount.all().filter("account =", account):
            shared_account.delete()
        account.delete()
        resj = json.dumps({"status": "OK", "username": username})
        self.response.write(resj)

class ShareAccountHandler(LoginRequiredHandler):
    def post(self):
        username = self.username
        user = User.all().filter("username =", username).get()
        if user == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with your username! Are you logged in?"}))
            return
        grantee_username = self.request.get("grantee_username")
        grantee = User.all().filter("username =", grantee_username).get()
        if grantee == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with that username."}))
            return
        host_url = self.request.get("host_url")
        host_username = self.request.get("host_username")
        account = StoredAccount.all().filter("user =", user).filter("host_url =", host_url).filter("host_username =", host_username).get()
        if account == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "No such account exists."}))
            return
        shared_account = SharedAccount()
        shared_account.granter = user
        shared_account.account = account
        shared_account.grantee = grantee
        shared_account.put()
        resj = json.dumps({"status": "OK", "username": username})
        self.response.write(resj)

class UnshareAccountHandler(LoginRequiredHandler):
    def post(self):
        username = self.username
        user = User.all().filter("username =", username).get()
        if user == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with your username! Are you logged in?"}))
            return
        grantee_username = self.request.get("grantee_username")
        grantee = User.all().filter("username =", grantee_username).get()
        if grantee == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "There is no user with that username."}))
            return
        host_url = self.request.get("host_url")
        host_username = self.request.get("host_username")
        account = StoredAccount.all().filter("user =", user).filter("host_url =", host_url).filter("host_username =", host_username).get()
        if account == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "No such account exists."}))
            return
        shared_account = SharedAccount.all().filter("account =", account).filter("grantee =", grantee).get()
        if shared_account == None:
            self.response.write(json.dumps({"status": "ERROR", "username": username, "error": "That account is not shared with that user."}))
            return
        shared_account.delete()
        resj = json.dumps({"status": "OK", "username": username})
        self.response.write(resj)        

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/register', RegisterHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/own_accounts', OwnAccountsHandler),
    ('/granted_accounts', GrantedAccountsHandler),
    ('/add_account', AddAccountHandler),
    ('/remove_account', RemoveAccountHandler),
    ('/share', ShareAccountHandler),
    ('/unshare', UnshareAccountHandler)
], debug=True)
