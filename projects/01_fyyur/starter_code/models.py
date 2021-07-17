from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    start_time = db.Column('start_time', db.DateTime)
#   artist = db.relationship("Artist", back_populates="venues")
#   venue = db.relationship("Venue", back_populates="artists")

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref = 'venue', lazy = True)
    # artists = db.relationship("Show", back_populates="venue")


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref = 'artist', lazy = True)
    # venues = db.relationship("Show", back_populates="artist")
    # genres = db.relationship('ArtistGenres', backref='artist', lazy=True)
