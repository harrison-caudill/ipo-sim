#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd


# cuz I'm lazy
from position import Grant

GRANTS = [
    Grant(name='rsu',
          vehicle='rsu',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n=1<<0,
          period_months=1),

    Grant(name='nso',
          vehicle='nso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n=1<<1,
          exercised=0,
          sold=0,
          period_months=1),

    Grant(name='iso',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n=1<<2,
          exercised=0,
          sold=0,
          period_months=1),
    ]

constants = {
    'ipo_price_usd': 12,
    'query_date': '9/23/20',

    'palantir_401k_usd': 0,
    'palantir_fsa_usd': 0,
    'palantir_drca_usd': 0,
    'reg_income_usd': 0,
    'ext_amt_income_usd': 0,
    'fed_withheld_usd': 0,
    'state_withheld_usd': 0,
    }
MODEL = pylink.DAGModel([deathAnd.Taxes(),
                         myMeager.Income(),
                         anAwkward.Position(GRANTS)],
                        **constants)
