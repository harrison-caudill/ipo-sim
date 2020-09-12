#!/usr/bin/env python

import math
import pylink

import income as myMeager
import position as anAwkward
import taxes as deathAnd


    def __s(v):
        return '{:,}'.format(round(v, 2))






class Reporter(object):

    def __init__(self, m):
        self.m = m

    def print_grants(self):
        pass

    def print_summary(self):
        pass




 1. What is the minimum/automatic number of withheld RSUs?

 2. What is the remaining RSU tax burden (in dollars)?

 3. How many RSUs must be sold on day 1 to cover the RSU tax burden?

 4. Percentage of RSUs that the answer to question 3 represents?

 5. If we sold everything we could, how much cash would we clear?

 6. If we sold all RSUs, and max number of NSOs, what percentage of
 full exercise price for all ISOs could be achieved without hitting
 AMT? (i.e. assume they're all priced the same)

 7. For a range of FMVs, graph 6



    grants = {}
    for g in GRANTS: grants[g.name] = g

    g = grants['RSU-10436']

    m = model
    e = m.enum

    for name in grants:
        g = grants[name]
        if g.vehicle == 'rsu' or True:
            g.sale_qty = g.outstanding() #g.vested(m.ipo_date)

    moneys = round(m.rsu_income_usd + m.nso_income_usd, 2)

    # temporarily eliminate alternative income streams
    m.override(e.palantir_401k_usd, 0)
    m.override(e.palantir_fsa_usd, 0)
    m.override(e.palantir_drca_usd, 0)
    m.override(e.reg_income_usd, 0)
    m.override(e.fed_withheld, 0)

    fed = m.fed_taxes_usd - m.fed_withheld
    state = round(m.state_taxes_usd, 2)
    taxes = round(fed + state, 2)

    def __s(v):
        return '{:,}'.format(round(v, 2))

    income = m.fed_taxable_income_usd
    def __p(name, v):
        print("=== %s ===" % name)
        print("Income: %s" % (__s(income)))
        print("Taxes:  %s" % (__s(v)))
        rate = round((100.0 * float(v) / float(income)), 2)
        print("Rate:   %s %%" % (rate))
        print("")

    __p("Fed", m.fed_taxes_usd)
    __p("Reg", m.fed_reg_income_taxes_usd)
    __p("AMT", m.amt_taxes_usd)
    __p(" SS", m.fed_ss_taxes_usd)
    __p("Med", m.fed_medicare_taxes_usd)

    # print('Income: %s  USD' % __s(income))

    # print("Price per Share:    $%.2g" % m.ipo_price_usd)
    # print("Pre-Tax Net:        $%s" % '{:,}'.format(moneys))
    # print("Tax Burden:         $%s" % '{:,}'.format(taxes))
    # print("Post-Tax Net:       $%s" % '{:,}'.format(moneys-taxes))
    # print("Effective Tax Rate: %%%.2f" % (100.0*((fed+state)/moneys)))
    # print("Fed Tax Rate:       %%%.2f" % (100.0*((fed)/moneys)))
    # reg_tax = deathAnd.apply_tax_table(m.fed_taxable_income_usd, m.fed_tax_table)
    # print('Income: %s  USD' % __s(income))
    # print('Taxes:   %s USD' % __s(reg_tax))

        
