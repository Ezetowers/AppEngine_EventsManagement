from google.appengine.ext import ndb
from Model.Model import *

import webapp2
import json
import logging

class AddGuest(webapp2.RequestHandler):
    @ndb.transactional(xg=True)
    def increment_guest_count(self, event_name):
        # Get the event
        events_query = Event.query(Event.name == event_name,
                                   ancestor=events_key())
        event = events_query.get()

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

    def guest_exists(self, guest_email, event):
        guest_query = Guest.query(Guest.email == guest_email,
                                  ancestor=event_guests_key(event))
        guest = guest_query.get()
        if guest:
            logging.warning(
                "Guest with email " + guest_email
                + " already exists. Dropping request")
            return True
        return False

    def post(self):
        event_name = self.request.get('actualEvent')
        check_duplicates = self.request.get('checkDuplicates')

        if check_duplicates == "true" and\
            self.guest_exists(self.request.get('guestEmail'), event_name):
            self.response.headers['Content-Type'] = "application/json"
            self.response.out.write(json.dumps({'add': 'duplicated'}))
            return

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
            self.response.out.write(json.dumps({'add': 'true'}))

