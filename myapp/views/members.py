import webapp2
from myapp.models import *

import logging
from toolbox.appengine_utilities.sessions import *

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

import json

class LoginRequiredHandler(webapp2.RequestHandler):

    def checkLogin(self, successHandler, **args):
        self.session = Session()
        if not 'username' in self.session:
            logging.debug("not logged in")
            self.redirect_to('login')
        else:
            logging.debug("logged in as: " + self.session.get("username"))
            successHandler(**args)

    def doGet(self, *args):
        ''' defined in derived classes '''
        pass


    def doPost(self, *args):
        '''defined in derived class '''
        pass

    def get(self, **args):
        self.checkLogin(self.doGet, **args)

    def post(self, **args):
        self.checkLogin(self.doPost, **args)

class ShareHandler(LoginRequiredHandler):
    def doGet(self, **args):

        username = self.session.get('username')

        template_dict = {
            'username': username
        }

        self.response.write(template.render('templates/share.html', template_dict))