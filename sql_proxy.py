from random import randint

class sqlQuery:

    def __init__(self, query):
        self.query = query
        self.encrypted = False
        self.encryption_key = None
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
    
    def decrypt(self):
        # Booleans which validate whether potentially malicious SQL injection has taken place  
        no_malicious_keywords = True 
        # Lists which will contain the encrypted versions of keywords
        encrypted_keywords = []
        # Single keywords with encryption extensions
        for keyword in self.keywords:
            encrypted_keywords.append(keyword + str(self.encryption_key))

        # Decryption is only carried out if the query has been encrypted
        if self.encrypted:
            for index in range(len(self.keywords)):
                # Sum of the keywords and their associated encryptions in the query 
                keyword_count = self.query.count(self.keywords[index] + " ") + self.query.count(" " + self.keywords[index]) - self.query.count(" " + self.keywords[index] + " ")
                encrypted_keyword_count = self.query.count(encrypted_keywords[index] + " ") + self.query.count(" " + encrypted_keywords[index]) - self.query.count(" " + encrypted_keywords[index] + " ")
                # Check whether each instance of a single keyword has the encryption key appended the end
                if keyword_count == encrypted_keyword_count:
                    pass
                else:
                    no_malicious_keywords = False
            
            # Remove keyword extension from 
            if no_malicious_keywords:
                self.query = self.query.replace(str(self.encryption_key), "")
                print(self.query)
            # Possible SQL Injection attack identified
            else:
                print("!!! Possible SQL Injection identified !!!".upper())
    
    def user_input(self, user_inputs):
        for user_input in user_inputs:
            self.query = self.query.replace("''", "'%s'"%(user_input)) 

# Testing the code works successfully below
query = "SELECT profile FROM userTable WHERE username = ''"
test = sqlQuery(query)
print(test.query)
test.encrypt()
print("Encrypted query \n", test.query)
username = input("Enter username: ", )
test.user_input([username])
print(test.query)
print("Decrypted query:")
test.decrypt()
