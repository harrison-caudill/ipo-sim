#!/usr/bin/env python

import math
import pylink
import pytest

from position import Grant
from position import mon_diff
from position import parse_date
from position import from_table


def test_mon_diff():

    assert 1 == mon_diff(parse_date('01/31/20'),
                         parse_date('02/29/20'))

    start = parse_date('1/2/20')
    assert 0 == mon_diff(start, parse_date('1/30/10'))
    assert 0 == mon_diff(start, parse_date('1/30/20'))
    assert 0 == mon_diff(start, parse_date('2/1/20'))
    assert 1 == mon_diff(start, parse_date('2/2/20'))
    assert 12 == mon_diff(start, parse_date('1/2/21'))
    assert 11 == mon_diff(start, parse_date('1/1/21'))

import position as anAwkward

# iso, nso, rsu
# not exercised, partially exercised, fully exercised
# not sold, partially sold, fully sold
# strike above, strike below
# partially vested, fully vested
# quarterly, monthly
GRANTS = [
    Grant(name='rsu',
          vehicle='rsu',
          strike_usd=0,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<0,
          period_months=1),

    Grant(name='nso',
          vehicle='nso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<1,
          exercised=0,
          sold=0,
          period_months=1),

    Grant(name='iso',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<2,
          exercised=0,
          sold=0,
          period_months=1),

    Grant(name='partial-exercise',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<3,
          exercised=1,
          sold=0,
          period_months=1),

    Grant(name='full-exercise',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<4,
          exercised=1<<4,
          sold=0,
          period_months=1),

    Grant(name='partial-sell',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<5,
          exercised=1,
          sold=1,
          period_months=1),

    Grant(name='full-sell',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<6,
          exercised=1<<6,
          sold=1<<6,
          period_months=1),

    Grant(name='strike-below',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<7,
          exercised=0,
          sold=0,
          period_months=1),

    Grant(name='strike-above',
          vehicle='iso',
          strike_usd=40,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<8,
          exercised=0,
          sold=0,
          period_months=1),

    Grant(name='part-vested',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=1<<9,
          exercised=0,
          sold=0,
          period_months=1),

    Grant(name='quarterly',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=16,
          n_shares=1<<10,
          exercised=0,
          sold=0,
          period_months=3),
    ]

EASY = [
    Grant(name='rsu',
          vehicle='rsu',
          strike_usd=0,
          start='1/1/20',
          n_periods=12,
          n_shares=10,
          period_months=1),

    Grant(name='nso',
          vehicle='nso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=10,
          exercised=0,
          sold=0,
          period_months=1),

    Grant(name='iso',
          vehicle='iso',
          strike_usd=4,
          start='1/1/20',
          n_periods=12,
          n_shares=10,
          exercised=0,
          sold=0,
          period_months=1),
    ]

TOT = (max(list(map(lambda x: x.n_shares, GRANTS)))<<1)-1
QUERY_DATE = '11/1/20'

@pytest.fixture
def model():
    return pylink.DAGModel([
        anAwkward.Position(GRANTS),
        ],
                           query_date='11/1/20')


