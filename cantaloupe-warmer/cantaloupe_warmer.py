""" Request a bunch of images from Cantaloupe by running through ranges of
book object pages.
"""

from string import Template
import requests

namespace = 'smith'
ranges = [
    {'start': 104191, 'rangesize': 3000},
    {'start': 29933, 'rangesize': 1700},
    {'start': 28512, 'rangesize': 1400},
    {'start': 107406, 'rangesize': 2700},
]

# Make a template for the URL, where $PIDNUM represents the incrementing pid
# number and $NAMESPACE is the namespace
urlTemplate = Template("https://compass.fivecolleges.edu/iiif/2/$NAMESPACE%3A$PIDNUM~JP2~a27cf65dff6ca913d5bf4d0516e2280b7446763a185e2c5db8f1f8b24f144a00https%3A%2F%2Fcompass.fivecolleges.edu%2Fislandora%2Fobject%2F$NAMESPACE%253A$PIDNUM%2Fdatastream%2FJP2%2Fview%3Ftoken%3Da27cf65dff6ca913d5bf4d0516e2280b7446763a185e2c5db8f1f8b24f144a00/full/pct:25/0/default.jpg")

for myrange in ranges:
    for pid in range(myrange['start'], myrange['start'] + myrange['rangesize']):
        url = urlTemplate.substitute(NAMESPACE = namespace, PIDNUM = pid)
        r = requests.get(url)
        print(url)
