from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True) # H(salt + H(pw))
    salt = db.StringProperty(required=True)

    public_key = db.StringProperty(required=True) # encr(json.stringify({p, q, d}), MP)
    private_key = db.StringProperty(required=True) # encr(json.stringify({pq, e}), MP)

class StoredAccount(db.Model):
    username = db.StringProperty(required=True)
    host_url = db.StringProperty(required=True)
    host_username = db.StringProperty(required=True)
    encr_host_password = db.StringProperty(required=True)

class SharedAccount(db.Model):
    # TODO - prevent duplicates!
    granter = db.ReferenceProperty(User, collection_name="sharedaccount_granter_set", required=True) # Want to enforce granter = account.user
    grantee = db.ReferenceProperty(User, collection_name="sharedaccount_grantee_set", required=True)

    # TODO - technically it shouldn't be linked, there should be a db proxy, but easier to code for now
    account = db.ReferenceProperty(StoredAccount, collection_name="shares", required=True)
    encr_grantee_password = db.StringProperty(required=True)

class ProxySession(db.Model):
    sharedAccount = db.ReferenceProperty(SharedAccount, required=True)
    cookies = db.TextProperty(required=True)
    
class LogRecord(db.Model):
    shared_account = db.ReferenceProperty(SharedAccount, required=True)
    record = db.TextProperty(required=True)
    timestamp = db.DateTimeProperty(auto_now_add=True)
