from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:anika0921@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text())

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    blogs = Blog.query.order_by(Blog.id.desc()).all() 
    return render_template('main.html', blogs=blogs)

@app.route('/new_blog', methods=['POST', 'GET']) 
def new_blog():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

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
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog/'+str(new_blog.id))   
    else:
        return render_template('new_blog.html')

@app.route('/blog/<int:id>')
def blog(id):
    blog = Blog.query.get(id)
    return render_template('blog.html', title=blog.title, body=blog.body )


if __name__ == '__main__':
    app.run()
