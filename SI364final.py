###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField, SelectMultipleField, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length, Email, Regexp, EqualTo # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
import requests
import json
import random
import hashlib 
import calendar
import time
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash

# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

## App setup code
app = Flask(__name__)
app.debug = True

## All app.config values
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string from si364'

## Setup code for Heroku
app.config['HEROKU_ON'] = os.environ.get('HEROKU')

## Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://daniellemeyerson@localhost:5432/danimeye_final"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
# App addition setups
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager


######################################
######## HELPER FXNS (If any) ########
######################################



#############################
##### ASSOCATION TABLES #####
#############################

user_collection = db.Table('user_collection',db.Column('personalComicCollection_id',db.Integer, db.ForeignKey('personalComicCollections.id')),db.Column('comics_id',db.Integer, db.ForeignKey('comics.id')))

##################
##### MODELS #####
##################

# Special model for users to log in
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    personal_comic_collections = db.relationship("PersonalComicCollection", backref = "User")


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

## DB load function
## Necessary for behind the scenes login manager that comes with flask_login capabilities! Won't run without this.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None

# Other models
class Character(db.Model): # Characters Table (the 'one')
    __tablename__ = "characters"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(500))
    thumbnail = db.Column(db.String(500))
    char_api_id = db.Column(db.Integer)
    comics = db.relationship("Comic", backref = "Character") # establishes the one-to-many relationship with Comic

    def __repr__(self):
        return "{}: {}".format(self.name, self.description)

class Comic(db.Model): # Comics Table (the 'many')
    __tablename__ = "comics"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    thumbnail = db.Column(db.String(500))
    char_id = db.Column(db.Integer, db.ForeignKey('characters.id')) # creates foreign key with character id 

    def __repr__(self):
        return "{}".format(self.name)

class PersonalComicCollection(db.Model):
     __tablename__ = "personalComicCollections"
     id = db.Column(db.Integer, primary_key = True)
     name = db.Column(db.String(255))
     user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
     comics = db.relationship('Comic', secondary = user_collection, backref = db.backref('personComicCollections', lazy = 'dynamic'), lazy = 'dynamic')

###################
###### FORMS ######
###################

# Provided
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

# Provided
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class MarvelForm(FlaskForm):
    name = StringField("Please enter a Marvel character.",validators=[Required()])
    submit = SubmitField("Submit")

    def validate_name(self, field):
        name_len = len(field.data)
        if name_len > 20:
            raise ValidationError("This name is longer than 20 characters. Please enter a different name.")

class ComicSearchForm(FlaskForm):
    comic_keyword = StringField("Search for a comic.", validators=[Required()])
    submit = SubmitField("Submit")

    def validate_comic_keyword(self, field):
        keyword_len = len(comic_keyword)
        if keyword_len > 100:
            raise ValidationError("This comic search is longer than 100 characters. Please enter a different comic.")

class CollectionCreateForm(FlaskForm):
    name = StringField('Collection Name',validators=[Required()])
    comic_picks = SelectMultipleField('Select the comics you want to include in this collection', validators=[Required()], coerce=int)
    submit = SubmitField("Create Collection")

    def validate_name(self, field):
        name_len = len(field.data)
        if name_len > 50:
            raise ValidationError("This name is longer than 50 characters. Please enter a different name.")

class UpdateButtonForm(FlaskForm):
    submit = SubmitField("Update")

class UpdateCollectionForm(FlaskForm):
    # name = StringField('Collection Name',validators=[Required()])
    comic_picks = SelectMultipleField('Select the comics you want to include in this collection', validators=[Required()], coerce=int)
    submit = SubmitField("Update Collection")

class DeleteButtonForm(FlaskForm):
    submit = SubmitField("Delete")

class AllComicsButtonForm(FlaskForm):
    submit = SubmitField("<< See All Comics")


## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#########################
###### HELPER FXNS ######
#########################

def get_comic_by_id(id):
    # """Should return gif object or None"""
    comic = Comic.query.filter_by(id=id).first()
    return comic

