import webapp2
from google.appengine.ext.webapp import template

class SplashHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect_to('login')

    def how_it_works(self):
        self.response.write(template.render('templates/powerpoint.html', { }))