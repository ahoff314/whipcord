from flask import Flask, render_template
import sqlite3
import os 
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
    
from models import * 



app = Flask(__name__)

# login_manager = LoginManager()


#remove debugger in prod please
app.debug = True

### ROUTES

# index page
@app.route("/")
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('entries.html', entries=entries)

# create new post
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New post has been successfully shared.')
    return redirect(url_for('show_entries'))

# Logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You are now logged in. Welcome to Castalia')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
    
# signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        insertUser(username, password)
        flash('You have successfully signed up. Welcome to Castalia')
        return redirect(url_for('show_entries'))
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been successfully logged out')
    return redirect(url_for('show_entries'))


### END ROUTES

# Load default config 

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'floffr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
))

#config file step 2 // set floffr_settings to file path for config file
app.config.from_envvar('FLOFFR_SETTINGS', silent=True)

# DB STUFF
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'



### SERVER  
host = os.environ.get('IP', '0.0.0.0')
port = int(os.environ.get('PORT', 8080))
if __name__ == "__main__":
    app.run(host=host, port=port)
    
## SQL lite
