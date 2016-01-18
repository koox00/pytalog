import os
import random
import string
import httplib2
import json
import requests
from functools import wraps

from flask import (render_template, request, redirect,
                   jsonify, url_for, flash, make_response,
                   session as login_session, abort, send_from_directory)

from pytalog import app, db
from models import Restaurant, MenuItem, User
from urlparse import urljoin
from werkzeug import secure_filename
from werkzeug.contrib.atom import AtomFeed
from oauth2client.client import (flow_from_clientsecrets, FlowExchangeError)
# Google oauth api credentials
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# Generate csrf token
def generate_csrf_token():
    if 'state' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
    return login_session['state']

# Make csrf_token() function global for the views
app.jinja_env.globals['csrf_token'] = generate_csrf_token


def login_required(f):
    """Decorator function for authenticated routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# Check before every POST for the csrf token
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = login_session.pop('state', None)
        if not token or \
            (token != request.form.get('csrf_token') and
             token != request.args.get('state')):
            abort(403)


# Error Page Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbbiden(e):
    response = make_response(
        json.dumps("This request is forbidden on this server."), 403)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.route('/login')
def showLogin():
    return render_template('login.html')


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    login_session['user_id'] = getUserID(login_session['email'])

    if login_session['user_id'] is None:
        login_session['user_id'] = createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '''
     "style="width: 300px; height: 300px;
     border-radius: 150px;
     -webkit-border-radius: 150px;
     -moz-border-radius: 150px;">
     '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    db.session.add(newUser)
    db.session.commit()
    user = User.query.filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    """Return user's id by email"""
    try:
        user = User.query.filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        print 'yes'
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print result
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def make_external(url):
    return urljoin(request.url_root, url)


# Atom FEED Endpoints for recent items
@app.route('/restaurants.atom')
def restaurant_feed():
    feed = AtomFeed('Recent Restaurants',
                    feed_url=request.url, url=request.url_root)
    restaurants = Restaurant.newest(10)
    for restaurant in restaurants:
        feed.add(restaurant.name, unicode(restaurant.menu_items_str),
                 content_type='html',
                 author=restaurant.user.name,
                 url=make_external(restaurant.url),
                 updated=restaurant.last_update,
                 published=restaurant.published)
    return feed.get_response()


# JSON APIs to view Restaurant Information
@app.route('/restaurants.JSON')
def restaurantsJSON():
    restaurants = Restaurant.query.all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# JSON APIs to view Restaurant Information
@app.route('/restaurants/<int:id>.JSON')
def restaurantJSON(id):
    items = Restaurant.query.filter_by(
        id=id).all()
    return jsonify(Restaurant=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/menu.JSON')
def restaurantMenuJSON(restaurant_id):
    # restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    items = MenuItem.query.filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>.JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = MenuItem.query.filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


# Show all restaurants
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = Restaurant.query.order_by(Restaurant.name)
    if 'username' not in login_session:
        return render_template('publicrestaurants.html',
                               restaurants=restaurants)
    else:
        return render_template('restaurants.html', restaurants=restaurants)


# Create a new restaurant
@app.route('/restaurants/new/', methods=['GET', 'POST'])
@login_required
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(
            name=request.form['name'], user_id=login_session['user_id'])
        db.session.add(newRestaurant)
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        db.session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


# Edit a restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
    editedRestaurant = Restaurant.query.filter_by(id=restaurant_id).first_or_404()
    if not checkOwnership(editedRestaurant):
        return redirect(url_for('showRestaurants'))

    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html',
                               restaurant=editedRestaurant)


# Delete a restaurant
@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteRestaurant(restaurant_id):
    restaurantToDelete = Restaurant.query.filter_by(id=restaurant_id).first_or_404()
    if not checkOwnership(restaurantToDelete):
        return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))

    if request.method == 'POST':
        db.session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        db.session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html',
                               restaurant=restaurantToDelete)


# Show a restaurant menu
@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first_or_404()
    items = MenuItem.query.filter_by(
                                    restaurant_id=restaurant_id).all()
    creator = restaurant.user

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicmenu.html',
                               items=items,
                               restaurant=restaurant,
                               creator=creator)
    else:
        return render_template('menu.html',
                               items=items,
                               restaurant=restaurant,
                               creator=creator)


# Create a new menu item
@app.route('/restaurants/<int:restaurant_id>/menu/new/',
           methods=['GET', 'POST'])
@login_required
def newMenuItem(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    if not checkOwnership(restaurant):
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           course=request.form['course'],
                           restaurant_id=restaurant_id,
                           user_id=restaurant.user_id)
        db.session.add(newItem)
        db.session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


# Edit a menu item
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editMenuItem(restaurant_id, menu_id):
    editedItem = MenuItem.query.filter_by(id=menu_id).one()
    if not checkOwnership(editedItem):
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        if request.files['photo']:
            filename = upload_file(request.files['photo'])
            if filename:
                editedItem.image = filename
        db.session.add(editedItem)
        db.session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               item=editedItem)


# Delete a menu item
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).one()
    if not checkOwnership(restaurant):
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    itemToDelete = MenuItem.query.filter_by(id=menu_id).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html',
                               item=itemToDelete,
                               restaurant_id=restaurant_id)


# Route serving uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


# check if file ext is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Upload file
def upload_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return False


def checkOwnership(model):
    return login_session['user_id'] == model.user.id
