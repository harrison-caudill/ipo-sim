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
        held = m.shares_withheld_rsu_n
        vested = m.shares_vested_rsu_n
        rate = round(100.0 * held / float(vested), 1)
        print("Withholding:   %s / %s ( %5.1f %% )" % (
            comma(held, dec=False, white=False),
            comma(vested, dec=False, white=False),
            rate))

    def question_2(self):
        self._qst(2, "What is the outstanding tax burden?")
        self.rep.print_tax_summary()

    def question_3(self):
        self._qst(3, "How many RSUs need to be sold to cover tax burden?")
        needed = int(math.ceil(m.outstanding_taxes_usd /
                               float(m.ipo_price_usd)))
        print("Share Price:  $ %.2f" % m.ipo_price_usd)
        print("Owed:         $ %s" % comma(m.outstanding_taxes_usd,
                                          dec=False, white=False))
        pct = int((needed * 100) / m.shares_vested_rsu_n)
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
        print("We Clear:  $ %s"%comma(m.cleared_from_sale_usd, dec=False, white=False))

    def question_5(self):
        self._qst(5, "How much cash if we sell the RSUs?")
        orders = myMeager.sales_orders_rsu(self.m)
        self.m.override(self.e.sales_orders, orders)

        self.rep.print_grants()

        print("We Clear: %s"%comma(m.cleared_from_sale_usd))

    def amt_free_iso(self, strike=None):
        if strike is None:
            g = [g for g in m.grants_lst if g.vehicle=='iso'][0]
            strike = g.strike_usd

        dollars = 0
        for i in range(m.shares_vested_iso_n):
            m.override(self.e.iso_exercise_income_usd, i*m.ipo_price_usd*10)
            if m.amt_taxes_usd > m.fed_reg_income_taxes_usd:
                dollars = i * m.ipo_price_usd*10
                break
        m.override(self.e.iso_exercise_income_usd, 0)

        # it'll cost dollars to hit amt, how many shares is that?
        n = int(dollars / (m.ipo_price_usd - strike))
        cost = n * strike

        return (dollars, n, strike, cost)

    def question_6(self):
        self._qst(6, "If we sell it all, how many ISOs can we buy w/o AMT?")
        orders = myMeager.sales_orders_all(self.m)
        self.m.override(self.e.sales_orders, orders)

        self.rep.print_grants()

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

    def go(self):
        self.question_1()
        self.question_2()
        self.question_3()
        self.question_4()
        self.question_5()
        self.question_6()
        self.question_7()
        print()

if __name__ == '__main__':
    m = private.MODEL
    dixon_hill = Investigator(m)
    dixon_hill.go()
