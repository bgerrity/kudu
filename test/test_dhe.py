#! /usr/bin/env python3
# test/test_dhe.py

import sys, os
sys.path.append(os.path.abspath('../Kudu'))

from lib import easy_crypto as ec

Alice = ec.generate_dh()
Bob = ec.generate_dh()
aliceFinal = ec.generate_dh_shared_secret(Alice, ec.export_dh_public(Bob))
bobFinal = ec.generate_dh_shared_secret(Bob, ec.export_dh_public(Alice))

print(aliceFinal == bobFinal)

# print(int(bin(bobFinal), base=2) == aliceFinal)
