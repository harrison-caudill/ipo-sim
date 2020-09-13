#!/usr/bin/env python

import functools
import math
import pylink
import calendar

import datetime

VEHICLES = ['iso', 'nso', 'rsu']


def parse_date(d):
    if str == type(d):
        return datetime.datetime.strptime(d, '%m/%d/%y')
    else:
        return d


def mon_diff(start, end):
    retval = 12*(end.year - start.year) + (end.month - start.month)
    if start.day > end.day: retval -= 1
    retval = max(retval, 0)
    return retval


def from_table(name,
               vehicle,
               first_date, first_val,
               second_date, second_val,
               last_date, last_val,
               n_shares,
               exercised=0,
               sold=0,
               strike_usd=0):
    """Generate a Grant object from rows in Sharepoint.

    name:       Grant ID from sharepoint
    vehicle:    one of 'iso', 'nso', or 'rsu'
    first_*:    The date (mm/dd/yy) and shares vested from the first row in SP
    second_*:   Ditto, but second row
    last_*:     Ditto, but last row
    n_shares:   Total number of shares
    exercised:  Number that have been exercised already
    sold:       Number that have been sold already
    strike_usd: Strike price in USD (zero OK for rsu)
    """

    first_date = parse_date(first_date)
    second_date = parse_date(second_date)
    last_date = parse_date(last_date)

    last_mon_day = calendar.monthrange(first_date.year, first_date.month)
    use_last_day = (last_mon_day == first_date.day)

    # number of months as measured by a banker
    full_months = mon_diff(first_date, last_date)
    period_months = mon_diff(first_date, second_date)

    n_periods = full_months / float(period_months)
    assert(not (n_periods % 1))

    n_cliff = first_val
    negative_cliff = (last_val < (second_val-1))

    return Grant(name=name,
                 vehicle=vehicle,
                 n_cliff=n_cliff,
                 n_shares=n_shares,
                 exercised=exercised,
                 strike_usd=strike_usd,
                 sold=sold,
                 start=first_date,
                 n_periods=n_periods,
                 period_months=period_months,
                 negative_cliff=negative_cliff)


