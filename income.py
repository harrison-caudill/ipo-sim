#!/usr/bin/env python

import math
import pylink


class Income(object):

    def __init__(self):

        self.tribute = {
            'income_obj': self,
            'sales_simulation_data': self.sales_simulation,
            'rsu_income_usd': self.rsu_income,
            'nso_income_usd': self.nso_income,
            'iso_sales_income_usd': self.iso_sales_income,
            'total_income_usd': self.total_income_usd,

            # RSU complexity
            'rsu_fed_hold_rate': 0.22,
            'rsu_state_hold_rate': 0.1023,
            'shares_withheld_rsu_n': self.rsu_withheld,
            'shares_withheld_rsu_usd': self.rsu_withheld_usd,

            # Sales Orders
            'sales_orders': {},
            }

    def sales_simulation(self, m):
        retval = {
            'cost': 0.0,
            'iso':  0.0,
            'nso':  0.0,
            'rsu':  0.0,
            }
        for g_id in m.sales_orders:
            order = m.sales_orders[g_id]
            g = m.grants_dict[g_id]
            tmp = g.sell(m.query_date,
                         order['qty'],
                         m.ipo_price_usd,
                         prefer_exercise=False,
                         update=False)
            retval[g.vehicle] += tmp['net_usd']
            retval['cost'] += tmp['cost']
        return retval

    def rsu_income(self, m):
        return m.sales_simulation_data['rsu']

    def iso_sales_income(self, m):
        return m.sales_simulation_data['iso']

    def nso_income(self, m):
        return m.sales_simulation_data['nso']

    def rsu_withheld(self, m):
        # FIXME: Assumes you have exceeded thresholds for the other
        #        random things (ss, sdi, foo, bar)
        mtab = m.medicare_tax_table
        med_val = max([mtab[k] for k in mtab.keys()])
        rate = ( 0.0
                 + m.rsu_fed_hold_rate
                 + m.rsu_state_hold_rate
                 + med_val
                 + 0.0 )
        return int(math.ceil(m.shares_vested_rsu_n * rate))

    def rsu_withheld_usd(self, m):
        return m.shares_withheld_rsu_n * m.ipo_price_usd

    def total_income_usd(self, m):
        return ( 0.0
                 + m.reg_income_usd
                 + m.rsu_income_usd
                 + m.nso_income_usd
                 + m.iso_sales_income_usd
                 + 0.0 )
        
