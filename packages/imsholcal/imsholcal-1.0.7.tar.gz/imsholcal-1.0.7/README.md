# imsholcal
exchange holiday calendar business day offset package

all country codes used are 3 letter ISO country codes, in lower case. dependant packages are:
os
pandas.tseries.offsets
pandas

see example use below for getting date 3 business days ago using aus holiday calendar:

from imsholcal.business_day import exch_hols
from datetime import datetime
import pytz

tminus_2 = (datetime.now(pytz.timezone('Australia/Sydney')) - exch_hols(3,'aus')).strftime("%m/%d/%Y")
