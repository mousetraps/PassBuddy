#!/usr/bin/env python

from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty()
    salt = db.StringProperty()
    pw_hsh = db.StringProperty() # H(salt + H(pw))
    token = db.StringProperty()

class StoredAccount(db.Model):
    user = db.ReferenceProperty(User)
    host_url = db.StringProperty()
    host_username = db.StringProperty()
    host_password = db.StringProperty() # Encrypted with at least the user's master password

class SharedAccount(db.Model):
    grantee = db.ReferenceProperty(User, collection_name="sharedaccount_reference_grantee_set")
    granter = db.ReferenceProperty(User, collection_name="sharedaccount_reference_granter_set") # Want to enforce granter = account.user
    account = db.ReferenceProperty(StoredAccount)
