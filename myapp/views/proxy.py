import json, re, urllib, urlparse, datetime

from myapp.models import *
from core import *
from toolbox.decode import *
from toolbox import programmatic_login_utils
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template



def fix_url(href, current_url, root_url, shared_account_key):
    if href == "":
        url = current_url
    elif href[0] == '#':  # page anchor
        url = current_url + href
    elif href[0] == '/':  # root-relative url
        url = root_url + href
    elif href.find('://') != -1:  # fully qualified url
        url = href
    else:  # relative url
        url = current_url + ('/' if current_url[-1] != '/' else '') + href  # don't worry about use of '..', for simplicity
    return '/mirror?key=' + shared_account_key + '&url=' + urllib.quote_plus(url)

def proxify_html(html, url, key):
    current_url = url
    if current_url.find('://') == -1:
        current_url = 'http://' + current_url
    root_end = current_url.find('/', current_url.find('//') + 2)
    root_url = current_url[0:root_end] if root_end != -1 else current_url
    def fix_url_wrapper(match):
        return match.group(1) + '="' + fix_url(match.group(2), current_url, root_url, key) + '"'
    regexPattern = r'(<a[^>]*href|<form[^>]*action)="([^"]*)'
    regexReplacement = fix_url_wrapper
    html = re.sub(regexPattern, regexReplacement, html)
    return html

def decryptPasswordForGuest(guest_username, d, p, q, shared_account):
    p = [int(numeric_string) for numeric_string in p]
    q = [int(numeric_string) for numeric_string in q]
    d = [int(numeric_string) for numeric_string in d]


    shared_password = None
    if shared_account.grantee.username == guest_username:
	encrypted_shared_password = shared_account.encr_grantee_password
	shared_password = rsaDecode([d, p, q], encrypted_shared_password)
    return shared_password

def deleteOldLogRecords(shared_account):
    LAST_WEEK = datetime.datetime.now() - datetime.timedelta(days=7)
    q = db.GqlQuery("SELECT * FROM LogRecord where shared_account = :1 and timestamp < :2", shared_account, LAST_WEEK)
    old_records = q.fetch(limit=None)
    for old_record in old_records:
        db.delete(old_record)


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

        shared_account_key = self.request.get("key")
        shared_account = db.get(shared_account_key)
        url_to_access = self.request.get("url")

        q = db.GqlQuery("SELECT * FROM ProxySession where sharedAccount = :1", shared_account)
        proxy_session = q.get()
        if proxy_session:

            # Log the request. For now just log the url accessed; in
            # the future if we handled form submissions etc., could
            # also log post data if we encrypted it with the granter's
            # public key..
            log_record = LogRecord(shared_account=shared_account, record=url_to_access)
            log_record.put()
            deleteOldLogRecords(shared_account)
            ##

            cookies = programmatic_login_utils.cookies_from_json(proxy_session.cookies)
            try:
                website_content = programmatic_login_utils.visit(url_to_access, cookies)
                website_content = unicode(website_content, errors='ignore')
                website_content = proxify_html(website_content, str(url_to_access), str(shared_account_key))
            except(urlfetch.Error):
                self.abort(404)
        else:
            pass
            # redirect to share page
        self.response.write(template.render('templates/mirror.html', {'website_content': website_content, 'username':self.session.get("username")}));


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
        
        q = db.GqlQuery("SELECT * FROM ProxySession where sharedAccount = :1", shared_account)
        proxy_session = q.get()
        # Log the login attempt, even if we already have cookies.
        log_record = LogRecord(shared_account=shared_account, record="LOGIN")
        log_record.put()
        deleteOldLogRecords(shared_account)
        ##
        if not proxy_session:
           shared_url_cookies = programmatic_login_utils.login(shared_login_url, shared_username, shared_password)
           shared_url_cookies_json = programmatic_login_utils.json_from_cookies(shared_url_cookies)
           
           proxy_session = ProxySession(sharedAccount = shared_account, cookies = shared_url_cookies_json)
           proxy_session.put()         
        self.response.write(shared_url)

class DetectLoginFormHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get("url")
        self.response.out.write(programmatic_login_utils.detect_login_form(url))

class LogsHandler(LoginRequiredHandler):
    def get(self):
        shared_account_key = self.request.get("key")
        shared_account = db.get(shared_account_key)
        q = db.GqlQuery("SELECT * from LogRecord where shared_account=:1 ORDER BY timestamp DESC", shared_account)
        log_records = q.fetch(limit=None)
        
        template_dict = {
            'grantee': shared_account.grantee.username,
            'host_url': shared_account.account.host_url,
            'host_username': shared_account.account.host_username,
            'log_records': log_records
        }

        self.response.write(template.render("templates/modal_logs.html", template_dict ))
