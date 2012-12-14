from google.appengine.ext.webapp import template
from myapp.views.core import *

class SplashHandler(BaseHandler):
    def get(self):
        # TODO fix code dup with username and templates
        self.response.write(template.render('templates/home.html', { 'username': self.session.get("username") }))

    def how_it_works(self):
        self.response.write(template.render('templates/powerpoint.html', { 'username': self.session.get("username")  }))