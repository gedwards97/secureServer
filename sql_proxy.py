from random import randint

class sqlQuery:

    def __init__(self, query):
        self.query = query
        self.encrypted = False
        self.encryption_key = None
        self.single_keywords = ['add', 'alter', 'all', 'and', 'any', 'as', 'asc', 'between',
                            'case', 'check', 'column', 'constraint', 'create', 'database', 
                            'default', 'delete', 'desc', 'distinct', 'drop', 'exec', 
                            'exists', 'from', 'having', 'in', 'index', 'join', 
                            'like', 'limit', 'not', 'or', 'procedure', 'rownum', 'select', 'set',
                            'table', 'top', 'unique', 'union', 'update', 'values', 'view', 
                            'where']

        self.multiple_keywords = ['add constraint', 'alter column', 'alter table', 'backup database',
                                 'create database', 'create index', 'create table', 'create procedure', 
                                 'create unique index', 'create view'
                                 'drop column', 'drop constraint', 'drop database', 'drop default', 
                                 'drop index', 'drop table', 'drop view', 'foreign key', 'full outer join',
                                 'group by', 'inner join', 'insert into', 'insert into select', 'is null',
                                 'is not null', 'left join', 'not null', 'order by', 'outer join', 
                                 'primary key', 'right join', 'select distinct', 'select into', 'select top',
                                 'truncate table', 'union all']
        
    def encrypt(self):
        # Defining the extension as a random six digit number 
        keyword_extension = randint(100000, 999999)

        # Check for multiple keywords first, as these can be specific cases of select sing keywords (such as create)
        for keywords in self.multiple_keywords:
            # Keywords can either be lowercase or capitals (need to extend this to title case as well I think)
            if (keywords + " " in self.query or " " + keywords in self.query):
                encrypted_keywords = keywords.replace(" ", str(keyword_extension) + " ")
                self.query = self.query.replace(keywords, encrypted_keywords)
                self.encrypted = True

            elif (keywords.upper() + " " in self.query or " " + keywords.upper() in self.query):
                encrypted_keywords = keywords.upper().replace(" ", str(keyword_extension) + " ")
                self.query = self.query.replace(keywords.upper(), encrypted_keywords)
                self.encrypted = True

        # Check for single keywords second
        for keyword in self.single_keywords:
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

            

# Need to implement a system which is able to successfully identify keywords, regardless of whether they have blank spaces either side or not.
 
test = sqlQuery("select * from truncate TABLE")
test.encrypt()
print(test.query)