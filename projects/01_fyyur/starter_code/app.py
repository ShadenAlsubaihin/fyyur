#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
import sys
from pprint import pprint
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  current_time = datetime.now()

  areas = db.session.query(Venue).distinct(Venue.city, Venue.state).with_entities(Venue.city, Venue.state)
  data = []
  for area in areas:
    venues = db.session.query(Venue).filter(Venue.city == area.city, Venue.state == area.state)
    venues_data = []
    for venue in venues:
      venue_data = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": db.session.query(Show).filter(Show.start_time >= current_time, Show.venue_id == venue.id).count()
      }
      venues_data.append(venue_data)

    area_data = {
      "city": area.city,
      "state": area.state,
      "venues": venues_data
    }
    data.append(area_data)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  current_time = datetime.now()

  search_term = request.form.get('search_term', '')
  search_term = '%{0}%'.format(search_term)
  venues = Venue.query.filter(Venue.name.ilike(search_term)).all()

  venues_data = []
  for venue in venues:
    venue_data = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': db.session.query(Show).filter(Show.start_time >= current_time, Show.venue_id == venue.id).count()
    }
    venues_data.append(venue_data)
  
  data = {
    'count': len(venues),
    'data': venues_data
  }

  return render_template('pages/search_venues.html', results=data, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  current_time = datetime.now()

  venue = Venue.query.get(venue_id)

  upcoming_shows = []
  past_shows = []

  # upcoming shows
  for artist, show in db.session.query(Artist, Show).join(Show).filter(Show.start_time >= current_time, Show.venue_id == venue.id).all():
    show_data = {
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.isoformat()
    }
    upcoming_shows.append(show_data)

  # past shows
  for artist, show in db.session.query(Artist, Show).join(Show).filter(Show.start_time < current_time, Show.venue_id == venue.id).all():
    show_data = {
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.isoformat()
    }
    past_shows.append(show_data)


  data_res = {
    "id": venue.id, 
    "name": venue.name, 
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state, 
    "phone": venue.phone, 
    "website": venue.website, 
    "facebook_link": venue.facebook_link, 
    "seeking_talent": venue.seeking_talent, 
    "seeking_description": venue.seeking_description, 
    "image_link": venue.image_link, 
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data_res)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_talent = True if not (request.form.get('seeking_talent', None) is None) else False
    seeking_description = form.seeking_description.data
    
    venue = Venue(
      name = name,
      city = city,
      state = state,
      phone = phone,
      address = address,
      genres = genres,
      image_link = image_link,
      facebook_link = facebook_link,
      website = website,
      seeking_talent = seeking_talent,
      seeking_description = seeking_description)
    
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue  ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue  ' + request.form['name'] + ' was successfully listed!')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = Artist.query.all()
  data = []
  for artist in artists:
    artist_data = {
      'id': artist.id,
      'name': artist.name
    }
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  current_time = datetime.now()

  search_term = request.form.get('search_term', '')
  search_term = '%{0}%'.format(search_term)
  artists = Artist.query.filter(Artist.name.ilike(search_term)).all()


  artists_data = []
  for artist in artists:
    artist_data = {
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': db.session.query(Show).filter(Show.start_time >= current_time, Show.artist_id == artist.id).count()
    }
    artists_data.append(artist_data)
  
  
  data = {
    'count': len(artists),
    'data': artists_data
  }

  
  return render_template('pages/search_artists.html', results=data, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  current_time = datetime.now()

  artist = Artist.query.get(artist_id)

  upcoming_shows = []
  past_shows = []

  # upcoming shows
  for venue, show in db.session.query(Venue, Show).join(Show).filter(Show.start_time >= current_time, Show.artist_id == artist.id).all():
    show_data = {
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.isoformat()
    }
    upcoming_shows.append(show_data)

  # past shows
  for venue, show in db.session.query(Venue, Show).join(Show).filter(Show.start_time < current_time, Show.artist_id == artist.id).all():
    show_data = {
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.isoformat()
    }
    past_shows.append(show_data)
  

  data_res = {
    "id": artist.id, 
    "name": artist.name, 
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state, 
    "phone": artist.phone, 
    "website": artist.website, 
    "facebook_link": artist.facebook_link, 
    "seeking_venue": artist.seeking_venue, 
    "seeking_description": artist.seeking_description, 
    "image_link": artist.image_link, 
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data_res)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = True if not (request.form.get('seeking_venue', None) is None) else False
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.address = form.address.data
    venue.genres = form.genres.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website = form.website_link.data
    venue.seeking_venue = True if not (request.form.get('seeking_talent', None) is None) else False
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  form = ArtistForm(request.form)
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website_link.data
    seeking_venue = True if not (request.form.get('seeking_venue', None) is None) else False
    seeking_description = form.seeking_description.data
    
    artist = Artist(
      name = name,
      city = city,
      state = state,
      phone = phone,
      genres = genres,
      image_link = image_link,
      facebook_link = facebook_link,
      website = website,
      seeking_venue = seeking_venue,
      seeking_description = seeking_description)
    
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Artist  ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  response = []

  for show, artist, venue in db.session.query(Show,Artist, Venue).join(Venue).join(Artist):
    data = {
      'venue_id': venue.id,
      'venue_name': venue.name,
      'artist_id': artist.id,
      'artist_name': artist.name,
      'artist_image_link': artist.image_link,
      'start_time': show.start_time.isoformat()
    }

    response.append(data)

  return render_template('pages/shows.html', shows=response)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  form = ShowForm(request.form)
  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data
    
    show = Show(
      artist_id = artist_id,
      venue_id = venue_id,
      start_time = start_time)
    
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
