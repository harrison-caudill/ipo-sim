#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd
import report as explosive
import private

from report import comma

class Investigator(object):
    """Executes a number of queries against the financial model."""

    def __init__(self, model):
        self.m = model
        self.e = model.enum
        self.rep = explosive.Report(model)

    def _qst(self, num, msg):
        print()
        print('/%s/'%('*'*78))
        print('/* %-75s*/'%('Question #%d'%num))
        print('/* %-75s*/'%(msg))
        print('/%s/'%('*'*78))
        print()
        print()

    def question_1(self):
        self._qst(1, "How many RSUs will be automatically withheld?")

        print(
            """These numbers are for shares vesting throughout the
year, since those will affect taxes as well.  Shares
available on the big day will NOT be affected by RSU
withholdings that will happen afterwards.
""")

        held = m.shares_withheld_rsu_n
        vested = m.shares_vested_rsu_eoy_n
        if vested:
            rate = round(100.0 * held / float(vested), 1)
        else:
            rate = -1.0
        print("Withholding:   %s / %s ( %5.1f %% )" % (
            comma(held, dec=False, white=False),
            comma(vested, dec=False, white=False),
            rate))

    def question_2(self):
        self._qst(2, "What is the outstanding tax burden?")
        self.rep.print_tax_summary()
        self.rep.print_grants()

    def question_3(self):
        self._qst(3, "How many RSUs need to be sold to cover tax burden?")
        needed = int(math.ceil(m.outstanding_taxes_usd /
                               float(m.ipo_price_usd)))
        print("Share Price:  $ %.2f" % m.ipo_price_usd)
        print("Owed:         $ %s" % comma(m.outstanding_taxes_usd,
                                          dec=False, white=False))
        if m.shares_vested_rsu_n:
            pct = int((needed * 100) / m.shares_vested_rsu_n)
        else:
            pct = -1
        print("Sell:           %s ( %5.1f %% )" % (
            comma(needed, dec=False, white=False),
            pct))

    def question_4(self):
        self._qst(4, "How much cash if we sell it all (starting with the expensive NSOs)?")
        orders = myMeager.sales_orders_all(self.m,
                                           nso_first=True,
                                           cheap_first=False)

        self.m.override(self.e.sales_orders, orders)
        self.rep.print_grants()
        self.rep.print_tax_summary()
        print()
        print("Share Price:  $ %.2f" % m.ipo_price_usd)
        print("NSOs Sold:      %s" % comma(m.shares_sold_nso_n,
                                           dec=False, white=False))
        print("NSO Income:   $ %s" % comma(m.nso_income_usd,
                                           dec=False, white=False))
        print("ISOs Sold:      %s" % comma(m.shares_sold_iso_n,
                                           dec=False, white=False))
        print("ISO Income:   $ %s" % comma(m.iso_sales_income_usd,
                                           dec=False, white=False))
        print("RSUs Sold:      %s" % comma(m.shares_sold_rsu_n,
                                           dec=False, white=False))
        print("RSU Income:   $ %s" % comma(m.rsu_income_usd,
                                           dec=False, white=False))
        print("Sale Income:  $ %s" % comma(m.rsu_income_usd
                                           + m.nso_income_usd
                                           + m.iso_sales_income_usd,
                                          dec=False, white=False))
        print("Owed:         $ %s" % comma(m.outstanding_taxes_usd,
                                          dec=False, white=False))
        print("We Clear:     $ %s"%comma(m.cleared_from_sale_usd, dec=False, white=False))
        print()
        print("This is AFTER paying all outstanding taxes.")

    def question_5(self):
        self._qst(5, "How much cash if we sell the RSUs?")
        orders = myMeager.sales_orders_rsu(self.m)
        self.m.override(self.e.sales_orders, orders)

        self.rep.print_grants()
        self.rep.print_tax_summary()
        print()

        print("We Clear: %s"%comma(m.cleared_from_sale_usd))

    def amt_free_iso(self, strike=None):
        m = self.m
        e = m.enum
        if strike is None:
            g = [g for g in m.grants_lst if g.vehicle=='iso'][0]
            strike = g.strike_usd

        dollars = 0
        amti_gap = 0
        n_shares = 0

        max_val = m.shares_available_iso_n*(m.ipo_price_usd-strike)
        iso_in = m.solve_for(e.iso_exercise_income_usd,
                             e.amt_taxes_usd, m.fed_reg_income_taxes_usd,
                             0, max_val, max_val/50.0, rounds=3)

        n_shares = int(iso_in / float(strike))
        cost = n_shares * strike

        return (iso_in, n_shares, strike, cost)

    def question_6(self):
        self._qst(6, "If we sell it all, how many ISOs can we buy w/o AMT?")
        orders = myMeager.sales_orders_all(self.m)
        self.m.override(self.e.sales_orders, orders)

        self.rep.print_grants()
        self.rep.print_tax_summary()
        print()

        print("Just using the first ISO strike price we find for starters.")

        cleared = m.cleared_from_sale_usd
        (amt, n, strike, cost) = self.amt_free_iso()
        remaining = cleared - cost

        print("AMT Income Gap:     $ %s" % comma(amt, dec=False, white=False))
        print("Exercisable shares:   %s" % comma(n, dec=False, white=False))
        print("Strike Price:       $ %s" % comma(strike,
                                                 dec=True, white=False))
        print("Exercise Cost:      $ %s" % comma(cost, dec=False, white=False))
        print("Cash Cleared:       $ %s" % comma(cleared,
                                                 dec=False, white=False))
        print("Cash Remaining:     $ %s" % comma(remaining,
                                               dec=False, white=False))

    def question_7(self):
        self._qst(7, "If we sell all RSUs, how many ISOs can we buy w/o AMT?")

        # Place an order for all RSUs
        orders = myMeager.sales_orders_rsu(self.m)
        self.m.override(self.e.sales_orders, orders)

        self.rep.print_grants()
        print()

        print("Just using the first ISO strike price we find for starters.")

        cleared = m.cleared_from_sale_usd
        (amt, n, strike, cost) = self.amt_free_iso()
        remaining = cleared - cost

        m.override(self.e.iso_exercise_income_usd, n*(m.ipo_price_usd-strike))

        self.rep.print_tax_summary()

        print("AMT Income Gap:     $ %s" % comma(amt, dec=False, white=False))
        print("Exercisable shares:   %s" % comma(n, dec=False, white=False))
        print("Strike Price:       $ %s" % comma(strike,
                                                 dec=True, white=False))
        print("Exercise Cost:      $ %s" % comma(cost, dec=False, white=False))
        print("Cash Cleared:       $ %s" % comma(cleared,
                                                 dec=False, white=False))
        print("Cash Remaining:     $ %s" % comma(remaining,
                                               dec=False, white=False))

    def question_8(self):
        self._qst(7, "We sell nothing on day 1, then the price drops.")

        # Place an order for all RSUs
        price = m.ipo_price_usd - 5
        orders = myMeager.sales_orders_rsu(self.m, price)
        self.m.override(self.e.sales_orders, orders)
        print("Sell Price:         $ %s" % comma(price,dec=False,white=False))
        print("Cash Cleared:       $ %s" % comma(m.cleared_from_sale_usd,
                                                 dec=False, white=False))
        print()

        price = m.ipo_price_usd
        orders = myMeager.sales_orders_rsu(self.m, price)
        self.m.override(self.e.sales_orders, orders)
        print("Sell Price:         $ %s" % comma(price,dec=False,white=False))
        print("Cash Cleared:       $ %s" % comma(m.cleared_from_sale_usd,
                                                 dec=False, white=False))
        print()

        price = m.ipo_price_usd + 5
        orders = myMeager.sales_orders_rsu(self.m, price)
        self.m.override(self.e.sales_orders, orders)
        print("Sell Price:         $ %s" % comma(price,dec=False,white=False))
        print("Cash Cleared:       $ %s" % comma(m.cleared_from_sale_usd,
                                                 dec=False, white=False))
        print()


    def go(self):
        self.question_1()
        self.question_2()
        self.question_3()
        self.question_4()
        self.question_5()
        self.question_6()
        self.question_7()
        self.question_8()
        print()

if __name__ == '__main__':
    m = private.MODEL
    dixon_hill = Investigator(m)
    dixon_hill.go()
