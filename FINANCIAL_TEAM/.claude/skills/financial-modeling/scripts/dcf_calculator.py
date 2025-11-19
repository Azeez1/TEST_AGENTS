#!/usr/bin/env python3
"""
DCF (Discounted Cash Flow) Calculator

Builds comprehensive DCF valuation models with terminal value calculations,
WACC computation, and sensitivity analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


def calculate_wacc(
    market_cap: float,
    total_debt: float,
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float
) -> float:
    """
    Calculate Weighted Average Cost of Capital (WACC).

    Args:
        market_cap: Market capitalization (equity value)
        total_debt: Total debt outstanding
        cost_of_equity: Cost of equity (e.g., from CAPM)
        cost_of_debt: Pre-tax cost of debt
        tax_rate: Corporate tax rate

    Returns:
        WACC as a decimal (e.g., 0.10 for 10%)
    """
    total_value = market_cap + total_debt
    equity_weight = market_cap / total_value
    debt_weight = total_debt / total_value

    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
    return wacc


def dcf_valuation(
    fcf_projections: List[float],
    terminal_growth_rate: float,
    wacc: float
) -> Dict[str, float]:
    """
    Perform DCF valuation with terminal value.

    Args:
        fcf_projections: List of projected free cash flows
        terminal_growth_rate: Perpetual growth rate for terminal value
        wacc: Weighted average cost of capital

    Returns:
        Dictionary with enterprise value, PV of cash flows, and terminal value
    """
    # Discount projected cash flows
    pv_fcf = []
    for i, fcf in enumerate(fcf_projections, 1):
        pv = fcf / (1 + wacc) ** i
        pv_fcf.append(pv)

    # Calculate terminal value using Gordon Growth Model
    terminal_fcf = fcf_projections[-1] * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (wacc - terminal_growth_rate)
    pv_terminal = terminal_value / (1 + wacc) ** len(fcf_projections)

    # Sum to get enterprise value
    enterprise_value = sum(pv_fcf) + pv_terminal

    return {
        'enterprise_value': enterprise_value,
        'pv_cash_flows': sum(pv_fcf),
        'pv_terminal_value': pv_terminal,
        'terminal_value': terminal_value,
        'pv_fcf_by_year': pv_fcf
    }


def build_dcf_dataframe(
    years: List[int],
    revenue: List[float],
    ebitda_margin: float,
    tax_rate: float,
    capex_pct_revenue: float,
    nwc_pct_revenue: float,
    depreciation_pct_revenue: float
) -> pd.DataFrame:
    """
    Build complete DCF model as a DataFrame.

    Args:
        years: List of projection years
        revenue: Revenue projections for each year
        ebitda_margin: EBITDA as % of revenue
        tax_rate: Corporate tax rate
        capex_pct_revenue: CapEx as % of revenue
        nwc_pct_revenue: Net Working Capital as % of revenue
        depreciation_pct_revenue: Depreciation as % of revenue

    Returns:
        DataFrame with complete P&L and FCF calculations
    """
    df = pd.DataFrame({'Year': years, 'Revenue': revenue})

    # P&L items
    df['EBITDA'] = df['Revenue'] * ebitda_margin
    df['Depreciation'] = df['Revenue'] * depreciation_pct_revenue
    df['EBIT'] = df['EBITDA'] - df['Depreciation']
    df['Taxes'] = df['EBIT'] * tax_rate
    df['NOPAT'] = df['EBIT'] - df['Taxes']

    # Cash flow adjustments
    df['Add: Depreciation'] = df['Depreciation']
    df['Less: CapEx'] = df['Revenue'] * capex_pct_revenue
    df['NWC'] = df['Revenue'] * nwc_pct_revenue
    df['Change in NWC'] = df['NWC'].diff().fillna(df['NWC'].iloc[0])

    # Free Cash Flow
    df['Free Cash Flow'] = (
        df['NOPAT']
        + df['Add: Depreciation']
        - df['Less: CapEx']
        - df['Change in NWC']
    )

    return df


def sensitivity_table(
    base_fcf: List[float],
    wacc_range: List[float],
    terminal_growth_range: List[float]
) -> pd.DataFrame:
    """
    Create two-way sensitivity table for DCF valuation.

    Args:
        base_fcf: Base case FCF projections
        wacc_range: Range of WACC values to test
        terminal_growth_range: Range of terminal growth rates to test

    Returns:
        DataFrame with sensitivity analysis results
    """
    results = []

    for tg in terminal_growth_range:
        row = []
        for wacc in wacc_range:
            valuation = dcf_valuation(base_fcf, tg, wacc)
            row.append(valuation['enterprise_value'])
        results.append(row)

    df = pd.DataFrame(
        results,
        index=[f'{tg:.1%}' for tg in terminal_growth_range],
        columns=[f'{w:.1%}' for w in wacc_range]
    )
    df.index.name = 'Terminal Growth'
    df.columns.name = 'WACC'

    return df


if __name__ == "__main__":
    # Example usage
    print("DCF Calculator Example\n")

    # Company assumptions
    market_cap = 1000  # $1B
    total_debt = 200   # $200M
    cost_of_equity = 0.12  # 12%
    cost_of_debt = 0.05    # 5%
    tax_rate = 0.25        # 25%

    wacc = calculate_wacc(market_cap, total_debt, cost_of_equity, cost_of_debt, tax_rate)
    print(f"WACC: {wacc:.2%}\n")

    # Revenue projections
    years = list(range(1, 6))
    revenue = [100, 120, 144, 173, 207]  # 20% growth

    # Build DCF model
    dcf_df = build_dcf_dataframe(
        years=years,
        revenue=revenue,
        ebitda_margin=0.30,
        tax_rate=tax_rate,
        capex_pct_revenue=0.05,
        nwc_pct_revenue=0.10,
        depreciation_pct_revenue=0.03
    )

    print("DCF Model:")
    print(dcf_df.to_string(index=False))
    print()

    # Perform valuation
    fcf = dcf_df['Free Cash Flow'].tolist()
    terminal_growth = 0.03  # 3%

    valuation = dcf_valuation(fcf, terminal_growth, wacc)
    print(f"Enterprise Value: ${valuation['enterprise_value']:.2f}M")
    print(f"PV of Cash Flows: ${valuation['pv_cash_flows']:.2f}M")
    print(f"PV of Terminal Value: ${valuation['pv_terminal_value']:.2f}M")
    print()

    # Sensitivity analysis
    print("Sensitivity Analysis:")
    sensitivity = sensitivity_table(
        fcf,
        wacc_range=[0.08, 0.09, 0.10, 0.11, 0.12],
        terminal_growth_range=[0.02, 0.025, 0.03, 0.035, 0.04]
    )
    print(sensitivity)
