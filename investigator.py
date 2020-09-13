#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd
import report as explosive
import private


class Investigator(object):
    """Executes a number of queries against the financial model."""

    def __init__(self, model):
        self.m = model
        self.e = model.enum

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
        rate = held / float(vested)
        print("Withholding %d / %d (%.2f)" % (held, vested, rate))

    def question_2(self):
        self._qst(2, "What is the outstanding tax burden?")
        rep = explosive.Report(m)
        rep.print_tax_summary()

    def owed(self):
        m = self.m
        owed = ( 0.0
                 + m.tax_burden_usd
                 - m.fed_withheld_usd
                 - m.state_withheld_usd
                 - m.shares_withheld_rsu_usd
                 + 0.0 )
        return owed

    def question_3(self):
        self._qst(3, "How many RSUs need to be sold to cover tax burden?")
        needed = int(math.ceil(self.owed() / float(m.ipo_price_usd)))
        print("Share Price: %.2f" % m.ipo_price_usd)
        print("Owed:    %s" % explosive.comma(self.owed()))
        pct = int((needed * 100) / m.shares_vested_rsu_n)
        print("Sell:        %d (%d %%)" % (needed, pct))

    def question_4(self):
        self._qst(4, "How much cash if we sell it all (start with NSO)?")
        orders = myMeager.sales_orders_all(self.m)
        self.m.override(self.e.sales_orders, orders)
        rep = explosive.Report(m)
        rep.print_grants()
        cleared = ( 0.0
                    + m.total_income_usd
                    - m.reg_income_usd
                    - self.owed()
                    - m.shares_withheld_rsu_usd
                    + 0.0 )
        print("We Clear: %s"%explosive.comma(cleared))

    def question_5(self):
        self._qst(5, "How much cash if we sell the RSUs?")
        orders = myMeager.sales_orders_rsu(self.m)
        self.m.override(self.e.sales_orders, orders)
        cleared = ( 0.0
                    + m.total_income_usd
                    - m.reg_income_usd
                    - self.owed()
                    - m.shares_withheld_rsu_usd
                    + 0.0 )
        print("We Clear: %s"%explosive.comma(cleared))

    def question_6(self):
        self._qst(6, "If we sell it all, how many ISOs can we buy w/o AMT?")
        orders = myMeager.sales_orders_all(self.m)
        self.m.override(self.e.sales_orders, orders)

        e = m.enum
        dollars = 0
        for i in range(m.shares_vested_iso_n):
            m.override(e.iso_exercise_income_usd, i*m.ipo_price_usd*10)
            if m.amt_taxes_usd > m.fed_reg_income_taxes_usd:
                dollars = i * m.ipo_price_usd*10
                break
        m.override(e.iso_exercise_income_usd, 0)

        # it'll cost dollars to hit amt, how many shares is that?
        strike = m.grants_lst[0].strike_usd
        n = int(dollars / (m.ipo_price_usd - strike))
        cost = n * strike

        cleared = ( 0.0
                    + m.total_income_usd
                    - m.reg_income_usd
                    - self.owed()
                    - m.shares_withheld_rsu_usd
                    + 0.0 )
        remaining = cleared - cost

        print("AMT Income:      %s" % explosive.comma(float(dollars)))
        print("Exercisable shares: %s" % explosive.comma(n)[:-3])
        print("Exercise Cost:   %s" % explosive.comma(float(cost)))
        print("Cash Cleared:    %s" % explosive.comma(float(cleared)))
        print("Cash Remaining:  %s" % explosive.comma(float(remaining)))

    def question_7(self):
        self._qst(7, "If we sell all RSUs, how many ISOs can we buy w/o AMT?")
        orders = myMeager.sales_orders_rsu(self.m)
        self.m.override(self.e.sales_orders, orders)

        e = m.enum
        dollars = 0
        for i in range(m.shares_vested_iso_n):
            m.override(e.iso_exercise_income_usd, i*m.ipo_price_usd*10)
            if m.amt_taxes_usd > m.fed_reg_income_taxes_usd:
                dollars = i * m.ipo_price_usd * 10
                break
        m.override(e.iso_exercise_income_usd, 0)

        # it'll cost dollars to hit amt, how many shares is that?
        strike = m.grants_lst[0].strike_usd
        n = int(dollars / (m.ipo_price_usd - strike))
        cost = n * strike


        cleared = ( 0.0
                    + m.total_income_usd
                    - m.reg_income_usd
                    - self.owed()
                    - m.shares_withheld_rsu_usd
                    + 0.0 )
        remaining = cleared - cost

        print("AMT Income:      %s" % explosive.comma(float(dollars)))
        print("Exercisable shares: %s" % explosive.comma(n)[:-3])
        print("Exercise Cost:   %s" % explosive.comma(float(cost)))
        print("Cash Cleared:    %s" % explosive.comma(float(cleared)))
        print("Cash Remaining:  %s" % explosive.comma(float(remaining)))
        rep = explosive.Report(m)
        rep.print_grants()
        print()

    def go(self):
        self.question_1()
        self.question_2()
        self.question_3()
        self.question_4()
        self.question_5()
        self.question_6()
        self.question_7()

if __name__ == '__main__':
    m = private.MODEL
    dixon_hill = Investigator(m)
    dixon_hill.go()
