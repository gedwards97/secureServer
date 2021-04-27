import datetime
import sqlite3
import sys
from datetime import timedelta
from functools import wraps
from random import randint,choice
from sql_proxy import sqlProxy
from flask import Flask,g,render_template,redirect,request,session,url_for,make_response,flash
# Own functions developed
from dsc_cookie import DSC
from encrypted_session import EncryptedSessionInterface


# Web application initiation
app = Flask(__name__)
# Creating application's secret key
# This is complex and random by design, in order to make it very difficult to guess -> if compromised, SecureCookieSession signatures are vulnerable
app.secret_key = ''.join(choice('0123456789abcdefghijklmnopqrstuvwxysABCDEFGHIJKMNLOPQRSTUVWXYZ') for i in range(10))
app.session_interface = EncryptedSessionInterface()

# Database initiatiom
DATABASE = 'database.sqlite'

# Global variables used throughout the server
logged_in = False
encrypt_user = None
csrf_cookie_exits = False
timedout = False
dsc = DSC()
dsc.init_app(app)

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
        global dsc
        context={}
        request.context = context
        if 'userid' in session:
            context['loggedin'] = True
            # Server side decryption of current username which is stored in SecureCookieSession item encrypted  
            context['username'] = session['username']
            if dsc.dsc_decrypt(app) is not None:
                context['dscvalue'] = dsc.dsc_decrypt(app).decode('utf-8')
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

    ################################################# DSC CSRF TRIAL
    global logged_in, csrf_cookie_exits, dsc
    print("logged in ", logged_in)
    if logged_in and not csrf_cookie_exits:
        print("DSC COOKIE INIT...")
        resp = dsc.dsc_cookie_init(app, 'index.html', context)
        csrf_cookie_exits = True
        return resp

    #################################################

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
        return redirect(url_for('forbidden', threat='SQL Injection threat detected'))
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
    global encrypt_user

    username = request.form.get('username','')
    password = request.form.get('password','')
    context = request.context

    if (len(username)<1 and len(password)<1):
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
        return redirect(url_for('forbidden', threat='SQL Injection threat detected'))
        # Database is not queried if an SQL injection threat is detected  ########################## <- DO I STILL NEED THIS?!?!?!
        # return redirect(url_for('login_fail', error='SQL Injection threat detected')) 
    else:
        # Query the database to see if the username entered exists
        account = query_db(proxy_query.query)
        pass_match = len(account)>0

        # Login executed if an account with matching credentials is found
        if pass_match:
            session['userid'] = account[0]['userid']
            session['username'] = username
            session['exp-time'] = datetime.datetime.now() + datetime.timedelta(minutes=5)
            
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
    global logged_in, csrf_cookie_exits
    res = make_response(redirect(url_for("login")))
    res.delete_cookie('dsc')
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('exp-time', None)
    csrf_cookie_exits = False
    logged_in = False
    return res

# Access this route from clicking the 'post' link created in base html
@app.route("/post/", methods=['GET', 'POST'])
@std_context
def new_post():
    # Prevent client from post page if they do not have a valid active session 
    if 'userid' not in session:
        return redirect(url_for('logout'))
    
    userid = session['userid']
    # Standard userid and username is retireved as context
    context = request.context
    if request.method == 'GET':
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

    ###################################### CSRF TRIALS
    form_csrf_value = request.form.get('dscval')
    users_csrf_value = context["dscvalue"]

    csrf_threat = form_csrf_value != users_csrf_value

    if proxy_query.injection_threat:
        return redirect(url_for('forbidden', threat='SQL Injection threat detected'))
    elif csrf_threat:
        return redirect(url_for('forbidden', threat='CSRF threat detected'))
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
@app.route("/forbidden")
@std_context
def forbidden():
    # Users session is ended 
    session.pop('userid', None)
    session.pop('username', None)
    

    context = request.context
    context['threat'] = request.args.get('threat', 'Unknown threat')
    # 403 Forbidden returned
    return render_template('403.html', **context)


from dateutil import parser

@app.before_request
def session_timeout_check():
    global logged_in, csrf_cookie_exits
    if 'exp-time' in session:
        present = datetime.datetime.now()
        exp_time_str = session['exp-time']
        # Converts exp-time from string to datetime object 
        cookie_exp_time = parser.parse(exp_time_str)
        # Session timeout protocol
        if present > cookie_exp_time:
            resp = make_response(redirect(url_for('login')))
            resp.delete_cookie('dsc')
            print("TIMED OUT")
            session.pop('userid', None)
            session.pop('username', None)
            session.pop('exp-time', None)
            flash("! ! ! !  Your session timed out ! ! ! !")
            csrf_cookie_exits = False
            logged_in = False
            return resp
        else:
            logged_in = True
            session['exp-time'] = present + datetime.timedelta(minutes=5)
        

if __name__ == '__main__':
    app.run(debug=True)












