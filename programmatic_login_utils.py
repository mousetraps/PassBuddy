# SITES THAT WORK:
# okcupid
# yahoo
# facebook.com if login is done on m.facebook.com
#   --using mobile user agent and visiting facebook.com redirects to the mobile site and then if the normal python browser visits that, it gets the right cookies and can navigate the normal site
# SITES THAT DON'T WORK:
# facebook: claims cookies are not enabled (perhaps because it wants to set them via javascript?)
# # yelp: ==facebook (but m.yelp.com redirects to www.yelp.com and mobile user agent trick does not help)
# gmail: ==facebook (but user agent trick does not help)
# foursquare: probably ==yelp (though no explicit cookie error, just doesn't work)
# reddit: too many requests error from urllib2 (in initial request of login page to scrape forms)

from HTMLParser import HTMLParser
from urllib import urlencode
import urllib2, json

class PasswordFieldFinderHTMLParser(HTMLParser):
    form_tags = []
    fti = -1
    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag
        if tag == 'input':
            attrs = dict(attrs)
            #print "Found input: " + str(attrs)
            self.form_tags[self.fti][1].append(attrs)
        if tag == 'form':
            attrs = dict(attrs)
            #print "###Found a form: " + str(attrs)
            self.form_tags.append((attrs, []))
            self.fti += 1
    def handle_endtag(self, tag):
        #print "Encountered an end tag :", tag
        if tag == 'form':
            #print "###Found a form end"
            self.fti -= 1
            if self.fti == -1:  # all nested forms have been matched and we are ready to start from scratch by moving to the end of the list
                self.fti = len(self.form_tags) - 1
    def handle_data(self, data):
        #print "Encountered some data  :", data
        pass

########

# Arguments: the url to a page on which you can log in, the username, the password
# Returns: a list of Cookies in the response. The calling function will probably want to pickle and save these so they can be read later by visit(url, cookies)
def login(url, username, password):
    mobile_request = urllib2.Request(url)
    mobile_request.add_header('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; Nexus One Build/FRG83) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')
    mobile_connection = urllib2.urlopen(mobile_request)
    url = mobile_connection.geturl()

    # instantiate the parser and fed it some HTML
    parser = PasswordFieldFinderHTMLParser()
    connection = urllib2.urlopen(url)
    html = connection.read()
    charset = 'utf-8'
    html = html.decode(charset)
    parser.feed(html)
    form_attrs_index = None
    form_attrs = None
    username_attrs = None
    password_attrs = None
    other_fields = set()
    for fi in range(len(parser.form_tags)):
        (attrs, input_tags) = parser.form_tags[fi]
        for tagi in range(len(input_tags)):
            pattrs = input_tags[tagi]
            if 'type' in pattrs and pattrs['type'] == 'password':
                form_attrs = attrs
                form_attrs_index = fi
                for tagj in range(len(input_tags)):
                    aattrs = input_tags[tagj]
                    if 'type' in aattrs and aattrs['type'] == 'password':
                        if password_attrs != None:
                            # Two password fields is a sign of a register form
                            # so reset to the starting point.
                            form_attrs = None
                            other_fields = set()
                            username_attrs = None
                            password_attrs = None
                            break
                        password_attrs = aattrs
                        if tagj > 0:
                            username_attrs = input_tags[tagj - 1]
                            other_fields.remove(tagj - 1)
                    else:
                        other_fields.add(tagj)
                break
        if form_attrs != None:
            break

    username_attrs['value'] = username
    password_attrs['value'] = password
    all_attrs = [username_attrs, password_attrs] + [parser.form_tags[fi][1][tagi] for tagi in other_fields]
    if 'action' in form_attrs and 'method' in form_attrs:
        form_url = form_attrs['action']
        if form_url[0] == '/':
            # Relative to site root
            root_end = connection.geturl().find('/', connection.geturl().find('//') + 2)
            form_url = connection.geturl()[:root_end] + form_url
        form_action = form_attrs['method']
        data = []
        for attrs in all_attrs:
            if 'name' in attrs and 'value' in attrs:
                data.append((attrs['name'], attrs['value'].encode(charset)))
            # else:
            #     sys.stderr.write("Warning: skipping tag in data because at least one of 'name' and 'value' were missing:\n" + str(attrs) + "\n")
        datastr = urlencode(data)
        if form_action.lower() == 'post':
            login_request = urllib2.Request(form_url, datastr)
        else:  # assume 'get'
            form_url_get = form_url + ('?' if form_url[-1] != '?' else '') + datastr
            login_request = urllib2.Request(form_url_get)
            login_request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4')
        cookie_processor = urllib2.HTTPCookieProcessor()
        od = urllib2.build_opener(urllib2.HTTPRedirectHandler(), cookie_processor)
        login_connection = od.open(login_request)        
        return [x for x in cookie_processor.cookiejar]
    else:
        # sys.stderr.write("Could not log in due to missing attributes in the form (require 'action' and 'method'):\n" + str(form_attrs) + "\n")
        return []

# Visits the given url, sending along the given cookies, and returns the HTML of the response. (could easily be altered to return the connection object, from which this can be read along with headers)
def visit(url, cookies):
    cookie_processor = urllib2.HTTPCookieProcessor()
    for cookie in cookies:
        cookie_processor.cookiejar.set_cookie(cookie)
    od = urllib2.build_opener(urllib2.HTTPRedirectHandler(), cookie_processor)
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4')
    connection = od.open(request)
    html = connection.read()
    return html



# Ton of code copying from login because I'm lazy
# Arguments: url to scrape
# Returns: json with selector info for the login form, username field, and password field (e.g. "username_selector")
def detect_login_form(url):
    # instantiate the parser and fed it some HTML
    parser = PasswordFieldFinderHTMLParser()
    connection = urllib2.urlopen(url)
    html = connection.read()
    charset = 'utf-8'
    html = html.decode(charset)
    parser.feed(html)
    form_attrs_index = None
    form_attrs = None
    username_attrs = None
    password_attrs = None
    other_fields = set()
    for fi in range(len(parser.form_tags)):
        (attrs, input_tags) = parser.form_tags[fi]
        for tagi in range(len(input_tags)):
            pattrs = input_tags[tagi]
            if 'type' in pattrs and pattrs['type'] == 'password':
                form_attrs = attrs
                form_attrs_index = fi
                for tagj in range(len(input_tags)):
                    aattrs = input_tags[tagj]
                    if 'type' in aattrs and aattrs['type'] == 'password':
                        if password_attrs != None:
                            # Two password fields is a sign of a register form
                            # so reset to the starting point.
                            form_attrs = None
                            other_fields = set()
                            username_attrs = None
                            password_attrs = None
                            break
                        password_attrs = aattrs
                        if tagj > 0:
                            username_attrs = input_tags[tagj - 1]
                            other_fields.remove(tagj - 1)
                    else:
                        other_fields.add(tagj)
                break
        if form_attrs != None:
            break
    res = {}
    if "id" in form_attrs:
        res["form_selector"] = {"type": "id", "value": form_attrs["id"]}
    elif "name" in form_attrs:
        res["form_selector"] = {"type": "name", "value": form_attrs["name"]}
    if "id" in username_attrs:
        res["username_selector"] = {"type": "id", "value": username_attrs["id"]}
    elif "name" in username_attrs:
        res["username_selector"] = {"type": "name", "value": username_attrs["name"]}
    if "id" in password_attrs:
        res["password_selector"] = {"type": "id", "value": password_attrs["id"]}
    elif "name" in password_attrs:
        res["password_selector"] = {"type": "name", "value": password_attrs["name"]}
    return json.dumps(res)
