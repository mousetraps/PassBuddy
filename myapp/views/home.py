import webapp2

class SplashHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect_to('login')