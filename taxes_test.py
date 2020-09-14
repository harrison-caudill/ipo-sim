#!/usr/bin/env python

import pylink
import pytest

import taxes as deathAnd
import income as myMeager
import position as anAwkward


@pytest.fixture
def model():
    fed_married_joint = {
        0      : 0.1,
        19750  : 0.12,
        80250  : 0.22,
        171050 : 0.24,
        326600 : 0.32,
        414700 : 0.35,
        622050 : 0.37
        }

    ca_married = {
        0 : 0.01,
        17618 : 0.02,
        41766 : 0.04,
        65920 : 0.06,
        91506 : 0.08,
        115648 : 0.093,
        590746 : 0.103,
        708890 : 0.113,
        1181484 : 0.123,
        1999999 : 0.133
        }

    return pylink.DAGModel([deathAnd.Taxes(),
                            anAwkward.Position([]),
                            myMeager.Income(),],
                           **{'palantir_401k_usd': 0,
                              'fed_tax_table': fed_married_joint,
                              'state_tax_table': ca_married,
                              'amt_exemption_rolloff_threshhold_usd': 1036800,
                              'amt_exemption_base_usd': 113400,
                              'palantir_fsa_usd': 0,
                              'palantir_drca_usd': 0,
                              'iso_exercise_income_usd': 0,
                              'ext_amt_income_usd': 0,
                              'reg_income_usd': 0,
                              'ipo_price_usd': 1,
                              'fed_std_deduction_usd': 1,
                              'state_std_deduction_usd': 1,
                              'query_date': '1/10/10',
                              })


