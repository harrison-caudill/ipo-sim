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

# Married filing jointly numbers
fed_married_joint = {
    0      : 0.1,
    19750  : 0.12,
    80250  : 0.22,
    171050 : 0.24,
    326600 : 0.32,
    414700 : 0.35,
    622050 : 0.37
    }

fed_single = {
    0      : 0.1,
    19750/2  : 0.12,
    80250/2  : 0.22,
    171050/2 : 0.24,
    326600/2 : 0.32,
    414700/2 : 0.35,
    622050/2 : 0.37
    }

# Married filing jointly numbers
ca_married = {
    0 : 0.01,
    17618 : 0.02,
    41766 : 0.04,
    65920 : 0.06,
    91506 : 0.08,
    115648 : 0.093,
    590746 : 0.103,
    708890 : 0.113,
    1181484 : 0.123,
    1999999 : 0.133
    }

# california single
ca_single = {
    0 : 0.01,
    8809 : 0.02,
    20883 : 0.04,
    32960 : 0.06,
    45753 : 0.08,
    57824 : 0.093,
    295371 : 0.103,
    354445 : 0.113,
    590742 : 0.123,
    1000000 : 0.133
    }


constants = {

    # Married filing jointly numbers
    'fed_tax_table': fed_married_joint,
    'state_tax_table': ca_married,
    'fed_std_deduction_usd': 24800,
    'amt_exemption_usd': 113400,
    'state_std_deduction_usd': 4537,

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
