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
            'cleared_from_sale_usd': self.cleared_from_sale,
            'shares_sold_nso_n': self.shares_sold_nso_n,
            'shares_sold_iso_n': self.shares_sold_iso_n,
            'shares_sold_rsu_n': self.shares_sold_rsu_n,
            'shares_available_rsu_n': self.shares_available_rsu_n,
            'shares_available_nso_n': self.shares_available_nso_n,
            'shares_available_iso_n': self.shares_available_iso_n,

            # Sales Orders
            'sales_orders': [],
            }

    def shares_available_rsu_n(self, m):
        return (m.shares_vested_unsold_rsu_n
                * (1.0 - m.shares_withheld_rsu_rate))

    def shares_available_nso_n(self, m):
        return (m.shares_vested_unsold_nso_n
                * (1.0 - m.shares_withheld_nso_rate))

    def shares_available_iso_n(self, m):
        return (m.shares_vested_unsold_iso_n
                * (1.0 - m.shares_withheld_iso_rate))

    def sales_simulation(self, m):
        cost = 0.0
        retval = {
            'iso':  0,
            'nso':  0,
            'rsu':  0,
            }

        end = copy.deepcopy(m.grants_dict)

        touched = {}

        # Process withholdings
        for name in end:
            grant = end[name]
            rate = getattr(m, 'shares_withheld_%s_rate' % grant.vehicle)
            grant.withhold(m.query_date, rate)

        # Process the sales orders (in order, allowing for duplicates)
        for order in m.sales_orders:
            g = m.grants_dict[order['id']]
            rate = getattr(m, 'shares_withheld_%s_rate' % g.vehicle)

            copied = end[g.name]
            touched[g.name] = copied

            # Execute the sell order on the copy -- this is where we
            # expect asserts to pop if we've screwed up the numbers.

            tmp = copied.sell(m.query_date,
                              order['qty'],
                              order['price'],
                              rate,
                              prefer_exercise=order['prefer_exercise'],
                              update=True,)

            # Add our copied object to the end-state
            end[copied.name] = copied
            touched[copied.name] = copied

            # Collect the results of the sale
            retval[g.vehicle] += tmp['net_usd']
            cost += tmp['cost']

            g = end[name]
            rate = getattr(m, 'shares_withheld_%s_rate'%g.vehicle)
            if name not in touched:
                # FIXME: Break out withhold vs sell
                # Until then, run a sell order with 0 shares to
                # trigger withholdings so that the ending cap table is
                # properly represented.
                g.sell(m.query_date, 0, 0, rate, update=True)

        retval['cost'] = cost
        retval['end'] = end
        return retval

    def shares_sold_rsu_n(self, m):
        gdict = m.grants_dict
        l = [ o for o in m.sales_orders if gdict[o['id']].vehicle == 'rsu' ]
        return int(sum([o['qty'] for o in l]))

    def shares_sold_iso_n(self, m):
        gdict = m.grants_dict
        l = [ o for o in m.sales_orders if gdict[o['id']].vehicle == 'iso' ]
        return int(sum([o['qty'] for o in l]))

    def shares_sold_nso_n(self, m):
        gdict = m.grants_dict
        l = [ o for o in m.sales_orders if gdict[o['id']].vehicle == 'nso' ]
        return int(sum([o['qty'] for o in l]))

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

    def cleared_from_sale(self, m):
        cleared = ( 0.0
                    + m.total_income_usd
                    - m.reg_income_usd
                    - m.outstanding_taxes_usd
                    + 0.0 )
        return cleared


###############################################################################
# Convenience Functions for Selling Shares                                    #
###############################################################################

def grant_lst_for_vehicle(m, vehicle, cheap_first=True):
    lst = [ g for g in m.grants_lst if g.vehicle == vehicle ]
    if cheap_first:
        lst.sort(key=lambda g: g.strike_usd)
    else:
        lst.sort(key=lambda g: g.strike_usd, reverse=True)
    return lst

def sales_orders_all(*a, **k):
    return sales_orders_rsu(*a,**k) + sales_orders_options(*a,**k)

def sales_orders_options(m,
                         price=None,
                         prefer_exercise=True,
                         cheap_first=True,
                         nso_first=False):
    """Place sell orders for all options possible

    If you don't specify a sales price, it'll automatically use the
    IPO price which is used for RSU withholding computations.

    If you would prefer to liquidate shares that are currently held,
    set prefer_exercise to True.

    If you want to ditch the expensive options first, assert cheap_first

    returns: [<Sales Order>, ...]
    """

    # default to the ipo price
    if price is None: price = m.ipo_price_usd
    assert(0 <= price)

    # Set up the list of sales orders
    option_lst = []
    nso_lst = grant_lst_for_vehicle(m, 'nso', cheap_first=cheap_first)
    iso_lst = grant_lst_for_vehicle(m, 'iso', cheap_first=cheap_first)
    
    if nso_first:
        option_lst = nso_lst + iso_lst
    else:
        option_lst = iso_lst + nso_lst

    retval = []

    # How many shares can be legally sold?
    remaining_restricted = m.shares_sellable_restricted_n

    for g in option_lst:
        rate = getattr(m, 'shares_withheld_%s_rate'%g.vehicle)
        n = g.available(m.query_date, rate)
        n = min(remaining_restricted, n)
        remaining_restricted -= n
        retval.append({
            'id': g.name,
            'qty': n,
            'price': price,
            'prefer_exercise': prefer_exercise
            })

    return retval

def sales_orders_rsu(m, price=None, **ignore):
    retval = []

    # default to the ipo price
    if price is None: price = m.ipo_price_usd
    assert(0 <= price)

    for g in m.grants_lst:
        if g.vehicle == 'rsu':
            n = g.available(m.query_date, m.shares_withheld_rsu_rate)
            retval.append({
                'id': g.name,
                'qty': n,
                'price': price,
                'prefer_exercise': False, # not used
                })

    return retval
