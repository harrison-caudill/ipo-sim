#!/usr/bin/env python

import math
import pylink


def comma(v):
    retval = '%13s' % ('{:,}'.format(round(float(v), 2)))
    if not (10*v % 1):
        retval = retval[1:] + '0'
    return retval


class Report(object):

    def __init__(self, m):
        self.m = m

    def _vs(self, v):
        rate = round(v / float(self.m.total_income_usd), 2)
        return (comma(v), '%5.1f %%' % (rate*100.0))

    def print_tax_summary(self):
        m = self.m
        print("="*60)
        print("Federal Taxes")
        print("="*60)
        print()
        print("Taxable Income: %s" % comma(m.fed_taxable_income_usd))
        print("Reg Taxes:      %s (%s)" % self._vs(m.fed_reg_income_taxes_usd))
        print("SS Taxes:       %s (%s)" % self._vs(m.fed_ss_taxes_usd))
        print("Medicare Taxes: %s (%s)" % self._vs(m.fed_medicare_taxes_usd))
        print("Federal Taxes:  %s (%s)" % self._vs(m.fed_taxes_usd))
        print("Withholdings:   %s (%s)" % self._vs(m.fed_withheld_usd))
        print()
        print("="*60)
        print("State Taxes")
        print("="*60)
        print()
        print("Taxable Income: %s" % comma(m.state_taxable_income_usd))
        print("Reg Taxes:      %s (%s)" % self._vs(m.state_reg_income_taxes_usd))
        print("SDI Taxes:      %s (%s)" % self._vs(m.state_random_taxes_usd))
        print("State Taxes:    %s (%s)" % self._vs(m.state_taxes_usd))
        print("Withholdings:   %s (%s)" % self._vs(m.state_withheld_usd))
        print()
        print("="*60)
        print("Total Taxes")
        print("="*60)
        print()
        print("Total Income:   %s" % comma(m.total_income_usd))
        print("State Taxes:    %s (%s)" % self._vs(m.state_taxes_usd))
        print("Federal Taxes:  %s (%s)" % self._vs(m.fed_taxes_usd))
        print("Total Taxes:    %s (%s)" % self._vs(m.tax_burden_usd))
        owed = ( 0.0
                 + m.tax_burden_usd
                 - m.fed_withheld_usd
                 - m.state_withheld_usd
                 - m.shares_withheld_rsu_usd
                 + 0.0 )
        print("Taxes Owed:     %s" % comma(owed))
        print("This is AFTER regular withholdings and AFTER the automatic RSU withholding")
        print()
        print()


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
                'strike':  start.strike_usd,
                'vested':  comma(start.vested(m.query_date))[:-3],
                'sold':    comma(end.sold - start.sold)[:-3],
                'rem':     comma(end.vested_unsold(m.query_date))[:-3],
                }
            print(row_fmt % kwargs)
        print()

    def print_summary(self):
        pass
