import hashlib
import base64
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from myapp.models import *
from core import *

class LoginHandler(BaseHandler):
    def get(self):

        action = self.request.get('action')

        if action and action == "getSalt":
            username = self.request.get('username')

            q = db.GqlQuery("SELECT * FROM User where username=:1", username)
            user = q.get()

            # TODO - error if user doesn't exist

            self.response.write(user.encr_salt)

        else:

            self.response.write(template.render('templates/login.html', {}))

    def post(self):

        if 'username' in self.session:
            del self.session['username']

        account = self.request.get('account')
        pwd = base64.b64encode(self.request.get('password'))


        q = db.GqlQuery("SELECT * FROM User where username = :1", account)
        user = q.get()

        if user == None:

            public_key = self.request.get('publicKey')
            private_key = self.request.get('privateKey')
            encr_salt = self.request.get('encryptedSalt')

            salt = base64.b64encode(os.urandom(24)) # salt bytes = 24
            hashed_password = hashlib.sha256(salt + pwd).hexdigest()

            new_user = User(username=account, password=hashed_password, salt=salt,
                public_key=public_key, private_key=private_key, encr_salt=encr_salt)

            new_user.put()

            self.session['username'] = account


            # TODO - return success/fail


        else:
            real_hash = user.password
            salt = user.salt

            hashed_password = hashlib.sha256(salt + pwd).hexdigest()

            if real_hash == hashed_password:
                self.session['username'] = account

                # TODO - return success/fail

            else:
                # TODO do something less hacky :)
                self.response.write(
                    template.render('templates/login.html',
                    {'error': "stop hackin'"}))

class LogoutHandler(BaseHandler):

    def get(self):
        if 'username' in self.session:
            del self.session['username']

        self.redirect_to("login")