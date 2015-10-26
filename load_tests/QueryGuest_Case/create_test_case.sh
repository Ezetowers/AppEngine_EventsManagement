#!/bin/bash

# 1: URL
# 2: Event Name
# 3: Amount cases

function parseXML {
    sed -i 's/&lt;/</g' $1
    sed -i 's/amp;//g' $1
    sed -i 's/&gt;/>/g' $1
}

createEventXMLName="create_event_file.xml"
addGuestsXMLName="add_guests_file.xml"
queryGuestsXMLName="query_guests_file.xml"

/usr/bin/python ./create_event.py $1 $2 $3 $createEventXMLName
parseXML $createEventXMLName

/usr/bin/python ./add_guests.py $1 $2 $3 $addGuestsXMLName
parseXML $addGuestsXMLName

/usr/bin/python ./query_guests.py $1 $2 $3 $queryGuestsXMLName
parseXML $queryGuestsXMLName