def get_or_create_comic(python_obj_comics, char_id):
    
    #print(python_obj_comics)
    #print(len(python_obj_comics["data"]["results"][0]["comics"]["items"]))
    comic_list = []
    for comic in python_obj_comics["data"]["results"]:
        comic_thumbnail_path = comic["thumbnail"]["path"] + "/portrait_uncanny.jpg"
        comic_title = comic["title"]
        comic_list.append((comic_title, comic_thumbnail_path))
        # print('test')
        # print(comic['name'])
    #print(comic_list)
    for comic in comic_list:
        comic_exists = Comic.query.filter_by(name = comic[0]).first()
        if not comic_exists:
            new_comic = Comic(name = comic[0], thumbnail = comic[1], char_id = char_id)
            db.session.add(new_comic)
            db.session.commit()
    return comic_list

def get_or_create_character(char_name):
    
    ts = str(calendar.timegm(time.gmtime()))
    priv_key = '357ac06e58c9b720d295a5c3623180a643a11eba'
    pub_key = '57cf9e503f7a88616af606035c5460dd'
    hash_string = ts + priv_key + pub_key
    m = hashlib.md5(hash_string.encode())
    api_hash = m.hexdigest()
        # api_hash = hash(priv_key+pub_key+ts)
    params_diction = {}
    params_diction['ts'] = ts
    params_diction['apikey'] = pub_key
    params_diction['hash'] = api_hash
    entered_character = Character.query.filter_by(name = char_name).first()
    if entered_character:
        flash('You have already searched for this Marvel chracter.')
        return entered_character
    else:
        params_diction['name'] = char_name 
        base_url = "https://gateway.marvel.com/v1/public/characters"
        resp = requests.get(base_url, params = params_diction)
        text = resp.text
        #print(resp.url)
        # print(text)
        python_obj = json.loads(text)
        #print(python_obj)

        if python_obj["data"]["results"][0]["comics"]["items"]:
            thumbnail = python_obj["data"]["results"][0]["thumbnail"]["path"] + "/portrait_uncanny.jpg"
            char_api_id = python_obj["data"]["results"][0]["id"]
            description = python_obj["data"]["results"][0]["description"]
            new_character = Character(name = char_name, description = description, thumbnail = thumbnail, char_api_id = char_api_id)
            db.session.add(new_character)
            db.session.commit()
            # make an api call to /v1/public/characters/{characterID}/comics
            # make a list of comics to send to get or create

            #base_url_comics = "https://gateway.marvel.com/v1/public/characters/" + '1009268'+ "/comics"
            base_url_comics = "https://gateway.marvel.com/v1/public/characters/" + str(char_api_id) + "/comics"
            del params_diction['name']
            resp_comics = requests.get(base_url_comics, params = params_diction)
            text_comics = resp_comics.text
            print(resp_comics.url)
            python_obj_comics = json.loads(text_comics)
            print(python_obj_comics)

            get_or_create_comic(python_obj_comics, new_character.id)
            return new_character

        else:
            flash("Sorry! please search for a different character.")
            

def get_or_create_collection(name, current_user, comic_list=[]):
    # """Always returns a PersonalGifCollection instance"""
    comicCollection = PersonalComicCollection.query.filter_by(name=name, user_id = current_user.id).first()
    if comicCollection:
        return comicCollection
    else:
        comicCollection = PersonalComicCollection(name = name, user_id = current_user.id, comics= [])
        for comic in comic_list:
            comicCollection.comics.append(comic)
        db.session.add(comicCollection)
        db.session.commit()
        return comicCollection

#######################
###### VIEW FXNS ######
#######################
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('home'))

@app.route('/register',methods=["GET","POST"])
def register():
    form2 = RegistrationForm()
    if form2.validate_on_submit():
        user = User(email=form2.email.data,username=form2.username.data,password=form2.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form2=form2)


@app.route('/', methods=['GET', 'POST'])
def home():
    form = MarvelForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    #print(form)
    if form.validate_on_submit():
        #print("hi")
        name = form.name.data
        character = get_or_create_character(name)
        # if character:
        return redirect(url_for('all_characters'))
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
        return redirect(url_for('home'))
    #print(form.errors)
    return render_template("home.html", form = form)

