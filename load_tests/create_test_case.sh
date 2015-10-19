#!/bin/bash
/usr/bin/python ./create_test_case.py $1 $2 $3 $4

sed -i 's/&lt;/</g' $4
sed -i 's/amp;//g' $4
sed -i 's/&gt;/>/g' $4
