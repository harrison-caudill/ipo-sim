#!/usr/bin/env python

import copy
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
            'rem_grants_lst': self.rem_grants_lst,
            'rem_grants_dict': self.rem_grants_dict,

            # Sales Orders
            'sales_orders': [],
            }

    def sales_simulation(self, m):
        cost = 0.0
        retval = {
            'iso':  0,
            'nso':  0,
            'rsu':  0,
            }

        end = copy.deepcopy(m.grants_dict)

        # make sure we aren't doing anything crazy

        for order in m.sales_orders:
            g = m.grants_dict[order['id']]

            copied = end[g.name]

            # Execute the sell order on the copy -- this is where we
            # expect asserts to pop if we've screwed up the numbers.
            tmp = copied.sell(m.query_date,
                              order['qty'],
                              order['price'],
                              prefer_exercise=order['prefer_exercise'],
                              update=True)

            # Add our copied object to the end-state
            end[copied.name] = copied

            # Collect the results of the sale
            retval[g.vehicle] += tmp['net_usd']
            cost += tmp['cost']

        retval['cost'] = cost
        retval['end'] = end
        return retval

    def rem_grants_lst(self, m):
        d = m.rem_grants_dict
        return [d[g.name] for g in m.grants_lst]

    def rem_grants_dict(self, m):
        return m.sales_simulation_data['end']

    def rsu_income(self, m):
        return m.sales_simulation_data['rsu']

    def iso_sales_income(self, m):
        return m.sales_simulation_data['iso']

    def nso_income(self, m):
        return m.sales_simulation_data['nso']

    def total_income_usd(self, m):
        return ( 0.0
                 + m.reg_income_usd
                 + m.rsu_income_usd
                 + m.nso_income_usd
                 + m.iso_sales_income_usd
                 + 0.0 )


###############################################################################
# Convenience Functions for Selling Shares                                    #
###############################################################################

def sales_orders_all(m, price=None, prefer_exercise=True):
    """Place sell orders for all shares possible

    Start with the RSUs, then the NSOs, then the ISOs.  The options
    will be selected in the order specified in private.py.

    If you don't specify a sales price, it'll automatically use the
    IPO price which is used for RSU withholding computations.

    If you would prefer to liquidate shares that are currently held,
    set prefer_exercise to True.

    returns: [<Sales Order>, ...]
    """

    # default to the ipo price
    if price is None: price = m.ipo_price_usd
    assert(0 <= price)

    # How many shares can be legally sold?
    remaining_restricted = m.shares_sellable_restricted_n

    retval = sales_orders_rsu(m, price=price)

    for g in m.grants_lst:
        if g.vehicle == 'nso':
            n = g.vested_unsold(m.query_date)
            n = min(remaining_restricted, n)
            remaining_restricted -= n
            retval.append({
                'id': g.name,
                'qty': n,
                'price': price,
                'prefer_exercise': prefer_exercise
                })

    for g in m.grants_lst:
        if g.vehicle == 'iso':
            n = g.vested_unsold(m.query_date)
            n = min(remaining_restricted, n)
            remaining_restricted -= n
            retval.append({
                'id': g.name,
                'qty': n,
                'price': price,
                'prefer_exercise': prefer_exercise
                })

    return retval

def sales_orders_rsu(m, price=None):
    retval = []

    # default to the ipo price
    if price is None: price = m.ipo_price_usd
    assert(0 <= price)

    for g in m.grants_lst:
        if g.vehicle == 'rsu':
            n = g.vested_unsold(m.query_date)
            retval.append({
                'id': g.name,
                'qty': n,
                'price': price,
                'prefer_exercise': False, # not used
                })

    return retval
