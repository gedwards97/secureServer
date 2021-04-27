cipher_dict = {'a': 2, 'b': 4, 'c': 6, 'd': 8, 'e': 10, 'f': 12, 'g': 14, 'h': 16,
        'i': 18, 'j': 20, 'k': 22, 'l': 24, 'm': 26, 'n': 1, 'o': 3, 'p': 5,
        'q': 7, 'r': 9, 's': 11, 't': 13, 'u': 15, 'v': 17, 'w': 19, 'x': 21,
        'y': 23, 'z': 25, ' ': 100, 'A': 101, 'B': 103, 'C': 105, 'D': 107, 
        'E': 109, 'F': 111, 'G': 113, 'H': 115, 'I': 117, 'J': 119, 'K': 121, 
        'L': 123, 'M': 125, 'N': 102, 'O': 104, 'P': 106, 'Q': 108, 'R': 110, 
        'S': 112, 'T': 114, 'U': 116, 'V': 118, 'W': 120, 'X': 122, 'Y': 124, 
        'Z': 126, '.': 30, '/' : 41, '\\' : 52, '$' : 63, '#' : 74, 
        '@' : 85, '%' : 96, '^' : 37, '*' : 48, '(' : 59, ')' : 60,
        '_' : 71, '-' : 82, '=' : 93, '+' : 34, '>' : 45, '<' : 56, 
        '?' : 67, ';' : 78, ':' : 89, '\'' : 90, '\"' : 31, '{' : 42,
        '}' : 53, '[' : 64, ']' : 75, '|' : 86, '`' : 97, '~' : 38, 
        '!' : 49, ',' : 50, '0' : 310, '1' : 309, '2' : 308, '3' : 307, '4' : 306,
        '5' : 305, '6' : 304, '7' : 303, '8' : 302, '9' : 301}


class NewCipher():

    def __init_(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.key = app.secret_key
        if not self.key:
            raise RuntimeError("Application's secret key is needed!")
        

    def encrypt(self, session_payload):
        payload_string = session_payload.decode('utf-8')
        encrypted_list = []
        encrypted_payload = ""


        for char in payload_string:
            encrypted_list.append(cipher_dict[char])


        for element in encrypted_list:
            encrypted_payload += str(element)
        
        encrypted_payload = encrypted_payload.encode('utf-8')

        
        return encrypted_payload, encrypted_list

    def decrypt(self, encrypted_list):

        decrypted_payload = ""

        for encrypted_item in encrypted_list:
            for key in cipher_dict:
                if encrypted_item == cipher_dict[key]:
                    decrypted_payload += key
                    break
        
        decrypted_payload = decrypted_payload.encode('utf-8')

        print("decrypted payload ", decrypted_payload)
        
        return decrypted_payload


