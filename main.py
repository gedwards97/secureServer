import datetime
import sqlite3
import sys
from datetime import timedelta
from functools import wraps
from random import randint,choice
from sql_proxy import sqlProxy
from flask import Flask,g,render_template,redirect,request,session,url_for,make_response,flash
from session_encryption import token_encryption, token_decryption, encrypt_key

# Web application initiation
app = Flask(__name__)
# Creating application's secret key
# This is complex and random by design, in order to make it very difficult to guess -> if compromised, SecureCookieSession signatures are vulnerable
app.secret_key = ''.join(choice('0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ') for i in range(18))

# Database initiatiom
DATABASE = 'database.sqlite'

# Global variables used throughout the server
logged_in = False
logged_out = False
encrypt_user = None

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts

    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


# I think this function determines the structure of the context of client's request (dictionary format)
# => whether it's GET or POST (only reuqests used so far), it contains userid and username of client
def std_context(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        context={}
        request.context = context
        if 'userid' in session:
            context['loggedin'] = True
            # Server side decryption of current username which is stored in SecureCookieSession item encrypted  
            context['username'] = token_decryption(encrypt_user, encrypt_key) # WAS -> session['username'] before 
        else:
            context['loggedin'] = False

        return f(*args,**kwargs)
    return wrapper

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Web Applications homepage
@app.route("/")
@std_context
def index():
    # Query which returns all posts stored in the application's database
    # This query does not take user input => DOESNT need to be passed through sql_proxy
    posts = query_db('SELECT posts.creator,posts.date,posts.title,posts.content,users.name,users.username FROM posts JOIN users ON posts.creator=users.userid ORDER BY date DESC LIMIT 10')

    token = randint(10,1000000000000) # <====== NEED TO DETERMINE THE PURPOSE OF THIS

    # Format of past posts
    def fix(item):
        item['date'] = datetime.datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M')
        item['content'] = '%s...'%(item['content'][:200])
        return item

    context = request.context # Defines context variable in basic from from std_context function
    # Adds posts and form_token keys, and corresponding values to the context variable
    context['posts'] = map(fix, posts)
    context['form_token'] = token
    print(context)

    # **context passes the context dictionary as keyword arguments
    # ie => **context = (userid=0, username=aking, posts=... etc)
    return render_template('index.html', **context)

@app.route("/<uname>/")
@std_context
def users_posts(uname=None):
    # Query subjected to sql injection testing
    query = "SELECT userid FROM users WHERE username = ''"
    proxy_query = sqlProxy(query)
    proxy_query.encrypt()
    
    proxy_query.user_input([uname])
    
    proxy_query.decrypt()

    
    if proxy_query.injection_threat:
        # Database is not queried if an SQL injection threat is detected 
        return redirect(url_for('user_sqlinjection'))
    else:
        # Database successfully queried
        cid = query_db(proxy_query.query)

        if len(cid)<1:
            return 'No such user'

        cid = cid[0]['userid']
        query = 'SELECT date,title,content FROM posts WHERE creator=%s ORDER BY date DESC'%(cid)
        
        context = request.context

        def fix(item):
            item['date'] = datetime.datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M')
            return item

        context['posts'] = map(fix, query_db(query))
        return render_template('user_posts.html', **context)


# Login process - SUCCESSFULLY IMPLEMENTED SQL + SESSION MITIGATIONS
@app.route("/login/", methods=['GET', 'POST'])
@std_context
def login():
    # Selecting global varaibles used 
    global logged_out, encrypt_user

    username = request.form.get('username','')
    password = request.form.get('password','')
    context = request.context

    if len(username)<1 and len(password)<1:
        return render_template('login.html', **context)

    #  Username + password check query is defined, applied to the proxy and is encrypted
    query = "SELECT userid FROM users WHERE username = '' AND password = ''"
    proxy_query = sqlProxy(query)
    proxy_query.encrypt()
    # User inputs are is inserted into the encrypted query
    proxy_query.user_input([username, password])
    # Query decryption takes place, this is only successfull if no injection threat is detected
    # If threat detected, query remains encrypted
    proxy_query.decrypt()

    if proxy_query.injection_threat:
        return redirect(url_for('user_sqlinjection'))
        # Database is not queried if an SQL injection threat is detected  ########################## <- DO I STILL NEED THIS?!?!?!
        # return redirect(url_for('login_fail', error='SQL Injection threat detected')) 
    else:
        # Query the database to see if the username entered exists
        account = query_db(proxy_query.query)
        pass_match = len(account)>0

        # Login executed if an account with matching credentials is found
        if pass_match:
            session['userid'] = account[0]['userid']
            encrypt_user = token_encryption(username, encrypt_key)
            session['username'] = encrypt_user[0]
            logged_out = False
            
            return redirect(url_for('index'))
        # Failed login protocol executed if username and password do not match those of an existing account
        else:
            return redirect(url_for('login_fail', error='Failed Login - Incorrect Credentials'))

# Login fail route 
# This is reached with incorrect credentials 
@app.route("/loginfail/")
@std_context
def login_fail():
    context = request.context
    # Takes error value from redirect above, if this doesn't exist => error value = Unknown error
    context['error_msg'] = request.args.get('error','Unknown error')
    return render_template('login_fail.html',**context)

@app.route("/logout/")
def logout():
    # Session credentials are removed as the user has logged out
    global logged_out
    session.pop('userid', None)
    session.pop('username', None)
    logged_out = True
    return redirect('/')

# Access this route from clicking the 'post' link created in base html
@app.route("/post/", methods=['GET', 'POST'])
@std_context
def new_post():
    # Prevent client from post page if they do not have a valid active session 
    if 'userid' not in session:
        return redirect(url_for('login'))

    userid = session['userid']
    # Standard userid and username is retireved as context
    context = request.context
    print("HERE G ", request.method)

    # When post link is clicked, request.method == GET <- deafult of app route (THINK IT IS POST WHEN 'POST' BUTTON IS CLICKED)
    if request.method=='GET':
        return render_template('new_post.html', **context)

    # Defining variables on the server side - TITLE and CONTENT retireved from post form
    date = datetime.datetime.now().timestamp()
    title = request.form.get('title')
    content = request.form.get('content')


    #  userid and date inserted before encryption, as they are not subject to user input
    query = "INSERT INTO posts (creator, date, title, content) VALUES ( '%s',%d, '', '')"%(userid, date)
    proxy_query = sqlProxy(query)
    proxy_query.encrypt()

    # Client's title and content of post is inserted into the query 
    proxy_query.user_input([title, content])
    
    # Query decryption takes place, this is only successfull if no injection threat is detected
    # If threat detected, query remains encrypted
    proxy_query.decrypt()

    if proxy_query.injection_threat:
        return redirect(url_for('user_sqlinjection'))
    else:
        query_db(proxy_query.query)
        get_db().commit()
        return redirect('/')

@app.route("/reset/", methods=['GET', 'POST'])
@std_context
def reset():
    context = request.context

    email = request.form.get('email','')
    if email=='':
        return render_template('reset_request.html')

    query = "SELECT email FROM users WHERE email='%s'"%(email)
    exists = query_db(query)
    if len(exists)<1:
        return render_template('no_email.html', **context)
    else:
        context['email'] = email
        return render_template('sent_reset.html', **context)

@app.route("/search/")
@std_context
def search_page():
    context = request.context
    search = request.args.get('s', '')
    print("1" + search, file=sys.stderr)

    #query = "SELECT posts.creator,posts.title,posts.content,users.username FROM posts JOIN users ON posts.creator=users.userid WHERE users.username LIKE '%%%s%%' ORDER BY date DESC LIMIT 10;"%(search)
    query = "SELECT username FROM users WHERE username LIKE '%%%s%%';"%(search)
    users = query_db(query)
    #for user in users:
        #post['content'] = '%s...'%(post['content'][:50])
    context['users'] = users
    context['query'] = search
    print(context, file=sys.stderr)
    return render_template('search_results.html', **context)

@app.route("/resetdb/<token>")
def resetdb(token=None):
    if token=='secret42':
        import create_db
        create_db.delete_db()
        create_db.create()
        return 'Database reset'
    else:
        return 'Nope',401


# App route for SQL Injection threats detected within the application
@app.route("/SQLejected")
def user_sqlinjection():
    # Users session is ended 
    global logged_out
    session.pop('userid', None)
    session.pop('username', None)
    logged_out = True
    # 403 Forbidden returned
    return 'Back off', 403



@app.before_request
def session_timeout():
    global logged_in, logged_out
    session.modified = True
    app.permanent_session_lifetime = timedelta(seconds=5)
    if session.get('userid', None) is None and logged_in is True:
        if logged_out is True:
            logged_in = False
            print("LOGGED OUT")
        else:
            logged_in = False
            print("SESSION TIMEOUT")
            flash("! ! ! !  Your session timed out ! ! ! !")

    elif session.get('userid', None) is not None and logged_in is True:
        logged_in = True
        print("STILL LOGGED IN")

    elif session.get('userid', None) is None and logged_in is False:
        logged_in = False
        print("HAVEN'T LOGGED IN")
    
    else:
        logged_in = True
        print("LOGGED IN")        

if __name__ == '__main__':
    app.run(debug=True)