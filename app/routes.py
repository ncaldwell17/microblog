# The routes are different URLs that the application can implement
# In Flask, application routes are written as Python functions, which
#   are called view functions.
# View functions are mapped to one or more route URLs so Flask knows what
#   logic to implement when a client requests a certain URL.
from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime

# the name of the view function is equivalent to the name of the html file
# it is also contained within the decorator 


# decorators are a unique Pythonic thing
# they're often used as callbacks for certain events
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# this decorator is imported by flask_login, prevents people from accessing
#   index that haven't logged in first. 
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        # it is standard practice to respond to a POST request with a redirect
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    # instead of the .all() method, I will now be using paginate 
    # using the paginate function returns an object of class paginate
    # .items is an attribute of the object, that contains the list of 
    #       all the items retrieved for the selected page
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


# these additional arguments 'methods' overwrite the default
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # handles case if logged-in user still tries to get to the login page 
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # does all the processing work after confirmation FALSE
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
        # flash method shows a message to user 
        # this message also needs to be formatted by code author
        #   in the base template html 
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        # redirect automatically navigates the browser to new page
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/joe')
def joe():
    param = request.args.get('foo','you didnt send anything')
    return jsonify({
        'input': param,
        'output': param.upper()
    })


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congradulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# this app.route has a dynamic component indicated by the <...>
@app.route('/user/<username>')
@login_required
def user(username):
    # query sends a message to the database
    # the .first_or_404() method lets me raise an exception if user is not found
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    # paginate takes in 1) the first page number, 2) num of items per page
    #       AND, 3) an error flag 
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                            next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        # there is no need to call db.session.add() before the commit
        #   because the reference current_user already put it there 
        # commits the data from the session to the actual database
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # allows the program to access the original username
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    # error checking
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    # error checking
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    # this is the same call as the main page, but without the form 
    return render_template('index.html', 
                            title='Explore', 
                            posts=posts.items,
                            next_url=next_url,
                            prev_url=prev_url)





