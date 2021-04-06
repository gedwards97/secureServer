from random import randint

class sqlProxy:

    def __init__(self, query):
        self.query = query
        self.single_keywords = [' add ', ' alter ', ' all ', ' and ', ' any ', ' as ', ' asc ', ' between ',
                            ' case ', ' check ', ' column ', ' constraint ', ' create ', ' database ', 
                            ' default ', ' delete ', ' desc ', ' distinct ', ' drop ', ' exec ', 
                            ' exists ', ' from ', ' having ', ' in ', ' index ', ' join ', 
                            ' like ', ' limit ', ' not ', ' or ', ' procedure ', ' rownum ', ' select ', ' set ',
                            ' table ', ' top ', ' unique ', ' union ', ' update ', ' values ', ' view ', 
                            ' where ']

        self.multiple_keywords = [' add constraint ', ' alter column ', ' alter table ', ' backup database ',
                                 ' create database ', ' create index ', ' create table ', ' create procedure ', 
                                 ' create unique index ', ' create view '
                                 ' drop column ', ' drop constraint ', ' drop database ', ' drop default ', 
                                 ' drop index ', ' drop table ', ' drop view ', ' foreign key ', ' full outer join ',
                                 ' group by ', ' inner join ', ' insert into ', ' insert into select ', ' is null ',
                                 ' is not null ', ' left join ', ' not null ', ' order by ', ' outer join ', 
                                 ' primary key ', ' right join ', ' select distinct ', ' select into ', ' select top ',
                                 ' truncate table ', ' union all ']
        
    def encrypt(self):
        # Defining the extension as a random six digit number 
        keyword_extension = randint(100000, 999999)

        # Check for multiple keywords first, as these can be specific cases of select sing keywords (such as create)
        for keyword in self.multiple_keywords:
            # Keywords can either be lowercase or capitals (need to extend this to title case as well I think)
            if keyword in self.query or keyword.upper() in self.query:
                # For now just checking if keywords are correctly detected
                print("Multiple keyword ", keyword, " found! We need to add the extension number ", str(keyword_extension))

        # Check for single keywords second
        for keyword in self.single_keywords:
            if keyword in self.query or keyword.upper() in self.query:
                # For now just checking if keywords are correctly detected
                print("Single keyword ", keyword, " found! We need to add the extension number ", str(keyword_extension))


# Need to implement a system which is able to successfully identify keywords, regardless of whether they have blank spaces either side or not.
 
test = sqlProxy("SELECT * FROM table")
test.encrypt()
