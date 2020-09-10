#!/usr/bin/env python

import math
import pylink


class Income(object):

    def __init__(self):

        self.tribute = {
            'sales_simulation_data': self.sales_simulation,
            'rsu_income_usd': self.rsu_income,
            'nso_income_usd': self.nso_income,
            'iso_sales_income_usd': self.iso_sales_income,
            'iso_exercise_income_usd': 0,
            }

    def sales_simulation(self, m):
        retval = {
            'cost': 0.0,
            'iso':  0.0,
            'nso':  0.0,
            'rsu':  0.0,
            }
        for g in m.grants_lst:
            tmp = g.sell(m.ipo_date,
                         g.sale_qty,
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
