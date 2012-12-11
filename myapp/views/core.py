import webapp2
import logging

from webapp2_extras import sessions

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)

        try:
            webapp2.RequestHandler.dispatch(self)

        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()


class LoginRequiredHandler(BaseHandler):

    def checkLogin(self, successHandler, **args):

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
