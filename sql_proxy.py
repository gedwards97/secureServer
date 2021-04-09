from random import randint

class sqlProxy:

    def __init__(self, query):
        self.query = query
        self.encrypted = False
        self.encryption_key = None
        self.injection_threat = False
        self.keywords = ['add', 'alter', 'all', 'and', 'any', 'as', 'asc', 'between',
                            'case', 'check', 'column', 'constraint', 'create', 'database', 
                            'default', 'delete', 'desc', 'distinct', 'drop', 'exec', 
                            'exists', 'from', 'having', 'in', 'index', 'join', 
                            'like', 'limit', 'not', 'or', 'procedure', 'rownum', 'select', 'set',
                            'table', 'top', 'unique', 'union', 'update', 'values', 'view', 
                            'where']
        
    def encrypt(self):
        # Defining the extension as a random six digit number 
        keyword_extension = randint(100000, 999999)

        # Check for single keywords second
        for keyword in self.keywords:
            # Instances of lowercase keywords are appended with the randomly generated keyword_extension
            if (keyword + " " in self.query or " " + keyword  in self.query):
                self.query = self.query.replace(keyword, keyword + str(keyword_extension))
                self.encrypted = True

            # Instances of uppercase keywords are appended with the randomly generated keyword_extension
            elif (keyword.upper() + " " in self.query or " " + keyword.upper() in self.query):
                self.query = self.query.replace(keyword.upper(), keyword.upper() + str(keyword_extension))
                self.encrypted = True
        
        # self.encrypted is a boolean, which is only True if query has been encrypted.
        # If True, then the sqlQuery object is assigned an encryption key needed for decryption
        if self.encrypted:
            self.encryption_key = keyword_extension
    
    def user_input(self, user_inputs):
        for user_input in user_inputs:
            # Replace first instace of '' with corresponding user input
            self.query = self.query.replace(" ''", "'%s'"%(user_input), 1) 
    
    def injection_test(self):
        # Booleans which validate whether potentially malicious SQL injection has taken place  
        no_malicious_keywords = True 
        # Lists which will contain the encrypted versions of keywords
        encrypted_keywords = []
        # Single keywords with encryption extensions
        for keyword in self.keywords:
            encrypted_keywords.append(keyword + str(self.encryption_key))

        # Decryption is only carried out if the query has been encrypted
        if self.encrypted:
            decrypted_query = self.query.replace(str(self.encryption_key), "")
            for index in range(len(self.keywords)):
                # Sum of the keywords and their associated encryptions in the query (SIMPLIFY THIS WITH A FUNCTION MAYBE)
                keyword_count = (decrypted_query.count(self.keywords[index] + " ") + decrypted_query.count(" " + self.keywords[index]) - decrypted_query.count(" " + self.keywords[index] + " ")) + (decrypted_query.count(" " + self.keywords[index].upper()) + decrypted_query.count(self.keywords[index].upper() + " ") - decrypted_query.count(" " + self.keywords[index].upper() + " "))
                encrypted_keyword_count = (self.query.count(encrypted_keywords[index] + " ") + self.query.count(" " + encrypted_keywords[index]) - self.query.count(" " + encrypted_keywords[index] + " ")) + (self.query.count(encrypted_keywords[index].upper() + " ") + self.query.count(" " + encrypted_keywords[index].upper()) - self.query.count(" " + encrypted_keywords[index].upper() + " "))
                # Check whether each instance of a single keyword has the encryption key appended the end
                if keyword_count == encrypted_keyword_count:
                    pass
                else:
                    no_malicious_keywords = False
            
            # Remove keyword extension from 
            if no_malicious_keywords:
                pass
            # Possible SQL Injection attack identified
            else:
                self.injection_threat = True
    
    def decrypt(self):
        self.injection_test()

        if self.injection_threat:
            pass
        else:
            self.query = self.query.replace(str(self.encryption_key), "")
    



