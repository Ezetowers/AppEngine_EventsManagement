import os
from Model.Model import *
from Handlers.AddGuest import AddGuest
from Handlers.EventsCreation import EventsCreation
from Handlers.EventRemoval import EventRemoval

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


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


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/updater', MainPage),
    ('/event_creation', EventsCreation),
    ('/event_removal', EventRemoval),
    ('/add_guest', AddGuest),
], debug=True)