class Grant(object):
    """Equity grants.

The following counts are available:
 * unvested (implicitly outstanding)
 * vested outstanding (iso/nso only)
 * exercised          (iso/nso only)
 * sold
 * held (fully owned share of stock)
"""

    def __init__(self,
                 name=None,
                 vehicle=None,
                 n_cliff=0,
                 n_shares=None,
                 exercised=0,
                 sold=0,
                 strike_usd=0,
                 start=None,
                 n_periods=48,
                 period_months=1,
                 negative_cliff=False):
        """Grant object, including requested actions.

        name:           the grant-id from palantir
        vehicle:        nso, iso, or rsu
        n_shares:       total number of shares
        n_cliff:        number of shares vested at cliff date
        exercised:      number of shares that were exercised (iso/nso only)
        sold:           number of shares that were sold
        strike_usd:     strike price of the grant (iso/nso only)
        start:          beginning date of regular vesting (mm/dd/yy)
        n_periods:      number of vesting periods
        period_months:  number of months in a vesting period
        negative_cliff: subtract the cliff amount from the last vest period
        """

        self.name = name
        assert (name)

        assert(vehicle in ['rsu', 'iso', 'nso'])
        self.vehicle = vehicle

        self.n_shares = n_shares
        assert (n_shares)

        self.n_cliff = n_cliff

        self.exercised = exercised
        assert ((exercised is not None) or ('rsu' == vehicle))

        self.sold = sold

        self.strike_usd = strike_usd
        assert (strike_usd or ('rsu' == vehicle))

        self.start = parse_date(start)
        self.n_periods = n_periods
        self.period_months = period_months

        self.negative_cliff = negative_cliff

        # This works properly with None's
        assert(exercised is None or exercised <= n_shares)
        assert(exercised is None or sold <= exercised)

    def unvested(self, on):
        return self.n_shares - self.vested(on)

    def vested(self, on):
        on = parse_date(on)

        if on < self.start:
            # Asking for a date before vesting began
            return 0

        # number of months as measured by a banker
        mon = mon_diff(self.start, on)

        # how many vesting periods will have been completed at this time?
        periods = int(min(float((math.floor(mon / self.period_months))),
                          self.n_periods))

        # Calculate the number of shares per vesting period
        n_vesting = self.n_shares - self.n_cliff
        if self.negative_cliff: n_vesting += self.n_cliff
        n_shares = int(math.floor(n_vesting / float(self.n_periods)))

        # Add that many shares each vesting period
        if periods >= self.n_periods:
            retval = self.n_shares
        else:
            retval = periods * n_shares + self.n_cliff

        # quick sanity check
        assert(retval >= self.exercised)

        return retval

    def vested_outstanding(self, on):
        return self.vested(on) - self.exercised

    def outstanding(self):
        return self.n_shares - self.exercised

    def held(self):
        return self.exercised - self.sold

    def outstanding_cost(self):
        return self.outstanding() * self.strike_usd

    def vested_outstanding_cost(self, on):
        outstanding = self.vested_outstanding(on)
        assert(self.strike_usd >= 0)
        assert(outstanding >= 0)
        return outstanding * self.strike_usd

    def vested_unsold(self, on):
        return self.vested(on) - self.sold

    def sell(self, on, n, fmv_usd, prefer_exercise=True, update=False):
        """Provides the info about a sell at a given FMV.

        on:      date at which the sale happens (so we can check the vesting)
        n:       number of shares to sell
        fmv_usd: sale price (fair market value)

        If you would like to exercise/sell instead of selling held
        stock, then you can set prefer_exercise to True (default).  If
        you'd prefer to sell any held stock first, set to logic low.
        """

        vested = self.vested(on)
        outstanding = self.vested_outstanding(on)
        held = self.held()
        available = held + vested

        assert(available >= n)

        sell_held = 0
        sell_outstanding = 0
        if prefer_exercise:
            sell_outstanding = min(n, outstanding)
            sell_held = n - sell_outstanding
        else:
            sell_held = min(n, held)
            sell_outstanding = n - sell_held

        if update:
            self.sold += n
            self.exercised += sell_outstanding

        cost = sell_outstanding * self.strike_usd
        gross = n * fmv_usd
        net = gross - cost
        return {
            'cost':      cost,
            'gross_usd': gross,
            'net_usd':   net,
            }


