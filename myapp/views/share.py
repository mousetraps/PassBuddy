import webapp2
from myapp.models import *

import logging

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

import json
from members import *

# TODO MAKE THIS WORK!!!!
class SharedTableHandler(LoginRequiredHandler):
    def doGet(self, **args):
        username = self.session.get('username')

        q = db.GqlQuery("SELECT * from User where username=:1", username)
        grantee_entity = q.get()

        template_dict = {
            'user': grantee_entity
        }

        self.response.write(template.render("templates/shared_accounts_table.html", template_dict ))

