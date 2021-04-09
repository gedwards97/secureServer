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

    encryted_list = []
    encryted_token= ""

    if key == 123:
        for char in token:
            encryted_list.append(encrypt_dict[char])
        
        for element in encryted_list:
            encryted_token += str(element)
    
    print(encryted_token)

token = "hash"
key = 123
token_encryption(token, key)