import webapp2
from google.appengine.ext.webapp import template

class SplashHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template.render('templates/home.html', { }))

    def how_it_works(self):
        self.response.write(template.render('templates/powerpoint.html', { }))