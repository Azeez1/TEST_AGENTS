#!/usr/bin/env python3
"""
Sensitivity Analysis Tool

Create tornado charts and data tables to analyze assumption sensitivity.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Tuple


def one_way_sensitivity(
    base_value: float,
    variable_name: str,
    variable_range: List[float],
    calculate_output: Callable
) -> pd.DataFrame:
    """
    Perform one-way sensitivity analysis.

    Args:
        base_value: Base case value
        variable_name: Name of variable being tested
        variable_range: Range of values to test
        calculate_output: Function that takes variable value and returns output

    Returns:
        DataFrame with variable values and corresponding outputs
    """
    results = []
    for value in variable_range:
        output = calculate_output(value)
        results.append({
            variable_name: value,
            'output': output,
            'change_from_base': output - base_value,
            'pct_change': (output - base_value) / base_value if base_value != 0 else 0
        })

    return pd.DataFrame(results)


def tornado_analysis(
    base_output: float,
    variables: Dict[str, Tuple[float, float]],
    calculate_output: Callable
) -> pd.DataFrame:
    """
    Create tornado chart data showing impact of each variable.

    Args:
        base_output: Base case output value
        variables: Dict of variable_name: (low_value, high_value)
        calculate_output: Function that takes **kwargs and returns output

    Returns:
        DataFrame sorted by impact magnitude (for tornado chart)
    """
    results = []

    for var_name, (low_val, high_val) in variables.items():
        # Test low value
        low_output = calculate_output(**{var_name: low_val})
        low_impact = low_output - base_output

        # Test high value
        high_output = calculate_output(**{var_name: high_val})
        high_impact = high_output - base_output

        results.append({
            'variable': var_name,
            'low_value': low_val,
            'high_value': high_val,
            'low_impact': low_impact,
            'high_impact': high_impact,
            'total_swing': abs(high_impact - low_impact)
        })

    df = pd.DataFrame(results)
    df = df.sort_values('total_swing', ascending=False)

    return df


def two_way_sensitivity_table(
    x_variable: str,
    x_range: List[float],
    y_variable: str,
    y_range: List[float],
    calculate_output: Callable
) -> pd.DataFrame:
    """
    Create two-way sensitivity table (data table).

    Args:
        x_variable: Name of x-axis variable
        x_range: Range of values for x variable
        y_variable: Name of y-axis variable
        y_range: Range of values for y variable
        calculate_output: Function that takes x, y and returns output

    Returns:
        DataFrame with sensitivity table
    """
    results = []

    for y_val in y_range:
        row = []
        for x_val in x_range:
            output = calculate_output(x_val, y_val)
            row.append(output)
        results.append(row)

    df = pd.DataFrame(
        results,
        index=y_range,
        columns=x_range
    )
    df.index.name = y_variable
    df.columns.name = x_variable

    return df


if __name__ == "__main__":
    print("Sensitivity Analysis Example\n")

    # Example: NPV sensitivity
    def calculate_npv(discount_rate, cash_flow_growth):
        cash_flows = [100 * (1 + cash_flow_growth)**i for i in range(5)]
        npv = sum(cf / (1 + discount_rate)**i for i, cf in enumerate(cash_flows, 1))
        return npv

    base_npv = calculate_npv(0.10, 0.05)
    print(f"Base case NPV: ${base_npv:.2f}\n")

    # One-way sensitivity: discount rate
    print("One-way sensitivity: Discount Rate")
    discount_range = [0.08, 0.09, 0.10, 0.11, 0.12]
    one_way = one_way_sensitivity(
        base_value=base_npv,
        variable_name='discount_rate',
        variable_range=discount_range,
        calculate_output=lambda dr: calculate_npv(dr, 0.05)
    )
    print(one_way.to_string(index=False))
    print()

    # Tornado analysis
    print("Tornado Analysis:")
    variables = {
        'discount_rate': (0.08, 0.12),
        'cash_flow_growth': (0.03, 0.07)
    }

    def calc_with_params(discount_rate=0.10, cash_flow_growth=0.05):
        return calculate_npv(discount_rate, cash_flow_growth)

    tornado = tornado_analysis(base_npv, variables, calc_with_params)
    print(tornado.to_string(index=False))
    print()

    # Two-way sensitivity table
    print("Two-way Sensitivity Table:")
    two_way = two_way_sensitivity_table(
        x_variable='Discount Rate',
        x_range=[0.08, 0.09, 0.10, 0.11, 0.12],
        y_variable='CF Growth',
        y_range=[0.03, 0.04, 0.05, 0.06, 0.07],
        calculate_output=calculate_npv
    )
    print(two_way)
