# shop-js encrypted message decoder in Python
# Copyright John Hanna (c) 2002 under the terms of the GPL
# see http://shop-js.sf.net for details and latest version
# modified 7/12/2002

# Of course to run this you'll need python from python.org or elsewhere

# this is expecting private key parts as generated by the shop-js RSA key generator
# you'll obviously want to replace these values with YOUR OWN private key values
# privateKey=[ [d],[p],[q] ]

def rc4(key, string):
    """Return string rc4 (de/en)crypted with RC4."""
    s,i,j,klen=range(256),0,0,len(key)
    for i in range(256):
        j=(ord(key[i%klen])+s[i]+j)%256
        s[i],s[j]=s[j],s[i]
    for i in range(256):
        j=(ord(key[i%klen])+s[i]+j)%256
        s[i],s[j]=s[j],s[i]
    r=''
    for i in range(len(string)):
        i2=i % 256
        j=(s[i2]+j)%256
        s[i2],s[j]=s[j],s[i2]
        r+=chr(ord(string[i])^s[(s[i2]+s[j])%256])
    return r

def inverse(x, n):
    """Return the mod n inverse of x."""
    y, a, b = n, 1, 0
    while y>0:
        x, (q, y) = y, divmod(x, y)
        a, b = b, a - b*q
    if a < 0:
        a = a + n
    assert x==1, "No inverse, GCD is %d" % x
    return a


def crt_RSA(m, d, p, q):
    """ Compute m**d mod p*q for RSA private key operations."""
    xp = pow(m % p, d%(p-1), p)
    xq = pow(m % q, d%(q-1), q)
    t = ((xq - xp) * inverse(p, q)) % q
    if t < 0:
        t = t + q
    return t * p + xp


b64s='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"'
def base64ToText(text):
    r,m,a,c='',0,0,0
    for i in text[:]:
        c=b64s.find(i)
        if(c >= 0) :
            if(m):
                r += chr((c << (8-m))& 255 | a)
            a = c >> m
            m+=2
            if(m==8):m=0
    return r

def t2b(s):
    r=0L
    m=1L
    for i in s[:]:
        r+=m*ord(i)
        m*=256L
    return r

def b2t(b):
    r=''
    while(b):
        r+=chr(b % 256)
        b>>=8
    return r

def fix(a):
    r=0L
    s=0
    for i in a[:]:
        r|=long(i) << s
        s+=28
    return r

def rsaDecode(key,text):
    """ decode the text based on the given rsa key. """
    # separate the session key from the text
    text=base64ToText(text)
    sessionKeyLength=ord(text[0])
    sessionKeyEncryptedText=text[1:sessionKeyLength+1]
    text=text[sessionKeyLength+1:]
    sessionKeyEncrypted=t2b(sessionKeyEncryptedText)

    # un-rsa the session key
    sessionkey=crt_RSA(sessionKeyEncrypted,fix(key[0]),fix(key[1]),fix(key[2]))
    sessionkey=b2t(sessionkey)

    text=rc4(sessionkey,text)
    return text


privateKey=[
 [211146173,236796389,99054011,39430498,107502635,22100528,173332685,126067633,23490737,43112374,215603654,97763768,129307240,193500832,225995383,196217318,247811242,95758361,147],
 [79930095,201216333,170018212,115859736,10404795,32150654,210660423,132599055,204635034,14],
 [47716471,908384,204231222,108648834,118784602,25920125,261301885,215145545,83985924,11]]

# if you want a test phrase, decode this:
# aXCFtURf_XY1L2SUxHGfR"E5FAeq9E"OeFmfl7WlNO5It131"noEcl81_UxP
# BMN6siYz7M_B"vE4boCaLGzajxQhLrgyw37TGofQC2v5QYnLJfxpqWDlPgSy
# J6QCBZtKde5_jbIwgC5ipn42WgU6

rsaDecode(privateKey, 'aXCFtURf_XY1L2SUxHGfR"E5FAeq9E"OeFmfl7WlNO5It131"noEcl81_UxPBMN6siYz7M_B"vE4boCaLGzajxQhLrgyw37TGofQC2v5QYnLJfxpqWDlPgSyJ6QCBZtKde5_jbIwgC5ipn42WgU6')