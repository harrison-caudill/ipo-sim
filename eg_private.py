#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd
from position import Grant
from position import from_table


###############################################################################
# Add your grants into the system                                             #
###############################################################################

# This array holds a list of grant objects in any order.  They'll be
# accessible either by index, or by name later on.
GRANTS = [
    # The easiest way to initialize your grant objects is to use a
    # convenience function called from_table.  It is designed to take
    # in a few easy things you can find (such as number of shares, and
    # strike price), as well as three rows from your vesting schedule.
    # Using those three rows, it'll work out the vesting schedule for
    # you.  Check the definition in position.py for more details.
    from_table(name='RSU-TK421',
               vehicle='rsu',
               first_date='11/05/55', first_val=1210,
               second_date='02/05/56', second_val=1657,
               last_date='11/05/59', last_val=447,
               n_shares=26512,
               exercised=0,
               sold=0,
               strike_usd=1.75),

    # Sometimes, they do grants as bonuses
    Grant(name='BonusTigers',
          vehicle='nso',
          strike_usd=2,
          start='1/1/20',
          n_periods=1,
          n_shares=0xdeadbeef,
          exercised=0,
          sold=0,
          period_months=1),

    # If you want to manually specify
    Grant(name='javax.swing',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=0xcafebabe,
          exercised=0,
          sold=0,
          period_months=1),
    ]

###############################################################################
# Select your tax table                                                       #
###############################################################################

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

ny_single = {
    0 : 0.04,
    8500 : 0.045,
    11700 : 0.0525,
    13900 : 0.0590,
    21400 : 0.0621,
    80650 : 0.0649,
    215400 : 0.685,
    1077550 : 0.882
    }


###############################################################################
# Input your constants                                                        #
###############################################################################

__constants = {

    # This is where you select the utilized tax tables
    'fed_tax_table': fed_married_joint,
    'state_tax_table': ca_married,

    # Look up the numbers that are appropriate for your tax filing
    'fed_std_deduction_usd': 24800,
    'amt_exemption_usd': 113400,
    'state_std_deduction_usd': 4537,

    # This price determines things like your tax burden from RSUs
    # vesting.  It's also the default sales price for any sales orders
    # you place.
    'ipo_price_usd': 12,

    # The query date is necessary to determine how many shares have
    # vested.  I'd recommend setting it to the IPO date.
    'query_date': '9/23/20',

    # If you want to also exercise some shares, you'll need to record
    # that income as it counts towards amti.  This is done in
    # investigator.py where it determines the number of ISOs you can
    # exercise before hitting AMT.
    'iso_exercise_income_usd': 0,

    # pre-tax contributions
    'palantir_401k_usd': 0,
    'palantir_fsa_usd': 0,
    'palantir_drca_usd': 0,

    # Regular income
    'reg_income_usd': 0,

    # If you have any other income that does not count as regular
    # income, but does affect amti (such as any ISOs you've exercised
    # this year), it should be included here.
    'ext_amt_income_usd': 0,

    # Check your paystub and estimate how much has been withheld for
    # taxes by the end of the year.  This one is needed to approximate
    # how much remaining tax burden will exist.
    'fed_withheld_usd': 0,
    'state_withheld_usd': 0,
    }


# Now we create the DAG Model.  We'll use this model for everything else.
MODEL = pylink.DAGModel([deathAnd.Taxes(),
                         myMeager.Income(),
                         anAwkward.Position(GRANTS)],
                        **__constants)
