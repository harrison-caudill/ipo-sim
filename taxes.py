#!/usr/bin/env python

import math
import pylink


class Taxes(object):

    def __init__(self, **overrides):
        medicare_tax_table = {
            0: 0.0145,
            250*1e3: 0.0145 + 0.009
            }

        amt_tax_table = {
            0: 0.26,
            197900: 0.28,
            }

        ss_tax_table = {
            0: 0.062,
            137700: 0.0,
            }

        sdi_tax_table = {
            0: 0.01,
            122909: 0.0
            }

        self.tribute = {

            # The various tax tables
            'medicare_tax_table': medicare_tax_table,
            'ss_tax_table': ss_tax_table,
            'amt_tax_table': amt_tax_table,
            'sdi_tax_table': sdi_tax_table,

            # Util
            'taxes_obj': self,
            'tax_exempt_contributions_usd': self.tax_exempt_contributions,
            'shares_withheld_iso_rate': 0.0,
            'shares_withheld_nso_rate': 0.0,

            # Federal Taxes
            'fed_taxes_usd': self.fed_taxes,
            'fed_taxable_income_usd': self.fed_taxable_income,
            'fed_tax_deduction_usd': self.fed_tax_deduction,
            'fed_reg_income_taxes_usd': self.fed_reg_income_taxes,
            'amt_taxes_usd': self.amt_taxes,
            'amt_base_income_usd': self.amt_base_income,
            'amt_taxable_income_usd': self.amt_taxable_income,
            'fed_random_taxes_usd': self.fed_random_taxes,
            'fed_medicare_taxes_usd': self.fed_medicare_taxes,
            'fed_ss_taxes_usd': self.fed_ss_taxes,
            'fed_itemized_deductions_usd': self.fed_itemized_deductions,
            'rsu_vesting_taxable_income_usd': self.rsu_vesting_taxable_income_usd,
            'fed_tax_rate_vs_taxable': self.fed_tax_rate_vs_taxable,
            'fed_tax_rate_vs_income': self.fed_tax_rate_vs_income,
            'amt_tax_rate_vs_taxable': self.amt_tax_rate_vs_taxable,
            'amt_tax_rate_vs_income': self.amt_tax_rate_vs_income,
            'amt_exemption_usd': self.amt_exemption_usd,
            'fed_outstanding_taxes_usd': self.fed_outstanding_taxes,

            # State Taxes
            'state_taxes_usd': self.state_taxes,
            'state_reg_income_taxes_usd': self.state_reg_income_taxes,
            'state_sdi_taxes_usd': self.state_sdi_taxes,
            'state_taxable_income_usd': self.state_taxable_income,
            'state_tax_deduction_usd': self.state_tax_deduction,
            'state_itemized_deductions_usd': self.state_itemized_deductions,
            'state_tax_rate_vs_taxable': self.state_tax_rate_vs_taxable,
            'state_tax_rate_vs_income': self.state_tax_rate_vs_income,
            'state_outstanding_taxes_usd': self.state_outstanding_taxes,

            # RSU complexity
            'rsu_fed_hold_rate': 0.22,
            'rsu_state_hold_rate': 0.1023,
            'shares_withheld_rsu_n': self.shares_withheld_rsu_n,
            'shares_withheld_rsu_rate': self.shares_withheld_rsu_rate,
            'shares_withheld_rsu_fed_n': self.shares_withheld_rsu_fed_n,
            'shares_withheld_rsu_state_n': self.shares_withheld_rsu_state_n,
            'shares_withheld_rsu_fed_rate': self.shares_withheld_rsu_fed_rate,
            'shares_withheld_rsu_state_rate': self.shares_withheld_rsu_state_rate,
            'shares_withheld_rsu_fed_usd': self.shares_withheld_rsu_fed_usd,
            'shares_withheld_rsu_state_usd': self.shares_withheld_rsu_state_usd,
            'shares_withheld_rsu_usd': self.shares_withheld_rsu_usd,

            # Final outputs
            'tax_burden_usd': self.tax_burden,
            'outstanding_taxes_usd': self.outstanding_taxes,

            }

        # Update for any passed-in values
        self.tribute.update(overrides)

    def state_outstanding_taxes(self, m):
        return ( 0.0
                 + m.state_taxes_usd
                 - m.state_withheld_usd
                 - m.shares_withheld_rsu_state_usd
                 + 0.0 )

    def fed_outstanding_taxes(self, m):
        return ( 0.0
                 + m.fed_taxes_usd
                 - m.fed_withheld_usd
                 - m.shares_withheld_rsu_fed_usd
                 + 0.0 )

    def outstanding_taxes(self, m):
        return m.fed_outstanding_taxes_usd + m.state_outstanding_taxes_usd

    def state_tax_rate_vs_taxable(self, m):
        return float(m.state_taxes_usd) / float(m.state_taxable_income_usd)

    def state_tax_rate_vs_income(self, m):
        return float(m.state_taxes_usd) / float(m.total_income_usd)

    def amt_tax_rate_vs_taxable(self, m):
        return float(m.amt_taxes_usd) / float(m.amt_taxable_income_usd)

    def amt_tax_rate_vs_income(self, m):
        return float(m.amt_taxes_usd) / float(m.total_income_usd)

    def fed_tax_rate_vs_taxable(self, m):
        return float(m.fed_taxes_usd) / float(m.fed_taxable_income_usd)

    def fed_tax_rate_vs_income(self, m):
        return float(m.fed_taxes_usd) / float(m.total_income_usd)

    def tax_burden(self, m):
        return ( 0.0
                 + m.fed_taxes_usd
                 + m.state_taxes_usd
                 + 0.0 )

    def apply_tax_table(self, v, tab):
        crit = sorted(list(tab.keys()))

        retval = 0

        for idx in range(len(tab)):

            # Find the tax rate and the taxable amount at that rate
            cur = crit[idx]
            rate = tab[cur]

            if (len(crit)-1) == idx:
                # top tax bracket, so there is no idx+1
                taxable = v - cur
            else:
                # either the whole bracket, or just the delta
                taxable = min(v, crit[idx+1]) - cur

            # Looks like we're done
            if 0 >= taxable: break

            # Compute the tax contribution
            retval += (float(taxable) * float(rate))

        return round(retval, 2)

    def shares_withheld_rsu_state_n(self, m):
        rate = m.shares_withheld_rsu_state_rate
        return int(math.ceil(m.shares_vested_rsu_eoy_n * rate))

    def shares_withheld_rsu_rate(self, m):
        return m.shares_withheld_rsu_state_rate+m.shares_withheld_rsu_fed_rate

    def shares_withheld_rsu_state_rate(self, m):
        return m.rsu_state_hold_rate

    def shares_withheld_rsu_n(self, m):
        return m.shares_withheld_rsu_state_n + m.shares_withheld_rsu_fed_n

    def shares_withheld_rsu_fed_rate(self, m):
        # FIXME: Assumes you have exceeded thresholds for the other
        #        random things (ss, sdi, foo, bar).  Drop an assert at
        #        least.  If not, then this will introduce a cycle.
        # FIXME: Unit Test
        mtab = m.medicare_tax_table
        med_val = max([mtab[k] for k in mtab.keys()])
        rate = ( 0.0
                 + m.rsu_fed_hold_rate
                 + med_val
                 + 0.0 )
        return rate

    def shares_withheld_rsu_fed_n(self, m):
        rate = m.shares_withheld_rsu_fed_rate
        return int(math.ceil(m.shares_vested_rsu_eoy_n * rate))

    def shares_withheld_rsu_usd(self, m):
        return m.shares_withheld_rsu_n * m.ipo_price_usd

    def shares_withheld_rsu_fed_usd(self, m):
        return m.shares_withheld_rsu_fed_n * m.ipo_price_usd

    def shares_withheld_rsu_state_usd(self, m):
        return m.shares_withheld_rsu_state_n * m.ipo_price_usd

    def state_taxes(self, m):
        return ( 0.0
                 + m.state_reg_income_taxes_usd
                 + m.state_sdi_taxes_usd
                 + 0.0 )

    def state_reg_income_taxes(self, m):
        v = m.state_taxable_income_usd
        tab = m.state_tax_table
        return self.apply_tax_table(v, tab)

    def state_sdi_taxes(self, m):
        v = m.state_taxable_income_usd
        tab = m.sdi_tax_table
        return self.apply_tax_table(v, tab)

    def state_taxable_income(self, m):
        return ( 0.0
                 + m.reg_income_usd
                 + m.rsu_vesting_taxable_income_usd
                 + m.nso_income_usd
                 + m.iso_sales_income_usd
                 - m.state_tax_deduction_usd
                 - m.tax_exempt_contributions_usd
                 + 0.0 )

    def state_tax_deduction(self, m):
        # Either we take the standard deduction, or we itemize
        return max(m.state_itemized_deductions_usd, m.state_std_deduction_usd)

    def state_itemized_deductions(self, m):
        # We aren't itemizing
        return 0

    def fed_taxes(self, m):
        return ( 0.0
                 + max(m.fed_reg_income_taxes_usd, m.amt_taxes_usd)
                 + m.fed_random_taxes_usd
                 + 0.0 )

    def fed_reg_income_taxes(self, m):
        v = m.fed_taxable_income_usd
        tab = m.fed_tax_table
        return self.apply_tax_table(v, tab)

    def amt_taxes(self, m):
        # FIXME: Not sure if this is right for amti >= 1e6
        v = m.amt_taxable_income_usd
        tab = m.amt_tax_table
        return self.apply_tax_table(v, tab)

    def fed_medicare_taxes(self, m):
        return self.apply_tax_table(m.fed_taxable_income_usd,
                                    m.medicare_tax_table)

    def fed_ss_taxes(self, m):
        return self.apply_tax_table(m.fed_taxable_income_usd,
                                    m.ss_tax_table)

    def fed_random_taxes(self, m):
        return ( 0.0
                 + m.fed_medicare_taxes_usd
                 + m.fed_ss_taxes_usd
                 + 0.0 )

    def rsu_vesting_taxable_income_usd(self, m):
        return ( 1.0
                 * m.shares_vested_rsu_eoy_n
                 * m.ipo_price_usd
                 * 1.0 )

    def amt_exemption_usd(self, m):
        i_crit = 1036800                # "phase-out threshold"
        income = m.amt_base_income_usd  # "amti"
        base = 113400

        if income <= i_crit: return base
        if income > (4 * base) + i_crit: return 0
        return base - ((income - i_crit) * 0.25)

    def amt_base_income(self, m):
        return ( 0.0
                 + m.reg_income_usd
                 + m.ext_amt_income_usd
                 + m.rsu_vesting_taxable_income_usd
                 + m.nso_income_usd
                 + m.iso_sales_income_usd
                 - m.tax_exempt_contributions_usd
                 + m.iso_exercise_income_usd
                 + 0.0 )

    def amt_taxable_income(self, m):
        return max(0.0,
                   ( 0.0
                     + m.amt_base_income_usd
                     - m.amt_exemption_usd
                     + 0.0 )
                   )

    def fed_taxable_income(self, m):
        return ( 0.0
                 + m.reg_income_usd
                 + m.rsu_vesting_taxable_income_usd
                 + m.nso_income_usd
                 + m.iso_sales_income_usd
                 - m.fed_tax_deduction_usd
                 - m.tax_exempt_contributions_usd
                 + 0.0 )

    def fed_tax_deduction(self, m):
        # Either we take the standard deduction, or we itemize
        return max(m.fed_itemized_deductions_usd, m.fed_std_deduction_usd)

    def fed_itemized_deductions(self, m):
        # We aren't itemizing, state tax deduction cap is $10k
        return 0

    def tax_exempt_contributions(self, m):
        return ( 0.0
                 + m.palantir_401k_usd
                 + m.palantir_fsa_usd
                 + m.palantir_drca_usd
                 + 0.0 )
