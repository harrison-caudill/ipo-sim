#!/usr/bin/env python

import math
import pylink
import matplotlib.pyplot as plt
import os
import pprint

import income as myMeager
import position as anAwkward
import taxes as deathAnd
import report as explosive
import private

if float(pylink.__version__) < 0.9:
    s = """
===============================================================================
===                            WARNING                                      ===
===============================================================================

TL;DR

If you aren't the type to write python code, you'll be fine, but we'd
still prefer you upgrade by running the following command:

pip install -U pylink-satcom



The full story:

Your version of pylink has a bug that includes a workaround.  We
recommend upgrading to the latest version (0.9) by issuing the
following command:

pip install -U pylink-satcom

The bug pertains to initialization of the system before using the
solve_for method in the DAGModel.  Bug 47 was fixed in pull request
48, and is reflected in version 0.9 of pylink.

if (!willing_to_upgrade && want_to_c0d3)
{
/*
 * WORKAROUND and DESCRIPTION
 *
 * Follow the example provided in amt_free_iso where we override the
 * thing we're solving for to be the lowest value in the search range
 * (really just any value in the search range).  Otherwise, what can
 * happen in versions before 0.9 is that you can accidentally leave
 * that value close to the correct value, but outside the search
 * range, then when you run the search, it computes the initial
 * best-position as being the uninitialized value it starts with
 * (i.e. whatever you had it set to before running solve_for).  If the
 * value you have it initially set to is closer to the right number
 * than any other position within the search range then it will
 * improperly attribute that diff to the first value in the search
 * range and return the wrong thing.
 */
}

"""
    print(s)
    input('Press <enter> to continue.')

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


        ### BUG IN PYLINK ###
        # https://github.com/harrison-caudill/pylink/issues/47
        m.override(e.iso_exercise_income_usd, 0)
        ### BUG IN PYLINK ###

        iso_in = m.solve_for(e.iso_exercise_income_usd,
                             e.amt_taxes_usd, m.fed_reg_income_taxes_usd,
                             0, max_val, max_val/10.0, rounds=5)

        n_shares = iso_in / float(strike)
        n_shares = int(min(n_shares, m.shares_vested_outstanding_iso_n))

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

        orig = m.iso_exercise_income_usd

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

        m.override(self.e.iso_exercise_income_usd, orig)

    def question_8(self, rsu_only=False):
        augment = "RSU + NSO"
        if rsu_only: augment = "RSU Only"
        self._qst(8, "Basic financials vs share price (%s)" % augment)

        m = self.m
        e = m.enum

        # Set up the loop
        lo = 5.0  # low fmv
        hi = 25.0 # high fmv
        up = 100
        orig = m.ipo_price_usd

        x =       []
        y_gross = []
        y_net =   []
        y_tax =   []
        y_amti =  []

        amt_exemption_rolloff = -1
        amt_exemption_gone = -1

        for i in range(up+1):
            fmv = (i*(hi-lo)/up)+lo
            x.append(fmv)

            m.override(e.ipo_price_usd, fmv)
            orders = myMeager.sales_orders_all(m,
                                               nso_first=True,
                                               cheap_first=False,
                                               prefer_exercise=True,
                                               restricted=True,
                                               price=fmv)
            if rsu_only:
                orders = myMeager.sales_orders_rsu(self.m, price=fmv)
            self.m.override(self.e.sales_orders, orders)

            if (0 > amt_exemption_rolloff
                and m.amt_base_income_usd > m.amt_exemption_rolloff_threshhold_usd):
                amt_exemption_rolloff = fmv

            if (0 > amt_exemption_gone
                and m.amt_exemption_usd == 0):
                amt_exemption_gone = fmv

                m.override(e.iso_exercise_income_usd, 0)
                m.override(e.ext_amt_income_usd, 0)

            y_gross.append(m.total_income_usd-m.reg_income_usd)
            y_tax.append(m.outstanding_taxes_usd)
            y_amti.append(m.amt_taxable_income_usd)
            y_net.append(m.cleared_from_sale_usd)

        # Reset our state
        m.override(e.ipo_price_usd, orig)

        # Let's make our plots
        fig, ax = plt.subplots()
        ax.set_ylabel('Value (USD)')

        ax.plot(x, y_gross, label='Gross Sales Income (post Withholding)')
        ax.plot(x, y_tax, label='Outstanding Tax Bill')
        ax.plot(x, y_amti, label='AMTI')
        ax.plot(x, y_net, label='Net Income from Sale')

        if 0 < amt_exemption_rolloff:
            ax.axvline(amt_exemption_rolloff)
            ax.text(amt_exemption_rolloff,
                    m.amt_exemption_rolloff_threshhold_usd*1.1,
                    'AMT Rolloff',
                    rotation=45)

        if 0 < amt_exemption_gone:
            ax.axvline(amt_exemption_gone)
            ax.text(amt_exemption_gone,
                    m.amt_exemption_rolloff_threshhold_usd*1.1,
                    'AMT Exemp. Gone',
                    rotation=45)

        ax.grid()
        fig.suptitle('Financials vs FMV (%s)'%augment)
        ax.legend()

        fname = 'fin_all.png'
        if rsu_only: fname = 'fin_rsu.png'
        path = os.path.join('.', fname)
        fig.savefig(path, transparent=False, dpi=600)

    def question_9(self):
        self._qst(9, "What does exercisable ISOs look like vs IPO price?")

        m = self.m
        e = m.enum

        # Set up the loop
        lo = 12.0  # low fmv
        hi = 15.0 # high fmv
        up = 100
        orig = m.ipo_price_usd
        x = []
        y_iso_n = []
        y_gross = []
        y_tax = []
        y_cleared = []
        y_ex_cost = []
        y_rem = []
        y_test = []
        y_amt_diff = []
        m.override(self.e.query_date, '3/15/21')
        #m.override(self.e.query_date, '12/31/35')

        # triggers for vertical lines
        amt_exemption_rolloff = -1
        amt_exemption_gone = -1
        iso_saturated = -1
        rolloff_val = -1
        gone_val = -1

        for i in range(up):
            fmv = (i*(hi-lo)/up)+lo
            x.append(fmv)

            m.override(e.ipo_price_usd, fmv)
            orders_all = myMeager.sales_orders_all(m,
                                                   nso_first=True,
                                                   cheap_first=False,
                                                   prefer_exercise=True,
                                                   restricted=False,
                                                   price=fmv)
            orders_opts = myMeager.sales_orders_options(m,
                                                        nso_first=True,
                                                        cheap_first=False,
                                                        prefer_exercise=True,
                                                        restricted=False,
                                                        price=fmv)
            orders_rsu = myMeager.sales_orders_rsu(m,price=fmv)
            self.m.override(self.e.sales_orders, orders_all)

            (amt, iso, strike, cost) = self.amt_free_iso()

            if (0 > amt_exemption_rolloff
                and m.amt_base_income_usd > m.amt_exemption_rolloff_threshhold_usd-10*m.ipo_price_usd
                and m.amt_base_income_usd < m.amt_exemption_rolloff_threshhold_usd+10*m.ipo_price_usd):
                amt_exemption_rolloff = fmv
                rolloff_val = iso

            if (0 > amt_exemption_gone
                and 0 < amt_exemption_rolloff
                and m.amt_exemption_usd == 0):
                amt_exemption_gone = fmv
                gone_val = iso

            if ((0 > iso_saturated)
                and (iso >= m.shares_vested_outstanding_iso_n)):
                iso_saturated = fmv

            m.override(self.e.iso_exercise_income_usd, amt)

            a = m.fed_reg_income_taxes_usd
            b = m.amt_taxes_usd

            y_iso_n.append(iso)
            cleared = m.cleared_from_sale_usd

            y_gross.append(m.total_income_usd)
            # y_tax.append(m.outstanding_taxes_usd)
            y_cleared.append(cleared)
            y_ex_cost.append(cost)
            # y_rem.append(cleared - cost)
            
        m.override(e.ipo_price_usd, orig)

        # Let's make our plots
        fig, ax_shares = plt.subplots()
        ax_shares.set_xlabel('Share Price (USD)')

        ax_shares.set_ylabel('ISOs (n)')
        ax_shares.plot(x, y_iso_n,
                       label='AMT Free ISO Exercises',
                       color='tab:purple')

        color = 'tab:green'
        ax_dollars = ax_shares.twinx()
        ax_dollars.set_ylabel('Value ($k)')

        y_cleared = [x/1000 for x in y_cleared]
        y_gross = [x/1000 for x in y_gross]
        y_ex_cost = [x/1000 for x in y_ex_cost]
        y_rem = [x/1000 for x in y_rem]
        ax_dollars.set_ylim(0, y_gross[-1]*1.1)

        ax_dollars.plot(x, y_gross, label='Pre-Tax Income')
        ax_dollars.plot(x, y_cleared, label='Post-Tax Cash from Sale')
        # ax_dollars.plot(x, y_tax, label='Taxes Owed')
        # ax_dollars.plot(x, y_cleared, label='Post-Tax Income')
        #ax_dollars.plot(x, y_ex_cost, label='Cost to Exercise')
        # ax_dollars.plot(x, y_rem, label='Remaining')

        if 0 < amt_exemption_rolloff:
            ax_shares.axvline(amt_exemption_rolloff)
            ax_shares.text(amt_exemption_rolloff,
                           rolloff_val*1.05,
                           'AMT Rolloff',
                           rotation=45)

        if 0 < amt_exemption_gone:
            ax_shares.axvline(amt_exemption_gone)
            ax_shares.text(amt_exemption_gone,
                           gone_val*.95,
                           'AMT Exemp. Gone',
                           rotation=45)

        if 0 < iso_saturated:
            ax_shares.axvline(iso_saturated)
            ax_shares.text(iso_saturated,
                           m.shares_vested_outstanding_iso_n*.95,
                           "All ISO's Available",
                           rotation=0)

        fig.suptitle('ISO Outlook vs FMV')
        ax_shares.legend(loc=3)
        ax_dollars.legend()

        fname = 'iso.png'
        path = os.path.join('.', fname)
        fig.savefig(path, transparent=False, dpi=600)

    def go(self):
        self.question_1()
        self.question_2()
        self.question_3()
        self.question_4()
        self.question_5()
        self.question_6()
        self.question_7()
        self.question_8()
        self.question_8(rsu_only=True)
        self.question_9()
        print()

if __name__ == '__main__':
    m = private.MODEL
    dixon_hill = Investigator(m)
    dixon_hill.go()
