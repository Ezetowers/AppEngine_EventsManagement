import os
import urllib
import sys
import logging

from google.appengine.api import users
from google.appengine.ext import ndb
import google.appengine.ext.db

import jinja2
import webapp2
import json


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    

# Store all the events with the same key just because google said it is 
# necessary
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
    email = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    surname = ndb.StringProperty(indexed=False)
    company = ndb.StringProperty(indexed=False)


class MainPage(webapp2.RequestHandler):
    def get(self):
        events_query = Event.query(ancestor=events_key())
        events = events_query.fetch()

        guest_list = []
        for event in events:
            guest_query = Guest.query(ancestor=event_guests_key(event.name))
            guests_by_event = guest_query.fetch()
            guest_list.append((event.name, guests_by_event))

        template_values = {
            'events': events,
            'guests_list': guest_list
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class AddGuest(webapp2.RequestHandler):
    @ndb.transactional(xg=True)
    def increment_guest_count(self, event_name):
        events_query = Event.query(ancestor=events_key())
        events = events_query.fetch()

        for event in events:
            if event.name == event_name:
                # We found the event. increment the count
                logging.debug(
                    "Event: " + event_name +
                    " - Capacity: " + event.capacity)
                logging.debug(
                    "Event: " + event_name +
                    " - Guests: " + event.guests)
                if int(event.capacity) > int(event.guests):
                    logging.debug(
                        "Event " + event_name +
                        ": There is capacity")
                    amount_guests = int(event.guests) + 1
                    event.guests = str(amount_guests)
                    event.put()
                    return True
                else:
                    logging.debug(
                        "Event " + event_name +
                        ": There ISN'T capacity")
                    return False

    def post(self):
        event_name = self.request.get('actualEvent')

        if not self.increment_guest_count(event_name):
            self.response.headers['Content-Type'] = "text/plain"
            self.response.out.write(json.dumps({'add': 'false'}))
            return
        else:
            # Add the guest
            guest = Guest(parent=event_guests_key(event_name))
            guest.name = self.request.get('guestName')
            guest.surname = self.request.get('guestSurname')
            guest.email = self.request.get('guestEmail')
            guest.company = self.request.get('guestCompany')
            guest.put()

            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps({'add' : 'true'}))

class EventsCreation(webapp2.RequestHandler):
    def post(self):
        # Get all the events to check if the event already exists
        name = self.request.get('eventName')
        capacity = int(self.request.get('eventCapacity'))

        # Upload a new event if this name and capacity are valid
        if name:
            event = Event(parent=events_key())
            event.name = name
            event.capacity = str(capacity)
            event.guests = str(0)
            event.put()

        query_params = {'event_name': name}
        self.redirect('/?' + urllib.urlencode(query_params))


class EventRemoval(webapp2.RequestHandler):
    @ndb.transactional(xg=True)
    def delete_event(self, event_name):
        events_query = Event.query(ancestor=events_key())
        events = events_query.fetch()

        for event in events:
            if event.name == event_name:
                logging.warning("DELETING EVENT " + event_name)
                event.key.delete()
            else:
                return False

        # Delete all the guests related with this event
        guests_query = Guest.query(ancestor=event_guests_key(event_name))
        guests = guests_query.fetch()

        logging.warning("DELETING GUESTS OF EVENT" + event_name)
        for guest in guests:
            guest.key.delete()

        return True

    def post(self):
        actual_event = self.request.get('event')
        logging.debug("Event to remove: " + actual_event)

        if self.delete_event(actual_event):
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps({'deleted' : 'true'}))
        else:
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps({'deleted' : 'false'}))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/updater', MainPage),
    ('/event_creation', EventsCreation),
    ('/event_removal', EventRemoval),
    ('/add_guest', AddGuest),
], debug=True)
