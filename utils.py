#!/usr/bin/env python

import random, string, datetime
from models import User

TOKEN_LENGTH = 20
COOKIE_LIFETIME_IN_DAYS = 7

def checkCookie(proposed_cookie):
    # Figure out the username for this cookie
    if proposed_cookie == None:
        return None
    if proposed_cookie.find("#") < 0:
        return None
    username = proposed_cookie[0:proposed_cookie.find("#")]
    # Find the user and therefore the correct token
    user = User.all().filter("username =", username).get()
    # If the user is not found, cookie can't be correct
    if user == None:
        return None
    # Check that the cookie stored matches the one given to this function
    if user.token == proposed_cookie:
        return user.username
    return None

def generateCookie(username):
    return username + "#" + ''.join(random.choice(string.ascii_letters + string.digits) for x in range(TOKEN_LENGTH))

def cookieExpiration():
    #return datetime.timedelta(days=COOKIE_LIFETIME_IN_DAYS)
    return 60*60*24*7
