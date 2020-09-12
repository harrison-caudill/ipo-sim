#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd
import report as explosive
import private


class Investigator(object):
    """ Question we want to ask:

 1. What is the minimum/automatic number of withheld RSUs?

 2. What is the remaining RSU tax burden (in dollars)?

 3. How many RSUs must be sold on day 1 to cover the RSU tax burden?

 4. If we sold everything we could, how much cash would we clear?

 5. If we sold all RSUs, and max number of NSOs, what percentage of
 full exercise price for all ISOs could be achieved without hitting
 AMT? (i.e. assume they're all priced the same)

 6. For a range of FMVs, graph 6
"""

    def __init__(self, model):
        self.m = model

    def _qst(self, num, msg):
        print()
        print('/%s/'%('*'*78))
        print('/* %-75s*/'%('Question #%d'%num))
        print('/* %-75s*/'%(msg))
        print('/%s/'%('*'*78))
        print()
        print()


    def sell_it_all(self, m):
        """Place sell orders for all shares possible

        Start with the RSUs, then the NSOs, then the ISOs
        """
        remaining_restricted = m.shares_sellable_restricted_n
        orders = {}

        for g in m.grants_lst:
            if g.vehicle == 'rsu':
                n = g.vested(m.query_date) - g.sold
                orders[g.name] = {'qty':n}

        for g in m.grants_lst:
            if g.vehicle == 'nso':
                n = g.vested(m.query_date) - g.sold
                n = min(remaining_restricted,
                        g.vested(m.query_date) - g.sold)
                remaining_restricted -= n
                orders[g.name] = {'qty':n}

        for g in m.grants_lst:
            if g.vehicle == 'iso':
                n = g.vested(m.query_date) - g.sold
                n = min(remaining_restricted,
                        g.vested(m.query_date) - g.sold)
                remaining_restricted -= n
                orders[g.name] = {'qty':n}

        e = m.enum
        m.override(e.sales_orders, orders)

    def sell_rsu(self, m):
        remaining_restricted = m.shares_sellable_restricted_n
        orders = {}
        for g in m.grants_lst:
            if g.vehicle == 'rsu':
                n = g.vested(m.query_date) - g.sold
            else:
                n = 0
            orders[g.name] = {'qty':n}
        e = m.enum
        m.override(e.sales_orders, orders)

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
        self.sell_it_all(m)
        cleared = ( 0.0
                    + m.total_income_usd
                    - m.reg_income_usd
                    - self.owed()
                    - m.shares_withheld_rsu_usd
                    + 0.0 )
        print("We Clear: %s"%explosive.comma(cleared))

    def question_5(self):
        self._qst(5, "How much cash if we sell the RSUs?")
        self.sell_rsu(m)
        cleared = ( 0.0
                    + m.total_income_usd
                    - m.reg_income_usd
                    - self.owed()
                    - m.shares_withheld_rsu_usd
                    + 0.0 )
        print("We Clear: %s"%explosive.comma(cleared))

    def question_6(self):
        self._qst(6, "If we sell it all, how many ISOs can we buy w/o AMT?")
        self.sell_it_all(m)

        e = m.enum
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
        self.sell_rsu(m)

        e = m.enum
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
        print()

    def question_8(self):
        self._qst(8, "What does our remaining position look like?")
        rep = explosive.Report(m)
        rep.print_grants()

    def go(self):
        self.question_1()
        self.question_2()
        self.question_3()
        self.question_4()
        self.question_5()
        self.question_6()
        self.question_7()
        self.question_8()
        
if __name__ == '__main__':
    m = private.MODEL
    dix = Investigator(m)
    dix.go()
