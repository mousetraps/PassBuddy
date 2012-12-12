from myapp.models import *
import logging
from google.appengine.ext.webapp import template
from core import *

class ManagedTableHandler(LoginRequiredHandler):
    def doGet(self, **args):
        username = self.session.get('username')

        q = db.GqlQuery("SELECT * from StoredAccount where username=:1", username)
        stored_accounts = q.fetch(limit=None)

        template_dict = {
            'username': username,
            'stored_accounts': stored_accounts
        }

        self.response.write(template.render("templates/stored_acounts_table.html", template_dict ))

class ManageHandler(LoginRequiredHandler):
    def doGet(self, **args):

        action = self.request.get("action")

        if (action == "getPassword"):

            username = self.session.get('username')
            key_name = self.request.get('key_name')

            stored_account = db.get(key_name)

            if (stored_account.username == username):
                self.response.write(stored_account.encr_host_password)
            else:
                # error
                pass

        elif (action == "getPublicKey"):
            username = self.request.get('username')

            q = db.GqlQuery("SELECT * from User where username=:1", username)
            stored_account = q.get()

            self.response.write(stored_account.public_key)

        elif (action == "getPrivateKey"):
            username = self.session.get('username')

            q = db.GqlQuery("SELECT * from User where username=:1", username)
            stored_account = q.get()

            self.response.write(stored_account.private_key)

        elif (action == "json"):
            username = self.session.get('username')
            
            q = db.GqlQuery("SELECT * from StoredAccount where username=:1", username)
            stored_accounts = q.fetch(limit=None)
            
            accounts = [{"host_url": a.host_url, "host_username": a.host_username, "encr_host_password": a.encr_host_password} for a in stored_accounts]
            
            self.response.write(json.dumps(accounts))

        else:

            username = self.session.get('username')

            q = db.GqlQuery("SELECT * from StoredAccount where username=:1", username)
            stored_accounts = q.fetch(limit=None)

            template_dict = {
                'username': username,
                'stored_accounts': stored_accounts
            }

            self.response.write(template.render("templates/manage.html", template_dict ))


    def doPost(self):
        action = self.request.get("action")

        if (action == "add"):
            site = self.request.get("site")
            username = self.request.get("username")
            encrypted_password = self.request.get("encrypted_password")
            owner = self.session.get('username')

            new_account = StoredAccount(username=owner, host_url=site, host_username=username, encr_host_password=encrypted_password)
            new_account.put()

            logging.debug("added credentials: %s %s %s %s" % (owner, site, username, encrypted_password))


        elif (action == "remove"):

            username = self.session.get('username')
            key_name = self.request.get('key_name')


            stored_account = db.get(key_name)

            # stored_account = db.get(27)
            if (stored_account.username == username):
                db.delete(stored_account)
            else:
                # TODO - error
                pass

        elif (action == "shareAccount"):

            username = self.session.get('username')

            grantee = self.request.get('grantee')
            encr_password = self.request.get('encrPassword')
            key = self.request.get('accountKey')

            stored_account = db.get(key)

            q = db.GqlQuery("SELECT * from User where username=:1", grantee)
            grantee_entity = q.get()

            q = db.GqlQuery("SELECT * from User where username=:1", username)
            granter_entity = q.get()

            if (stored_account.username == username):
                shared_account = SharedAccount(granter=granter_entity, grantee=grantee_entity, account=stored_account, encr_grantee_password=encr_password)

                shared_account.put()

            else:
                # TODO - error
                pass

        elif action == "unshareAccount":
            username = self.session.get('username')
            key_name = self.request.get('key')


            stored_account = db.get(key_name)

            if stored_account.granter.username == username or stored_account.grantee.username == username:
                db.delete(stored_account)
            else:
                # TODO - error
                pass
