from google.appengine.ext import ndb
from Model.Model import *

import webapp2
import json
import logging

class QueryGuest(webapp2.RequestHandler):
    def post(self):
        event_name = self.request.get('actualEvent')
        guest_email = self.request.get('queryEmail')
        
        guest_query = Guest.query(Guest.email == guest_email,
                                  ancestor=event_guests_key(event_name))
        guest = guest_query.get()

        exists = ""
        if guest:
            exists = "true"
        else:
            exists = "false"

        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps({'exists': exists}))

