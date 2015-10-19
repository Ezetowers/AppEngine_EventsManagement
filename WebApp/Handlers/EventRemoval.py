from google.appengine.ext import ndb
from Model.Model import *

import webapp2
import json
import logging


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