class TestGrant(object):

    def test_vested(self):
        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/2/20',
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        assert 0 == g.vested('1/30/10')
        assert 0 == g.vested('1/30/20')
        assert 0 == g.vested('2/1/20')
        assert 1 == g.vested('2/2/20')
        assert 2 == g.vested('3/2/20')
        assert 12 == g.vested('1/2/21')
        assert 12 == g.vested('1/2/22')

        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/30/20',
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        assert 0 == g.vested('2/28/10')
        assert 1 == g.vested('3/1/20')

        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/1/20',
                  n_periods=4,
                  n_shares=12,
                  period_months=3)

        assert 0 == g.vested('1/30/20')
        assert 0 == g.vested('2/1/20')
        assert 3 == g.vested('4/1/20')

    def test_from_table(self):
        g = from_table(name='RSU-TK421',
                       vehicle='rsu',
                       first_date='1/1/20', first_val=750,
                       second_date='2/1/20', second_val=1000,
                       last_date='1/1/24', last_val=250,
                       n_shares=48000,
                       exercised=0,
                       sold=0)
        with pytest.raises(ValueError):
            g = from_table(name='RSU-TK421',
                           vehicle='rsu',
                           first_date='1/1/20', first_val=750,
                           second_date='2/1/20', second_val=1000,
                           last_date='1/1/24', last_val=250,
                           n_shares=4800,
                           exercised=0,
                           sold=0)

    def test_unvested(self):
        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/2/20',
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        assert 12-0 == g.unvested('1/30/10')
        assert 12-0 == g.unvested('1/30/20')
        assert 12-0 == g.unvested('2/1/20')
        assert 12-1 == g.unvested('2/2/20')
        assert 12-2 == g.unvested('3/2/20')
        assert 12-12 == g.unvested('1/2/21')
        assert 12-12 == g.unvested('1/2/22')

        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/1/20',
                  n_periods=4,
                  n_shares=12,
                  period_months=3)

        assert 12-0 == g.unvested('1/30/20')
        assert 12-0 == g.unvested('2/1/20')
        assert 12-3 == g.unvested('4/1/20')

    def test_vested_outstanding(self):
        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/2/20',
                  exercised=6,
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        assert 6 == g.vested_outstanding('1/2/21')

    def test_outstanding(self):
        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/2/20',
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        assert 12 == g.outstanding()

        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/1/20',
                  n_periods=4,
                  exercised=6,
                  sold=6,
                  n_shares=12,
                  period_months=1)

        assert 6 == g.outstanding()

    def test_held(self):
        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/1/20',
                  n_periods=4,
                  exercised=6,
                  sold=6,
                  n_shares=12,
                  period_months=1)

        assert 0 == g.held()

        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/1/20',
                  n_periods=4,
                  exercised=6,
                  sold=3,
                  n_shares=12,
                  period_months=1)

        assert 3 == g.held()

    def test_outstanding_cost(self):
        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/2/20',
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        assert 12*4 == g.outstanding_cost()

        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/1/20',
                  n_periods=4,
                  exercised=6,
                  sold=6,
                  n_shares=12,
                  period_months=1)

        assert 6*4 == g.outstanding_cost()

    def test_vested_outstanding_cost(self):
        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=4,
                  start='1/2/20',
                  exercised=6,
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        assert 6*4 == g.vested_outstanding_cost('1/2/21')

    def test_strike(self):
        with pytest.raises(ValueError):
            g = Grant(name='test',
                      vehicle='rsu',
                      strike_usd=4,
                      start='1/2/20',
                      exercised=6,
                      n_periods=12,
                      n_shares=12,
                      period_months=1)

        with pytest.raises(ValueError):
            g = Grant(name='test',
                      vehicle='iso',
                      strike_usd=0,
                      start='1/2/20',
                      exercised=6,
                      n_periods=12,
                      n_shares=12,
                      period_months=1)

        g = Grant(name='test',
                  vehicle='rsu',
                  strike_usd=0,
                  start='1/2/20',
                  exercised=6,
                  n_periods=12,
                  n_shares=12,
                  period_months=1)

        g = Grant(name='test',
                  vehicle='iso',
                  strike_usd=5,
                  start='1/2/20',
                  exercised=6,
                  n_periods=12,
                  n_shares=12,
                  period_months=1)


class TestPosition(object):
    def test_shares_total_n(self, model):
        m = model
        e = m.enum
        assert m.shares_total_n == TOT

    def test_shares_sellable_n(self, model):
        m = model
        e = m.enum
        # FIXME (use EASY)
        pass

    def test_shares_sellable_restricted_n(self, model):
        m = model
        e = m.enum
        # FIXME (use EASY)
        pass

    def test_shares_vested_n(self, model):
        m = model
        e = m.enum
        m.override(e.query_date, '1/1/21')
        assert m.shares_vested_n == TOT - (3*(1<<10)>>2)

    def test_shares_unvested_n(self, model):
        m = model
        e = m.enum
        m.override(e.query_date, '1/1/21')
        assert m.shares_unvested_n == (3*(1<<10)>>2)

    def test_shares_held_n(self, model):
        m = model
        e = m.enum
        n = 1 + (1<<4)
        assert m.shares_held_n == n

    def test_vested_outstanding(self, model):
        m = model
        e = m.enum
        m.override(e.query_date, '1/1/21')
        n = TOT - (3*(1<<10)>>2) # total vested
        n -= (1 + (1<<4) + 1 + (1<<6))
        assert m.shares_vested_outstanding_n == n

    def test_exercise_cost_vested_outstanding_usd(self, model):
        m = model
        e = m.enum
        m.override(e.query_date, '1/1/21')
        n = TOT - (3*(1<<10)>>2) # total vested
        n -= (1 + (1<<4) + 1 + (1<<6))
        n -= 1 # zero cost for the rsu
        res = (n << 2) + (1<<8) * 36 # one of them was $40/share
        assert m.exercise_cost_vested_outstanding_usd == res

    def test_shares_total_rsu_n(self, model):
        m = model
        e = m.enum
        assert 1 == m.shares_total_rsu_n

    def test_shares_total_nso_n(self, model):
        m = model
        e = m.enum
        assert 2 == m.shares_total_nso_n

    def test_shares_total_iso_n(self, model):
        m = model
        e = m.enum
        assert (TOT - 3) == m.shares_total_iso_n
