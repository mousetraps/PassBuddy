from _codecs import decode
import webapp2
from myapp.models import *

import logging

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

import json
from members import *

from toolbox.decode import *

class DecryptPasswordHandler(LoginRequiredHandler):
    def doGet(self, **args):
        username = self.session.get("username")

        # TODO allow_multiple is deprecated...
        d = self.request.get("d[]", allow_multiple=True)
        p = self.request.get("p[]", allow_multiple=True)
        q = self.request.get("q[]", allow_multiple=True)

        p = [int(numeric_string) for numeric_string in p]
        q = [int(numeric_string) for numeric_string in q]
        d = [int(numeric_string) for numeric_string in d]

        key = self.request.get("key")
        shared_account = db.get(key)

        if shared_account.grantee.username == username:
            encrypted_password = shared_account.encr_grantee_password
            loginPassword = rsaDecode([d, p, q], encrypted_password)
            self.response.write(loginPassword)
