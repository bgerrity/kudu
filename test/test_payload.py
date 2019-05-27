#! /usr/bin/env python3
# test/test_payload.py

import sys, os

sys.path.append(os.path.abspath('../Kudu'))

from lib import payload as pl

# local changes
pl.ADDRESS_SIZE = 3
pl.MESSAGE_SIZE = 10

pay = pl.Payload("foo".encode(), "bar".encode(), "saltywater".encode())
print(pay)

expor = pl.export_payload(pay)
print(expor)

impor = pl.import_payload(expor)
print(impor)