class Position(object):

    def __init__(self, grants):
        self.grants = grants

        gdict = {}
        for g in grants: gdict[g.name] = g

        self.tribute = {
            'position_obj': self,
            'grants_lst': grants,
            'grants_dict': gdict,
            'max_sellable_restricted_frac': 0.2,

            'shares_sellable_n': self.shares_sellable,
            'shares_sellable_restricted_n': self.shares_sellable_restricted,
            }

        self._add_summation_nodes('shares_total%s_n',
                                  'n_shares')

        self._add_summation_nodes('shares_sold%s_n',
                                  'sold')

        self._add_summation_nodes('shares_exercised%s_n',
                                  'exercised')

        self._add_summation_nodes('shares_vested%s_n',
                                  'vested',
                                  *['query_date'])

        self._add_summation_nodes('shares_unvested%s_n',
                                  'unvested',
                                  *['query_date'])

        self._add_summation_nodes('shares_vested_unsold%s_n',
                                  'vested_unsold',
                                  *['query_date'])

        self._add_summation_nodes('shares_vested_outstanding%s_n',
                                  'vested_outstanding',
                                  *['query_date'])

        self._add_summation_nodes('shares_outstanding%s_n',
                                  'outstanding',
                                  call=True)

        self._add_summation_nodes('shares_held%s_n',
                                  'held',
                                  call=True)

        self._add_summation_nodes('exercise_cost_outstanding%s_usd',
                                  'outstanding_cost',
                                  call=True)

        self._add_summation_nodes('exercise_cost_vested_outstanding%s_usd',
                                  'vested_outstanding_cost',
                                  *['query_date'])

        self._add_summation_nodes('rem_shares_total%s_n',
                                  'n_shares',
                                  rem=True)

        self._add_summation_nodes('rem_shares_sold%s_n',
                                  'sold',
                                  rem=True)

        self._add_summation_nodes('rem_shares_exercised%s_n',
                                  'exercised',
                                  rem=True)

        self._add_summation_nodes('rem_shares_vested%s_n',
                                  'vested',
                                  *['query_date'],
                                  rem=True)

        self._add_summation_nodes('rem_shares_unvested%s_n',
                                  'unvested',
                                  *['query_date'],
                                  rem=True)

        self._add_summation_nodes('rem_shares_vested_unsold%s_n',
                                  'vested_unsold',
                                  *['query_date'],
                                  rem=True)

        self._add_summation_nodes('rem_shares_vested_outstanding%s_n',
                                  'vested_outstanding',
                                  *['query_date'],
                                  rem=True)

        self._add_summation_nodes('rem_shares_outstanding%s_n',
                                  'outstanding',
                                  call=True,
                                  rem=True)

        self._add_summation_nodes('rem_shares_held%s_n',
                                  'held',
                                  call=True,
                                  rem=True)

        self._add_summation_nodes('rem_exercise_cost_outstanding%s_usd',
                                  'outstanding_cost',
                                  call=True,
                                  rem=True)

        self._add_summation_nodes('rem_exercise_cost_vested_outstanding%s_usd',
                                  'vested_outstanding_cost',
                                  *['query_date'],
                                  rem=True)

    def _add_summation_nodes(self, fmt, field, *args, call=False, rem=False):
        """Generate summation nodes for counting types of stock.

        OK, this method is complicated.  Because of python's
        late-bindings, and the need to generate and register callable
        objects, we use functools to create a curried outer function
        which returns the callable object we actually want to register.

        The fmt is the name of the node with a single %s which will be
        given the vehicle

        field is the attribute to reference in the grant object, which
        can be callable (as indicated either with the call kwarg, or
        by including a non-zero number of *args).

        Since most of these will need to be duplicated for reviewing
        the equity position after the sales are processed, we include
        a convenience boolean for prepending 'rem_' and referencing
        the post-sale list of grant objects.
        """
        if len(args): call=True

        # ohhh late bindings...
        for typ in VEHICLES:
            def __outer(typ):
                def __inner(m):
                    if call:
                        cargs = [getattr(m, node) for node in args]
                        f = lambda g: getattr(g, field)(*cargs) if g.vehicle == typ else 0
                    else:
                        f = lambda g: getattr(g, field) if g.vehicle == typ else 0
                    lst = m.rem_grants_lst if rem else m.grants_lst
                    return sum(list(map(f, lst)))
                return __inner
            f = functools.partial(__outer, typ)()
            self.tribute[fmt % ('_%s'%typ)] = f

        # let's not forget the summation
        def __tmp(m):
            return sum([ getattr(m, fmt % ('_%s'%typ)) for typ in VEHICLES ])
        self.tribute[fmt % ('')] = __tmp

    def shares_sellable(self, m):
        return (0
                + m.shares_sellable_restricted_n
                + m.total_rsu_n
                + 0 )

    def shares_sellable_restricted(self, m):
        n_unsold = ( 0
                     + (m.shares_total_iso_n - m.shares_sold_iso_n)
                     + (m.shares_total_nso_n - m.shares_sold_nso_n)
                     + 0 )
        max_shares = int(math.floor(n_unsold * m.max_sellable_restricted_frac))

        available = ( 0
                      + m.shares_vested_outstanding_iso_n
                      + m.shares_vested_outstanding_nso_n
                      + 0 )

        return min(available, max_shares)
