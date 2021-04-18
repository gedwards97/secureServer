import random

# Random alphanumeric string. Encryption and decryption can only be carried out if this key is passed through the funtion 
encrypt_key = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ') for i in range(16))


def token_encryption(token, key):

    # Dictionary which the encryption is based upon
    encrypt_dict = {
        'a': 2, 'b': 4, 'c': 6, 'd': 8, 'e': 10, 'f': 12, 'g': 14, 'h': 16,
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
        '!' : 49, '0' : 310, '1' : 309, '2' : 308, '3' : 307, '4' : 306,
        '5' : 305, '6' : 304, '7' : 303, '8' : 302, '9' : 301
    }

    # Encrypted list breaks up encrypted elements, to allow for decryption
    encryted_list = []
    # Final encrypted token which can is then stored in the SecureCookieSession object
    encryted_token= ""

    if key == encrypt_key:
        for char in token:
            # Append a characters encrypted value onto the encrypted list
            encryted_list.append(encrypt_dict[char])
        
        for element in encryted_list:
            # Concatenate the encrypted token
            encryted_token += str(element)
    
    return encryted_token, encryted_list


def token_decryption(token, key):    

    # Redefine dictionary which the encryption is based upon
    encrypt_dict = {
        'a': 2, 'b': 4, 'c': 6, 'd': 8, 'e': 10, 'f': 12, 'g': 14, 'h': 16,
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
        '!' : 49, '0' : 310, '1' : 309, '2' : 308, '3' : 307, '4' : 306,
        '5' : 305, '6' : 304, '7' : 303, '8' : 302, '9' : 301
    }

    # Decryption is only attempted if the correct encryption key is passed, and the token's value is not None
    # Token values (such as username) default as None on the server, when they are initiated as global variables
    if key == encrypt_key and token != None:
        # Defining encrypted list from the token tuple (returned from the encryption function)
        encrypted_list = token[1]
        decrypted_token = ""
        # Matching encrypted value with it's corresponding key
        for encrypted_item in encrypted_list:
            for key in encrypt_dict:
                if encrypted_item == encrypt_dict[key]:
                    # Concatenating the decrypted token with the suitable key
                    decrypted_token += key
                else: 
                    pass
    else:
        decrypted_token = None
    
    return decrypted_token



# token2 = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ') for i in range(random.randint(20, 25)))
# # token2 = "George123"
# print(token2)


# key = 123
# token2_encrypt = token_encryption(token2, key)
# print(token2_encrypt[0])

# token2_decrypt = token_decryption(token2_encrypt, key)
# print(token2_decrypt)

# # Implement this onto server 
# # Session timeout as well onto server
