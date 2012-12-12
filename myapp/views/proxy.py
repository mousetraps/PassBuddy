from myapp.models import *
from core import *
from toolbox.decode import *
from toolbox import programmatic_login_utils

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

class DetectLoginFormHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get("url")
        self.response.out.write(programmatic_login_utils.detect_login_form(url))
