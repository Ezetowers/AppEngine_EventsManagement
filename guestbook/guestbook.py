import os
import urllib
import sys
import logging

from google.appengine.api import users
from google.appengine.ext import ndb

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

        # logging.debug(template_values)

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class AddGuest(webapp2.RequestHandler):
    # @ndb.transactional(retries=3)
    def increment_guest_count(self, event_name):
        try:
            events_query = Event.query(ancestor=events_key())
            events = events_query.fetch()

            for event in events:
                if event.name == event_name:
                    # We found the event. increment the count
                    if int(event.capacity) > int(event.guests):

                        amount_guests = int(event.guests) + 1
                        event.guests = str(amount_guests)
                        event.put()
                        break
                    else:
                        return False
        except TransactionFailedError:
            # Exit in this case
            sys.exit(-1)
        finally:
            return True

    def post(self):
        event_name = self.request.get('actualEvent')

        self.increment_guest_count(event_name)

        # Add the guest
        logging.debug("Actual event: " + event_name)

        guest = Guest(parent=event_guests_key(event_name))
        guest.name = self.request.get('guestName')
        guest.surname = self.request.get('guestSurname')
        guest.email = self.request.get('guestEmail')
        guest.company = self.request.get('guestCompany')
        guest.put()

        query_params = {'event_name': event_name}
        self.redirect('/?' + urllib.urlencode(query_params))


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

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/event_creation', EventsCreation),
    ('/add_guest', AddGuest),
], debug=True)
