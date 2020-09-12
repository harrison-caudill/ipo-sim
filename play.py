#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd


# cuz I'm lazy
from position import Grant

GRANTS = [
    Grant(name='test-grant',
          vehicle='iso',
          strike_usd=1.00,
          start='1/1/10',
          n_periods=48,
          n=10000,
          exercised=0,
          sold=0),
    ]

class Private(object):
    def __init__(self):
        self.tribute = {
            'palantir_401k_usd': 0,
            'palantir_fsa_usd': 0,
            'palantir_drca_usd': 0,
            'reg_income_usd': 0,
            'ipo_price_usd': round(35/2.3, 2),
            'ipo_date': '9/23/20',
            'query_date': '9/23/20',
            'fed_withheld': 0,
            }

if __name__ == '__main__':
    model = pylink.DAGModel([
        Private(),
        deathAnd.Taxes(),
        myMeager.Income(),
        anAwkward.Position(GRANTS)])

    grants = {}
    for g in GRANTS: grants[g.name] = g

    m = model
    e = m.enum

    for name in grants:
        g = grants[name]
        if g.vehicle == 'rsu' or True:
            #print('%10s: %d' % (g.name, g.vested_outstanding('9/9/20')))
            g.sale_qty = g.n

    moneys = round(m.rsu_income_usd + m.nso_income_usd, 2)

    fed = m.fed_taxes_usd - m.fed_withheld
    state = round(m.state_taxes_usd, 2)
    taxes = round(fed + state, 2)

    print("Price per Share: %s d" % m.ipo_price_usd)

    print(moneys, taxes)

    print(moneys - taxes, float(int(1000 * taxes / (moneys+m.reg_income_usd))/10))
