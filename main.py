from _datetime import datetime
from flask import Flask, render_template, request,url_for,redirect,session,g
from flask_sqlalchemy import SQLAlchemy
import json
import math
import os
from werkzeug.utils import secure_filename



#################


app = Flask(__name__)
app.secret_key="uniquesecretkey"




db = SQLAlchemy(app)
with open("config.json","r") as c:
    param = json.load(c)["param"]

app.config['upload_folder']=param['file_path']





#########database####
app.config['SQLALCHEMY_DATABASE_URI']=param["local_host"]
class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_no = db.Column(db.String(11), nullable=True)
    msg = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(20), nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(200), nullable=False)
    content= db.Column(db.String(500), nullable=True)
    date = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(50), nullable=True)
    blogger = db.Column(db.String(20), nullable=True)
#######################




########## HOME #############


@app.route("/")
def home():
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(param['no_of_posts']))
    page=request.args.get('page')
    # page number
    # page=1
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    # posts  in pair of 5**
    posts=posts[(page-1)*int(param['no_of_posts']) :  (page-1)*int(param['no_of_posts'])+ int(param['no_of_posts'])]

    #first page
    if(page==1):
         next='/?page='+str(page+1)
         prev='#'

    # last page

    elif(page==last):
        prev='/?page='+str(page-1)
        next='#'
    else:
        prev = '/?page=' + str(page - 1)
        next = '/?page=' + str(page + 1)


    return render_template("index.html", param=param,posts=posts,prev=prev,next=next)

########## ABOUT ##############

@app.route("/about")
def about():
    return render_template("about.html",param=param)


############# CONTACT ##################


@app.route("/contact", methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        ''''add entries to the contact table'''
        Name = request.form.get('name')
        Email = request.form.get('email')
        PhoneNo = request.form.get('phone_no')
        Msg = request.form.get('msg')
        entry = Contact(name=Name,email=Email,phone_no=PhoneNo, msg=Msg, date=datetime.now())
        db.session.add(entry)
        db.session.commit()


    return render_template("contact.html",param=param)

################ POST ######################


@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",param=param,post=post)


########################### Dashboard ##############################


id=1010
Useradmin='abc'
Passadmin='pass'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.id=id
        user = Useradmin
        g.user = user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']


        if username==Useradmin and password == Passadmin:
            session['user_id'] = id
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html',param=param)

########################### admin profile##############################

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    posts = Posts.query.filter_by().all()


    return render_template('admin profile.html',param=param,posts=posts)

########################### edut post##############################

@app.route('/editPost/<string:sno>', methods=['GET', 'POST'])
def edit(sno):


    if request.method=='POST':

        ntitle = request.form.get('title')
        nsubtitle = request.form.get('subtitle')
        ncontent = request.form.get('content')
        nblogger= request.form.get('blogger')
        nimage =request.form.get('image')
        nslug=request.form.get('slug')
        ndate=datetime.now()

        if sno=='0':  #add a new post in db
            post = Posts(title=ntitle, subtitle=nsubtitle, content=ncontent,blogger=nblogger, image=nimage,slug=nslug,date=datetime.now())
            db.session.add(post)
            db.session.commit()

        else:          # to edit the previous posts
            post = Posts.query.filter_by(sno=sno).first()
            post.title=ntitle
            post.subtitle=nsubtitle
            post.slug=nslug
            post.blogger = nblogger
            post.content=ncontent
            post.date=datetime.now()
            post.image=nimage
            db.session.commit()
            # return redirect('/editPost/'+sno)
            return redirect('/profile')

    post = Posts.query.filter_by(sno=sno).first()

    return render_template('edit post.html',param=param,post=post,sno=sno)

@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    post = Posts.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('/profile')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')

@app.route('/uploader', methods=['GET','POST'])
def uploader():
    if (request.method=='POST'):
        f=request.files['file1']
        f.save(os.path.join(app.config['upload_folder'],secure_filename(f.filename)))
        return 'uploaded successfully'

    return redirect('/profile')











app.run(debug=True)
