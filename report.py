#!/usr/bin/env python

import math
import pylink


def comma(v, dec=True, n=13, white=True):
    if dec:
        retval = '%*s' % (n, '{:,}'.format(round(float(v), 2)))
        if not (10*v % 1):
            retval = retval[1:] + '0'
    else:
        retval = '%*s' % (n, '{:,}'.format(int(v)))

    if not white: retval = retval.replace(' ', '')

    return retval

TAX_FMT = """%%T: Rate vs the taxable income
%%A: Rate vs the ACTUAL (in your bank) income

=== State Taxes ===
Taxable Income:     %(state_taxable_income)s $
Actual Income:      %(total_income)s $
Reg Taxes:          %(var_state_reg)s
SDI Taxes:          %(var_state_sdi)s
State Taxes:        %(var_state_tot)s
Cash Withheld:      %(var_state_with)s
RSU Withheld:       %(var_state_rsu_with)s
Outstanding:        %(var_state_out)s

=== Federal Taxes ===
Fed Taxable Income: %(fed_taxable_income)s $
AMT Taxable Income: %(amt_taxable_income)s $
Actual Income:      %(total_income)s $
Reg Taxes:          %(var_fed_reg)s
AMT Taxes:          %(var_fed_amt)s
SS Taxes:           %(var_fed_ss)s
Medicare Taxes:     %(var_fed_med)s
Federal Taxes:      %(var_fed_tot)s
Cash Withheld:      %(var_fed_with)s
RSU Withheld:       %(var_fed_rsu_with)s
Outstanding:        %(var_fed_out)s

=== Overall ===
Actual Income:      %(total_income)s $
State Taxes:        %(var_state_tot)s
Federal Taxes:      %(var_fed_tot)s
Total Taxes:        %(var_tot)s
Outstanding:        %(var_tot_out)s
"""


class Report(object):

    def __init__(self, m):
        self.m = m

    def print_tax_summary(self):
        m = self.m

        args = {}
        
        def __a(name, val, real_only=False):
            ri = round(((100.0 * float(val)) / float(m.total_income_usd)), 1)
            if real_only:
                s = '%s $   ( %5.1f%%A         )' % (comma(val, dec=False), ri)
            else:
                rt = round(((100.0 * float(val)) / float(taxable_income)), 1)
                s = '%s $   ( %5.1f%%A %5.1f%%T )' % (comma(val, dec=False), ri, rt)
            args['var_'+name] = s

        args['total_income'] = comma(m.total_income_usd, dec=False)

        taxable_income = m.state_taxable_income_usd
        args['state_taxable_income'] = comma(m.state_taxable_income_usd, dec=False)
        __a('state_reg', m.state_reg_income_taxes_usd)
        __a('state_sdi', m.state_sdi_taxes_usd)
        __a('state_tot', m.state_taxes_usd)
        __a('state_with', m.state_withheld_usd)
        __a('state_rsu_with', m.shares_withheld_rsu_state_usd)
        __a('state_out', m.state_outstanding_taxes_usd)

        args['fed_taxable_income'] = comma(m.fed_taxable_income_usd, dec=False)
        args['amt_taxable_income'] = comma(m.amt_taxable_income_usd, dec=False)
        taxable_income = m.amt_taxable_income_usd
        __a('fed_amt', m.amt_taxes_usd)
        taxable_income = m.fed_taxable_income_usd
        __a('fed_reg', m.fed_reg_income_taxes_usd)
        __a('fed_ss', m.fed_ss_taxes_usd)
        __a('fed_med', m.fed_medicare_taxes_usd)
        __a('fed_tot', m.fed_taxes_usd)
        __a('fed_with', m.fed_withheld_usd)
        __a('fed_rsu_with', m.shares_withheld_rsu_fed_usd)
        __a('fed_out', m.fed_outstanding_taxes_usd)

        __a('tot', m.tax_burden_usd, real_only=True)
        __a('tot_out', m.outstanding_taxes_usd, real_only=True)

        print(TAX_FMT % args)

    def print_grants(self):
        m = self.m
        print("="*60)
        print("Cap Table")
        print("="*60)

        start_lst = m.grants_lst
        end_lst = m.rem_grants_lst

        print('        ID       Type  Strike        Vested            Sold       Remaining')
        row_fmt = '%(name)15s  %(vehicle)s %(strike)6s %(vested)15s %(sold)15s %(rem)15s'
        for i in range(len(start_lst)):
            start = start_lst[i]
            end = end_lst[i]
            assert(start.name == end.name)
            kwargs = {
                'name':    start.name,
                'vehicle': start.vehicle,
                'strike':  '%5.1f' % start.strike_usd,
                'vested':  comma(start.vested(m.query_date), dec=False),
                'sold':    comma(end.sold - start.sold, dec=False),
                'rem':     comma(end.vested_unsold(m.query_date), dec=False),
                }
            print(row_fmt % kwargs)
        print()