@app.route('/characters') # returns all searched for characters
def all_characters():
    form = MarvelForm()
    characters = Character.query.all()
    #print(characters)
    return render_template('all_characters.html', form = form, all_characters = characters)

@app.route('/comics', methods = ['GET']) # returns all comics categorized by character 
def all_comics():
    search_form = ComicSearchForm(request.args)
    comic_dict = {}
    if len(request.args):
        comics = Comic.query.filter_by(name = search_form.comic_keyword.data).all()
        if comics:
            print("INSIDE IF")
            print(comics)
            char_name = Character.query.filter_by(id=comics[0].char_id).first()
            comic_dict[char_name.name] = [comics[0]]
        else:
            flash("No matches found. Please enter a new comic.")
            return redirect(url_for("all_comics"))
    else:
        comics = Comic.query.all()
        comic_dict = {}
        #characters = Character.query.all()
        for character in Character.query.all():
            current_id = character.id
            #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            #print(current_id)
            comic_by_character_id = Comic.query.filter_by(char_id = current_id).all() # a list of all comics filtered by id 
            #print(comic_by_character_id)
            comic_list = []
            for comic in comic_by_character_id:
                comic_list.append(comic)
            #print(comic_list)
            comic_dict[character.name] = comic_list
    return render_template('all_comics.html', form = search_form, comic_dict = comic_dict)


@app.route('/create_collection',methods=["GET","POST"])
@login_required
def create_collection():
    form = CollectionCreateForm()
    comics = Comic.query.all()
    choices = [(c.id, c.name) for c in comics]
    form.comic_picks.choices = choices
    #print("HI")
    #print(form.validate_on_submit())
    if request.method =='POST':
        #print("$$$$")
        selected_comics = form.comic_picks.data
        selected_comic_obj = []
        for comic in selected_comics:
            this_comic = get_comic_by_id(int(comic))
            selected_comic_obj.append(this_comic)
        new_comic_collection = get_or_create_collection(name = form.name.data, current_user= current_user, comic_list = selected_comic_obj)
        #print(new_comic_collection.comics)
        return redirect(url_for("collections"))
    return render_template("create_collection.html", form = form)


@app.route('/collections')
@login_required
def collections():
    form_del = DeleteButtonForm()
    form_up = UpdateButtonForm()
    current_user_comic_collections = PersonalComicCollection.query.filter_by(user_id = current_user.id) # is it enough to filter by id?
    return render_template("collections.html", collections = current_user_comic_collections, form_del = form_del, form_up = form_up)

@app.route('/collection/<id_num>')
def single_collection(id_num):
    # form = UpdateButtonForm()
    id_num = int(id_num)
    collection = PersonalComicCollection.query.filter_by(id=id_num).first()
    comics = collection.comics.all()
    print(comics)
    return render_template('collection.html',collection=collection, comics=comics)

@app.route('/update/<collection_name>',methods=["GET","POST"])
def update(collection_name):
    form = UpdateCollectionForm() 
    comics = Comic.query.all()
    print(comics)
    choices = [(c.id, c.name) for c in comics]
    form.comic_picks.choices = choices
    if form.validate_on_submit():
        print("INSIDE THE IF")
        selected_comics = form.comic_picks.data
        selected_comic_obj = []
        for comic in selected_comics:
            this_comic = get_comic_by_id(int(comic))
            selected_comic_obj.append(this_comic)
        this_collection = PersonalComicCollection.query.filter_by(name = collection_name).first()
        this_collection.comics = selected_comic_obj
        db.session.commit()
        flash("{} has been successfully updated".format(this_collection.name))
        return redirect(url_for('collections'))
    return render_template('update_collection.html', name = collection_name, form = form)


@app.route('/delete/<collection_id>',methods=["GET","POST"])
def delete(collection_id):
    this_collection = PersonalComicCollection.query.filter_by(id = collection_id).first()
    db.session.delete(this_collection)
    db.session.commit()
    flash("Successfully deleted {}".format(this_collection.name))
    return redirect(url_for('collections'))


## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
