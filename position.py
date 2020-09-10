#!/usr/bin/env python

import math
import pylink

import datetime

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
                 n=None,
                 exercised=0,
                 sold=0,
                 strike_usd=0,
                 start=None,
                 n_periods=48,
                 period_months=1,
                 sale_qty=0,
                 negative_cliff=False):
        """Grant object, including requested actions.

        name:           the grant-id from palantir
        vehicle:        nso, iso, or rsu
        n:              total number of shares
        n_cliff:        number of shares vested at cliff date
        exercised:      number of shares that were exercised (iso/nso only)
        sold:           number of shares that were sold
        strike_usd:     strike price of the grant (iso/nso only)
        start:          beginning date of regular vesting (mm/dd/yy)
        n_periods:      number of vesting periods
        period_months:  number of months in a vesting period
        sale_qty:       the number of shares to sell
        negative_cliff: subtract the cliff amount from the last vest period
        """

        self.name = name
        assert (name)

        assert(vehicle in ['rsu', 'iso', 'nso'])
        self.vehicle = vehicle

        self.n = n
        assert (n)

        self.n_cliff = n_cliff

        self.exercised = exercised
        assert ((exercised is not None) or ('rsu' == vehicle))

        self.sold = sold

        self.strike_usd = strike_usd
        assert (strike_usd or ('rsu' == vehicle))

        self.start = self._parse_date(start)
        self.n_periods = n_periods
        self.period_months = period_months

        # So you can register individual actions with individual
        # grants
        self.sale_qty = sale_qty
        assert (sale_qty <= (n - sold))

        self.negative_cliff = negative_cliff

        # This works properly with None's
        assert(exercised is None or exercised <= n)
        assert(exercised is None or sold <= exercised)

    def unvested(self, on):
        return self.n - self.vested(on)

    def vested(self, on):
        on = self._parse_date(on)

        if on < self.start:
            # Asking for a date before vesting began
            return 0

        # number of months as measured by a banker
        mon = ( 0
                + 12*(on.year - self.start.year)
                + (on.month - self.start.month)
                + 0 )
        if self.start.day > on.day: mon -= 1
        mon = max(mon, 0)

        # how many vesting periods will have been completed at this time?
        periods = int(min(float((math.floor(mon / self.period_months))),
                          self.n_periods))

        # Calculate the number of shares per vesting period
        n_vesting = self.n - self.n_cliff
        if self.negative_cliff: n_vesting += self.n_cliff
        n_shares = int(math.floor(n_vesting / float(self.n_periods)))

        # Add that many shares each vesting period
        if periods >= self.n_periods:
            retval = self.n
        else:
            retval = periods * n_shares + self.n_cliff

        # quick sanity check
        assert(retval >= self.exercised)

        return retval

    def vested_outstanding(self, on):
        return self.vested(on) - self.exercised

    def outstanding(self):
        return self.n - self.exercised

    def held(self):
        return self.exercised - self.sold

    def _parse_date(self, d):
        if str == type(d):
            return datetime.datetime.strptime(d, '%m/%d/%y')
        else:
            return d

    def outstanding_cost(self):
        return self.outstanding() * self.strike_usd

    def vested_outstanding_cost(self, on):
        outstanding = self.vested_outstanding(on)
        assert(self.strike_usd >= 0)
        assert(outstanding >= 0)
        return outstanding * self.strike_usd

    def sell(self, on, n, fmv_usd, prefer_exercise=True, update=False):
        """Provides the info about a sell at a given FMV.

        on:      date at which the sale happens (so we can check the vesting)
        n:       number of shares to sell
        fmv_usd: sale price (fair market value)

        If you would like to exercise/sell instead of selling held
        stock, then you can set prefer_exercise to True (default).  If
        you'd prefer to sell any held stock first, set to logic low.

        WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING

        WARNING      You MUST run model.clear_cache() if update=True    WARNING

        WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING
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

        self.tribute = {
            'position_obj': self,
            'grants_lst': grants,
            'max_sellable_restricted_frac': 0.2,

            'shares_total_n': self.shares_total,
            'shares_sellable_n': self.shares_sellable,
            'shares_sellable_restricted_n': self.shares_sellable_restricted,
            'shares_vested_n': self.shares_vested,
            'shares_vested_nso_n': self.shares_vested_nso,
            'shares_outstanding_n': self.shares_outstanding,
            'shares_vested_outstanding_n': self.shares_vested_outstanding,
            'shares_vested_outstanding_nso_n': self.shares_vested_outstanding_nso,
            'shares_vested_outstanding_rsu_n': self.shares_vested_outstanding_rsu,
            'shares_unvested_n': self.shares_unvested,
            'shares_held_n': self.shares_held,
            'vested_outstanding_exercise_cost_usd': self.vested_outstanding_exercise_cost,
            'outstanding_exercise_cost_usd': self.outstanding_exercise_cost,
            'total_rsu_n': self.total_rsu,
            'total_iso_n': self.total_iso,
            'total_nso_n': self.total_nso,
            }

    def shares_total(self, m):
        return sum(list(map(lambda g: g.n, m.grants_lst)))

    def shares_sellable(self, m):
        return (0
                + m.shares_sellable_restricted_n
                + m.total_rsu_n
                + 0 )

    def shares_sellable_restricted(self, m):
        return math.floor((m.total_iso_n + m.total_nso_n)
                          * m.max_sellable_restricted_frac)

    def shares_unvested(self, m):
        return sum(list(map(lambda g: g.unvested(m.query_date), m.grants_lst)))

    def shares_vested(self, m):
        return sum(list(map(lambda g: g.vested(m.query_date), m.grants_lst)))

    def shares_vested_nso(self, m):
        f = lambda g: g.vested(m.query_date) if g.vehicle == 'nso' else 0
        return sum(list(map(f, m.grants_lst)))

    def shares_vested_outstanding_nso(self, m):
        f = lambda g: g.vested_outstanding(m.query_date) if g.vehicle == 'nso' else 0
        return sum(list(map(f, m.grants_lst)))

    def shares_vested_outstanding_rsu(self, m):
        f = lambda g: g.vested_outstanding(m.query_date) if g.vehicle == 'rsu' else 0
        return sum(list(map(f, m.grants_lst)))

    def shares_vested_outstanding(self, m):
        return sum(list(map(lambda g: g.vested_outstanding(m.query_date),
                            m.grants_lst)))

    def shares_outstanding(self, m):
        return sum(list(map(lambda g: g.outstanding(m.query_date),
                            m.grants_lst)))

    def shares_exercised(self, m):
        return sum(list(map(lambda g: g.exercised, m.grants_lst)))

    def shares_sold(self, m):
        return sum(list(map(lambda g: g.sold, m.grants_lst)))

    def shares_held(self, m):
        return sum(list(map(lambda g: g.held(), m.grants_lst)))

    def vested_outstanding_exercise_cost(self, m):
        return sum(list(map(lambda g: g.vested_outstanding_cost(m.query_date),
                            m.grants_lst)))

    def outstanding_exercise_cost(self, m):
        return sum(list(map(lambda g: g.outstanding_cost(m.query_date),
                            m.grants_lst)))

    def total_rsu(self, m):
        return sum(list(map(lambda g: g.n if g.vehicle == 'rsu' else 0,
                            m.grants_lst)))
        
    def total_iso(self, m):
        return sum(list(map(lambda g: g.n if g.vehicle == 'iso' else 0,
                            m.grants_lst)))

    def total_nso(self, m):
        return sum(list(map(lambda g: g.n if g.vehicle == 'nso' else 0,
                            m.grants_lst)))
        
    def shares_outstanding(self, m):
        return sum(list(map(lambda g: g.outstanding(m.query_date),
                            m.grants_lst)))
