from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:kasey@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '123456'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(160))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.args.get('id'):
        ind_id= request.args.get('id')
        ind_blog = Blog.query.filter_by(id=ind_id).all()
        return render_template('singleUser.html', ind_blog=ind_blog)
    elif request.args.get('user'):
        ind_user = request.args.get('user')
        ind_post= Blog.query.filter_by(owner_id=ind_user).all()
        return render_template('singleUser.html', ind_post=ind_post)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="Blogz", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        blog = Blog (request.form['name'], request.form['body'], owner)
        body = request.form['body']
        name = request.form['name']

        new_title_error = ''
        new_entry_error = ''

        if  body == '' and name == '':
            new_entry_error= 'Please enter a new entry'
            new_title_error = 'Please enter a title' 

        
        if  new_title_error and new_entry_error != '':
            return render_template('newpost.html', new_title_error=new_title_error, new_entry_error=new_entry_error)
        
        else:
            db.session.add(blog)
            db.session.commit()
            blog = Blog.query.get(blog.id)
            return render_template('singlepost.html', blog=blog, owner=owner)

    else:
        return render_template('newpost.html', owner=owner)

@app.route('/singlepost', methods=['GET', 'POST'])
def singlepost():

    id = request.args.get('id')

    blog = Blog.query.get(id)
    return render_template('singlepost.html', title="Blogz", blog=blog)

@app.route('/singleUser', methods=['GET'])
def singleUser():
    owner = User.query.filter_by(username=session['username']).first()
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('singleUser.html',title="Blogz", blogs=blogs, owner=owner)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        
        if username == '':
            flash('Please enter a valid username')
        if existing_user == True:
            flash('Duplicate user')
        if password == '':
            flash('Please enter a valid password')
        if verify == '':
            flash('Please enter a valid password')
        if password != verify:
            flash('Passwords do not match')
        if len(username) < 3 or len(username) > 20:
            flash( 'Invalid username')
        if len(password) < 3 or len(password) > 20:
            flash('Invalid password')   

            return render_template('signup.html')

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
    return render_template('newpost.html', username=username)
            
            
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')      
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first() 
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    return render_template('login.html')       
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', titile="Bloggerz", users=users)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()