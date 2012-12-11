import webapp2

from google.appengine.ext.webapp import template

class SplashHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect_to('login')