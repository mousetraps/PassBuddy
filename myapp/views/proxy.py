import json
from myapp.models import *
from core import *
from toolbox.decode import *
from toolbox import programmatic_login_utils

def decryptPasswordForGuest(guest_username, d, p, q, shared_account):
    p = [int(numeric_string) for numeric_string in p]
    q = [int(numeric_string) for numeric_string in q]
    d = [int(numeric_string) for numeric_string in d]


    shared_password = None
    if shared_account.grantee.username == guest_username:
	encrypted_shared_password = shared_account.encr_grantee_password
	shared_password = rsaDecode([d, p, q], encrypted_shared_password)
    return shared_password


class DecryptPasswordHandler(LoginRequiredHandler):
    def doGet(self, **args):
        current_username = self.session.get("username")

        # TODO allow_multiple is deprecated...
        d = self.request.get("d[]", allow_multiple=True)
        p = self.request.get("p[]", allow_multiple=True)
        q = self.request.get("q[]", allow_multiple=True)

        shared_account_key = self.request.get("key")
        shared_account = db.get(shared_account_key)
 
        self.response.write(decryptPasswordForGuest(current_username, d, p, q, shared_account))


class MirrorHandler(LoginRequiredHandler):
    def doGet(self, **args):
        cookies = []
        shared_url = self.request.get("url")

        have_cookies = False #TODO: check in database
        if have_cookies:
           #get the cookies
           ""
        else:
           # redirect to share page

           #store the cookies
        try:
            website_content = programmatic_login_utils.visit(url, cookies)
        except(urlfetch.Error):
            self.abort(404)
        
        self.response.write(template.render('templates/mirror.html', {'website_content', website_content}));

class LoginGuestHandler(LoginRequiredHandler):
    def doPost(self, **args):
        current_username = self.session.get("username")

        # TODO allow_multiple is deprecated...
        d = self.request.get("d[]", allow_multiple=True)
        p = self.request.get("p[]", allow_multiple=True)
        q = self.request.get("q[]", allow_multiple=True)
        
        shared_account_key = self.request.get("key")
        shared_account = db.get(shared_account_key)
        shared_url = shared_account.account.host_url
        if shared_url[:7] != "http://":
             shared_url = "http://" + shared_url
        shared_login_url = shared_url + "/login" #TODO: make this smarter

        shared_username = shared_account.account.host_username
        shared_password = decryptPasswordForGuest(current_username, d, p, q, shared_account)

        have_cookies = False # TODO: check in the database
        if not have_cookies:
           shared_url_cookies = programmatic_login_utils.login(shared_login_url, shared_username, shared_password)
           # TODO: get this working
           #print type(shared_url_cookies[0]).__name__
           #shared_url_cookies_str = json.dumps(shared_url_cookies)
           
           #proxy_session = ProxySession(sharedAccount = shared_account, cookies = shared_url_cookies_str)
           #proxy_session.put()         
        self.response.write(shared_url)
        
