from flask import request
from flask.sessions import SessionInterface, SessionMixin
from datetime import timedelta, datetime
import json
from own_encryption import NewCipher
from random import choice

class EncryptedSession(dict, SessionMixin):
    pass

class EncryptedSessionInterface(SessionInterface):
    '''
    Overrides the default
    Flask session implementation, replacing base64 encryption of the 
    client-side session cookie.
    '''
    session_class = EncryptedSession
    
    def __init__(self):
        self.cipherlist = [] 
        self.signaturelist = []

    def open_session(self, app, request):
        # Secret key and signature check !
        cipher = NewCipher()
        signature = cipher.decrypt(self.signaturelist)
        signature = signature.decode('utf-8')
        if len(self.signaturelist) == 0:
            pass
        elif not app.secret_key or signature != 'our!signature':
            return None 

        # Get the session cookie
        session_cookie = request.cookies.get(app.session_cookie_name)
        if not session_cookie:
            return self.session_class()

        try:
            # Retrieve cookie payload
            payload = cipher.decrypt(self.cipherlist)
            payload = payload.decode('utf-8')
            
            # Convert back to a dict and pass that onto the session
            session_dict = json.loads (payload)
            return self.session_class (session_dict)

        except ValueError:
            return self.session_class()

    def save_session(self, app, session, response):

        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)

        # Salt and signature which will be appended to the final cookie structure
        # Salt is solefully for entropy increase / Siganture is checked in open_session
        salt = ''.join(choice('0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ') for i in range(8))
        salt = salt.encode('utf-8')
        signature = 'our!signature'
        signature = signature.encode('utf-8')

        # If the session is modified to be empty, remove the cookie.
        # If the session is empty, return without setting the cookie.
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain, path=path)
            return
        
        # Bytes version of session cookie dictionary
        bdict = bytes (json.dumps(dict(session), sort_keys=True, default=str), 'utf-8')
        prefix = "ck"

        # Cookie contents encryption
        cipher = NewCipher()
        ciphertext, self.cipherlist = cipher.encrypt(bdict)
        ciphersalt = cipher.encrypt(salt)[0]
        ciphersig, self.signaturelist = cipher.encrypt(signature)


        # Create the session cookie as prefix.payload.salt.signature
        tup = [prefix, ciphertext.decode(), ciphersalt.decode(), ciphersig.decode()] #ciphersalt.decode()
        session_cookie = ".".join(tup)

        # Set the session cookie
        response.set_cookie(app.session_cookie_name, session_cookie, httponly=True,
                             domain=domain, path=path)
        