class TestTaxes(object):

    def test_tax_tables(self, model):

        table = {
            0:    0.1,
            100:  0.2,
            1000: 0.5,
            }

        m = model

        taxes = m.taxes_obj.apply_tax_table(0, table)
        assert abs(taxes - 0) < 1e-4;

        taxes = m.taxes_obj.apply_tax_table(50, table)
        assert abs(taxes - 5.0) < 1e-4;

        taxes = m.taxes_obj.apply_tax_table(100, table)
        assert abs(taxes - 10.0) < 1e-4;

        taxes = m.taxes_obj.apply_tax_table(110, table)
        assert abs(taxes - 12) < 1e-4;

        taxes = m.taxes_obj.apply_tax_table(200, table)
        assert abs(taxes - 30) < 1e-4;

        taxes = m.taxes_obj.apply_tax_table(1000, table)
        assert abs(taxes - 190) < 1e-4;

        taxes = m.taxes_obj.apply_tax_table(5000, table)
        assert abs(taxes - 2190) < 1e-4;

    def test_exempt_contributions(self, model):
        m = model
        e = m.enum

        m.override(e.palantir_401k_usd, 0xf00)
        m.override(e.palantir_fsa_usd, 0xdeadbeef)
        m.override(e.palantir_drca_usd, 0x0ff1ce)

        proper = 0xf00 + 0xdeadbeef + 0x0ff1ce

        assert abs(m.tax_exempt_contributions_usd - proper) < 1e-4

    def test_fed_taxes_usd(self, model):
        m = model
        e = m.enum

        m.override(e.fed_random_taxes_usd, 50)
        m.override(e.fed_reg_income_taxes_usd, 100)

        m.override(e.amt_taxes_usd, 75)
        assert abs(m.fed_taxes_usd - 150) < 1e-4
        
        m.override(e.amt_taxes_usd, 150)
        assert abs(m.fed_taxes_usd - 200) < 1e-4

    def test_fed_tax_deduction_usd(self, model):
        m = model
        e = m.enum

        m.override(e.fed_itemized_deductions_usd,
                   m.fed_std_deduction_usd + 1)
        assert abs(m.fed_tax_deduction_usd
                   - m.fed_itemized_deductions_usd) < 1e-4

        m.override(e.fed_itemized_deductions_usd,
                   m.fed_std_deduction_usd + 0)
        assert abs(m.fed_tax_deduction_usd
                   - m.fed_std_deduction_usd) < 1e-4

        m.override(e.fed_itemized_deductions_usd,
                   m.fed_std_deduction_usd - 1)
        assert abs(m.fed_tax_deduction_usd
                   - m.fed_std_deduction_usd) < 1e-4

    def test_fed_reg_income_taxes_usd(self, model):
        m = model
        e = m.enum

        table = {
            0:    0.1,
            100:  0.2,
            1000: 0.5,
            }
        money = 1000

        m.override(e.fed_tax_table, table)
        m.override(e.fed_taxable_income_usd, money)

        taxes = m.taxes_obj.apply_tax_table(money, table)
        assert taxes == m.fed_reg_income_taxes_usd

    def test_fed_medicare_taxes_usd(self, model):
        m = model
        e = m.enum

        table = {
            0:    0.1,
            100:  0.2,
            1000: 0.5,
            }
        money = 1000

        m.override(e.medicare_tax_table, table)
        m.override(e.fed_taxable_income_usd, money)

        taxes = m.taxes_obj.apply_tax_table(money, table)
        assert taxes == m.fed_medicare_taxes_usd

    def test_fed_ss_taxes_usd(self, model):
        m = model
        e = m.enum

        table = {
            0:    0.1,
            100:  0.2,
            1000: 0.5,
            }
        money = 1000

        m.override(e.ss_tax_table, table)
        m.override(e.fed_taxable_income_usd, money)

        taxes = m.taxes_obj.apply_tax_table(money, table)
        assert taxes == m.fed_ss_taxes_usd

    def test_amt_taxes_usd(self, model):
        m = model
        e = m.enum

        table = {
            0:    0.1,
            100:  0.2,
            1000: 0.5,
            }
        money = 1000

        m.override(e.amt_tax_table, table)
        m.override(e.amt_taxable_income_usd, money)

        taxes = m.taxes_obj.apply_tax_table(money, table)
        assert taxes == m.amt_taxes_usd

    def set_all_income(self, m):
        """Set everything to 100.

        That way we can watch for irrelevant input being considered.
        """
        e = m.enum
        for node in [
            e.fed_taxable_income_usd,
            e.fed_tax_deduction_usd,
            e.amt_base_income_usd,
            e.amt_taxable_income_usd,
            e.fed_random_taxes_usd,
            e.fed_itemized_deductions_usd,
            e.fed_reg_income_taxes_usd,
            e.rsu_vesting_taxable_income_usd,
            e.state_reg_income_taxes_usd,
            e.state_taxable_income_usd,
            e.state_tax_deduction_usd,
            e.state_itemized_deductions_usd,
            e.shares_withheld_rsu_n,
            e.shares_withheld_rsu_fed_n,
            e.shares_withheld_rsu_state_n,
            e.shares_withheld_rsu_fed_usd,
            e.shares_withheld_rsu_state_usd,
            e.shares_withheld_rsu_usd,
            e.tax_exempt_contributions_usd,
            e.amt_exemption_usd,
            e.ext_amt_income_usd,
            ]:
            m.override(node, 100)

    def test_amt_taxable_income_usd(self, model):
        m = model
        e = m.enum
        self.set_all_income(m)

        m.override(e.amt_base_income_usd, 2)
        m.override(e.amt_exemption_usd, 1)
        m.revert(e.amt_taxable_income_usd)

        assert abs(0.0
                   + m.amt_taxable_income_usd
                   - 1
                   + 0.0) < 1e-4

    def test_amt_base_income(self, model):
        m = model
        e = m.enum
        self.set_all_income(m)

        m.override(e.reg_income_usd, 1)
        m.override(e.ext_amt_income_usd, 1)
        m.override(e.rsu_vesting_taxable_income_usd, 1)
        m.override(e.nso_income_usd, 1)
        m.override(e.iso_sales_income_usd, 1)
        m.override(e.iso_exercise_income_usd, 1)

        m.override(e.tax_exempt_contributions_usd, 1)

        m.revert(e.amt_base_income_usd)

        assert abs(0.0
                   + m.amt_base_income_usd
                   - 5
                   + 0.0) < 1e-4

    def test_amt_exemption_usd(self, model):
        m = model
        e = m.enum
        i_crit = 1036800
        base = 113400

        m.override(e.amt_base_income_usd, 0)
        print(base, m.amt_exemption_usd)
        assert base == m.amt_exemption_usd

        m.override(e.amt_base_income_usd, i_crit - 1)
        assert base == m.amt_exemption_usd

        m.override(e.amt_base_income_usd, i_crit)
        assert base == m.amt_exemption_usd

        m.override(e.amt_base_income_usd, i_crit+4)
        assert (base-1) == m.amt_exemption_usd

        m.override(e.amt_base_income_usd, i_crit+4*base)
        assert 0 == m.amt_exemption_usd


    def test_fed_random_taxes_usd(self, model):
        m = model
        e = m.enum
        self.set_all_income(m)

        m.override(e.fed_ss_taxes_usd, 1)
        m.override(e.fed_medicare_taxes_usd, 1)
        m.revert(e.fed_random_taxes_usd)

        assert abs(0.0
                   + m.fed_random_taxes_usd
                   - 2
                   + 0.0) < 1e-4


    def test_state_taxes_usd(self, model):
        m = model
        e = m.enum
        self.set_all_income(m)

        m.override(e.state_sdi_taxes_usd, 1)
        m.override(e.state_reg_income_taxes_usd, 1)
        m.revert(e.state_taxes_usd)

        assert abs(0.0
                   + m.state_taxes_usd
                   - 2
                   + 0.0) < 1e-4

    def test_state_reg_income_taxes_usd(self, model):
        m = model
        e = m.enum

        table = {
            0:    0.1,
            100:  0.2,
            1000: 0.5,
            }
        money = 1000

        m.override(e.state_tax_table, table)
        m.override(e.state_taxable_income_usd, money)

        taxes = m.taxes_obj.apply_tax_table(money, table)
        assert taxes == m.state_reg_income_taxes_usd

    def test_state_sdi_taxes_usd(self, model):
        m = model
        e = m.enum

        self.set_all_income(m)
        m.override(e.state_taxable_income_usd, 100)
        table = {
            0:    0.01,
            1000:  0.0,
            }
        m.override(e.sdi_tax_table, table)
        m.revert(e.state_sdi_taxes_usd)

        assert abs( m.state_sdi_taxes_usd - 1 ) == 0

    def test_state_taxable_income_usd(self, model):
        m = model
        e = m.enum
        self.set_all_income(m)

        m.override(e.reg_income_usd, 1)
        m.override(e.nso_income_usd, 1)
        m.override(e.iso_sales_income_usd, 1)
        m.override(e.rsu_vesting_taxable_income_usd, 1)

        m.override(e.tax_exempt_contributions_usd, 1)
        m.override(e.state_tax_deduction_usd, 1)

        m.revert(e.state_taxable_income_usd)

        assert abs(0.0
                   + m.state_taxable_income_usd
                   - 2
                   + 0.0) < 1e-4

    def test_state_tax_deduction_usd(self, model):
        m = model
        e = m.enum

        m.override(e.state_itemized_deductions_usd,
                   m.state_std_deduction_usd + 1)
        assert abs(m.state_tax_deduction_usd
                   - m.state_itemized_deductions_usd) < 1e-4

        m.override(e.state_itemized_deductions_usd,
                   m.state_std_deduction_usd + 0)
        assert abs(m.state_tax_deduction_usd
                   - m.state_std_deduction_usd) < 1e-4

        m.override(e.state_itemized_deductions_usd,
                   m.state_std_deduction_usd - 1)
        assert abs(m.state_tax_deduction_usd
                   - m.state_std_deduction_usd) < 1e-4

    def test_state_itemized_deductions_usd(self, model):
        m = model
        e = m.enum

        # not implemented
        assert 0 == m.state_itemized_deductions_usd

    def test_fed_taxable_income_usd(self, model):
        m = model
        e = m.enum
        self.set_all_income(m)

        m.override(e.reg_income_usd, 1)
        m.override(e.rsu_vesting_taxable_income_usd, 1)
        m.override(e.nso_income_usd, 1)
        m.override(e.iso_sales_income_usd, 1)
        m.override(e.rsu_vesting_taxable_income_usd, 1)

        m.override(e.tax_exempt_contributions_usd, 1)
        m.override(e.fed_tax_deduction_usd, 1)

        m.revert(e.fed_taxable_income_usd)

        assert abs(0.0
                   + m.fed_taxable_income_usd
                   - 2
                   + 0.0) < 1e-4

    def test_tax_burden_usd(self, model):
        m = model
        e = m.enum

        m.override(e.state_sdi_taxes_usd, 100)
        m.override(e.state_reg_income_taxes_usd, 100)
        m.override(e.fed_random_taxes_usd, 100)
        m.override(e.fed_reg_income_taxes_usd, 100)
        m.override(e.amt_taxes_usd, 100)
        m.override(e.fed_ss_taxes_usd, 100)
        m.override(e.fed_medicare_taxes_usd, 100)
        m.override(e.state_taxes_usd, 1)
        m.override(e.fed_taxes_usd, 1)

        assert abs(m.tax_burden_usd - 2) < 1e-4

