# importing module
from datetime import date
import logging

# Create and configure logger
logging.basicConfig(filename=f"{date.today()}_pitch-hikers.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
log = logging.getLogger()