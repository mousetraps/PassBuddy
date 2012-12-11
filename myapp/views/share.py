from myapp.models import *
from google.appengine.ext.webapp import template
from core import *


class ShareHandler(LoginRequiredHandler):
    def doGet(self, **args):

        username = self.session.get('username')

        template_dict = {
            'username': username
        }

        self.response.write(template.render('templates/share.html', template_dict))

class SharedTableHandler(LoginRequiredHandler):
    def doGet(self, **args):
        username = self.session.get('username')

        q = db.GqlQuery("SELECT * from User where username=:1", username)
        grantee_entity = q.get()

        template_dict = {
            'user': grantee_entity
        }

        self.response.write(template.render("templates/shared_accounts_table.html", template_dict ))

