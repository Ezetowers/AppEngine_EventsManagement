from google.appengine.api import users
from google.appengine.ext import ndb

""" This class has the DTOs used to retrieve and store data from the 
    DB and also has the keys to obtain them

    Store all the events with the same key just because google said it is 
    necessary
"""

DEFAULT_EVENT_BOX = '-'


def events_key():
    return ndb.Key('global', DEFAULT_EVENT_BOX)


def event_guests_key(event_name):
    return ndb.Key('Event', event_name)


class Event(ndb.Model):
    name = ndb.StringProperty()
    capacity = ndb.StringProperty()
    # Amount of Guests in the Event
    guests = ndb.StringProperty(indexed=False)


class Guest(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    surname = ndb.StringProperty(indexed=False)
    company = ndb.StringProperty(indexed=False)