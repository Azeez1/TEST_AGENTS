#!/usr/bin/env python3
"""
Scenario Analysis Tool

Create and compare multiple scenarios (base/bull/bear) for financial models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List


def create_scenarios(
    base_assumptions: Dict[str, float],
    bull_adjustments: Dict[str, float],
    bear_adjustments: Dict[str, float]
) -> Dict[str, Dict[str, float]]:
    """
    Create three scenarios from base assumptions.

    Args:
        base_assumptions: Base case assumptions
        bull_adjustments: Multipliers for bull case (e.g., {'revenue_growth': 1.2})
        bear_adjustments: Multipliers for bear case (e.g., {'revenue_growth': 0.8})

    Returns:
        Dictionary with bear, base, and bull scenarios
    """
    scenarios = {'base': base_assumptions.copy()}

    # Bull case
    scenarios['bull'] = base_assumptions.copy()
    for key, multiplier in bull_adjustments.items():
        if key in scenarios['bull']:
            scenarios['bull'][key] *= multiplier

    # Bear case
    scenarios['bear'] = base_assumptions.copy()
    for key, multiplier in bear_adjustments.items():
        if key in scenarios['bear']:
            scenarios['bear'][key] *= multiplier

    return scenarios


def compare_scenarios_table(scenarios_results: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Create comparison table of scenario outputs.

    Args:
        scenarios_results: Dict of scenario names to output metrics

    Returns:
        DataFrame comparing scenarios side-by-side
    """
    return pd.DataFrame(scenarios_results).T


def monte_carlo_simulation(
    base_value: float,
    volatility: float,
    num_simulations: int = 1000,
    periods: int = 5
) -> Dict[str, any]:
    """
    Run Monte Carlo simulation for probabilistic outcomes.

    Args:
        base_value: Starting value
        volatility: Annual volatility (std dev)
        num_simulations: Number of simulation runs
        periods: Number of time periods

    Returns:
        Dictionary with simulation results and statistics
    """
    results = []

    for _ in range(num_simulations):
        path = [base_value]
        for period in range(periods):
            shock = np.random.normal(0, volatility)
            next_val = path[-1] * (1 + shock)
            path.append(next_val)
        results.append(path[-1])  # Final value

    return {
        'mean': np.mean(results),
        'median': np.median(results),
        'std': np.std(results),
        'percentile_5': np.percentile(results, 5),
        'percentile_25': np.percentile(results, 25),
        'percentile_75': np.percentile(results, 75),
        'percentile_95': np.percentile(results, 95),
        'all_results': results
    }


if __name__ == "__main__":
    print("Scenario Analysis Example\n")

    # Base assumptions
    base = {
        'revenue': 100,
        'revenue_growth': 0.20,
        'ebitda_margin': 0.30,
        'terminal_value': 500
    }

    # Scenario adjustments
    bull = {'revenue_growth': 1.25, 'ebitda_margin': 1.10}  # +25% growth, +10% margin
    bear = {'revenue_growth': 0.75, 'ebitda_margin': 0.90}  # -25% growth, -10% margin

    scenarios = create_scenarios(base, bull, bear)

    print("Scenario Assumptions:")
    for name, assumptions in scenarios.items():
        print(f"\n{name.upper()}:")
        for key, value in assumptions.items():
            if 'growth' in key or 'margin' in key:
                print(f"  {key}: {value:.1%}")
            else:
                print(f"  {key}: {value:.2f}")

    print("\n" + "="*50)
    print("\nMonte Carlo Simulation Example:")
    mc_results = monte_carlo_simulation(
        base_value=100,
        volatility=0.20,
        num_simulations=10000,
        periods=5
    )

    print(f"Mean outcome: ${mc_results['mean']:.2f}")
    print(f"Median outcome: ${mc_results['median']:.2f}")
    print(f"5th percentile: ${mc_results['percentile_5']:.2f}")
    print(f"95th percentile: ${mc_results['percentile_95']:.2f}")
