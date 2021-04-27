from flask import make_response, render_template, request, session, g
from random import choice
from session_encryption import token_encryption, token_decryption, encrypt_key
from own_encryption import NewCipher
import json

########################################

def generate_dsc(app):
    secret_key = app.secret_key
    token_key = "csrf_token"

    if token_key not in g:
        cipher = NewCipher()
        token_value = ''.join(choice("0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ") for i in range(10))
        salt = 'csrf-token'
        ciphertoken = cipher.encrypt(".".join([token_value.encode('utf-8'), salt.encode('utf-8')]))

        setattr(g, token_key, ciphertoken)
    
    return g.get(token_key)


# def _get_config()

#####################################




dsc_list = None

class DSC():

    def __init__(self, app=None):
        self.dsc_list = None
        self.cipher_key = None
        self.cipher = NewCipher()

        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.cipher_key = app.config.get("SECRET_KEY")
        if not self.cipher_key:
            raise RuntimeError("dsc-cookie requires the usage of SECRET_KEY")

    def dsc_cookie_init(self, app, template, context):
        if app.secret_key != self.cipher_key:
            print("CSRF HAS BEEN HACKED GEORGE")
            raise RuntimeError("keys do not match!")
        
        prefix = "ck"
        dsc_value = ''.join(choice("0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ") for i in range(20))
        # Appending raw csrf value to html context dict
        dsc_value = dsc_value.encode('utf-8')
        salt = ''.join(choice('0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ') for i in range(8))
        salt = salt.encode('utf-8')

        # Cookie encryption - dsc_encrypted_list updated for decryption purposes 
        cipherdsc, self.dsc_list = self.cipher.encrypt(dsc_value)
        print("DSC LIST ", dsc_list)
        ciphersalt = self.cipher.encrypt(salt)[0]

        dsc_cookie = ".".join([prefix, cipherdsc.decode(), ciphersalt.decode()])
        
        # Creating response and setting the encrypted csrf cookie 
        resp = make_response(render_template(template, **context))
        resp.set_cookie('dsc', dsc_cookie, httponly=True)

        return resp


    def dsc_decrypt(self, app):
        if app.secret_key != self.cipher_key:
            print("CSRF HAS BEEN HACKED GEORGE")
            raise RuntimeError("keys do not match!")
        
        if self.dsc_list is None:
            dsc_val = None
        else:
            dsc_val = self.cipher.decrypt(self.dsc_list)
            print("DSC FUNC VAL ", dsc_val)

        return dsc_val


class DSC2():

    def __init__(self):
        self.dsc_list = None

    def open(self, app, request):

        if not app.secret_key:
            print("CSRF BEEN HACKED")