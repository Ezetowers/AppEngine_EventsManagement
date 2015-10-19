from Model.Model import *
from Model.Model import Event

import webapp2
import urllib


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
