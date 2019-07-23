from flask import Flask, redirect, request, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy 
import re
# from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:anika0921@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = b'\xe4\x9d\x9d\x12\xa8y\xf3\xf0\xab\xd6P\xfaz\x98\x8b\xc5'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user
        

class User(db.Model):
     
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogz = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password     

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog_list', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')           

@app.route('/')
def index():
    users = User.query.all() 
    return render_template('index.html', users=users)
    
@app.route('/blogs')
def blog_list():

    user_id = request.args.get('user')
    if user_id == None:
       blogs = Blog.query.order_by(Blog.id.desc()).all() 
       user = User.query.all()
       return render_template('blogs.html', blogs=blogs, user=user)  
    else:
        blogs = Blog.query.filter_by(user_id=user_id).all()  
        user = User.query.all()
        return render_template('blogposts.html', blogs=blogs, user=user) 

@app.route('/new_blog', methods=['POST', 'GET']) 
def new_blog():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        user = User.query.filter_by(username=session['username']).first()
        
        invalid = False
        title_error = None
        body_error = None

        if len(title.strip()) == 0:
            title_error = "Please fill the title of your new blog post"
            invalid = True
        if body == None or len(body.strip()) == 0:
            body_error =  "Please fill the body of your new blog post"  
            invalid = True 
        if invalid:
            return render_template('new_blog.html',title=title, body=body, title_error=title_error, body_error=body_error)
        else:    
            new_blog = Blog(title, body, user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect(url_for('blog', id=new_blog.id))   
    else:
        return render_template('new_blog.html')

@app.route('/login', methods=['POST', 'GET'])
def login(): 
    if 'username' in session:
        return redirect('/')  
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/')
        else:
            error = "Username doesn't exist or password is incorrect."
            return render_template('login.html', error=error)    
    else: 
        return render_template('login.html')  

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['vpassword']

        invalid = False
        username_error = None
        password_error = None
        vpassword_error = None
        duplicate_error = None


        valid = re.compile(r"(^[0-9a-zA-Z_]{3,20}$)")

        if not valid.match(username):
            username_error = "That's not valid Username" 
            invalid = True
        if not valid.match(password):
            password_error = "That's not valid Password"
            invalid = True
        if  verify == '' or verify != password:
            vpassword_error = "Passwords don't match"
            invalid = True
        if invalid:    
            return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, vpassword_error=vpassword_error)
        else:
             existing_user = User.query.filter_by(username=username).first()
             if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/new_blog')
             else:
                duplicate_error = True
                return render_template('signup.html', duplicate_error=duplicate_error)
    else:            
        return render_template('signup.html')

@app.route('/blog/<int:id>')
def blog(id):
    blog = Blog.query.get(id)
    user = User.query.get(blog.user_id)
    return render_template('blog.html', title=blog.title, body=blog.body, user=user)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run()
