#!/usr/bin/env python3
"""Superforecasting & Probabilistic Analysis Toolkit.

Tools for disciplined forecasting:
- Bayesian probability updating
- Base-rate calibration
- Fermi decomposition with log-normal confidence bounds
- Monte Carlo simulation for arrival times / value thresholds
- Brier score calculation
"""

import sys
import math
import argparse
import json
import numpy as np


def bayesian_update(prior: float, likelihood_ratio: float) -> dict:
    """Update prior probability using Bayes factor / Likelihood Ratio (P(E|H) / P(E|~H))."""
    if prior <= 0 or prior >= 1:
        raise ValueError("Prior must be strictly between 0 and 1.")
    if likelihood_ratio <= 0:
        raise ValueError("Likelihood ratio must be positive.")
    
    prior_odds = prior / (1.0 - prior)
    posterior_odds = prior_odds * likelihood_ratio
    posterior = posterior_odds / (1.0 + posterior_odds)
    
    return {
        "prior": round(prior, 4),
        "likelihood_ratio": round(likelihood_ratio, 4),
        "posterior": round(posterior, 4),
        "posterior_pct": f"{posterior * 100:.2f}%"
    }


def fermi_bounds(factors: list[tuple[float, float]]) -> dict:
    """Combine independent log-normal factors given as (low_90, high_90).
    
    Returns 5th, 50th (median), and 95th percentiles.
    """
    mu_sum = 0.0
    var_sum = 0.0
    
    for low, high in factors:
        if low <= 0 or high <= 0 or low >= high:
            raise ValueError(f"Invalid factor bounds: ({low}, {high})")
        # For lognormal 90% interval [low, high]:
        # log(low) = mu - 1.645 * sigma, log(high) = mu + 1.645 * sigma
        log_l = math.log(low)
        log_h = math.log(high)
        mu_i = (log_l + log_h) / 2.0
        sigma_i = (log_h - log_l) / (2.0 * 1.6448536269514722)
        mu_sum += mu_i
        var_sum += sigma_i ** 2
        
    sigma_total = math.sqrt(var_sum)
    p05 = math.exp(mu_sum - 1.6448536269514722 * sigma_total)
    p50 = math.exp(mu_sum)
    p95 = math.exp(mu_sum + 1.6448536269514722 * sigma_total)
    
    return {
        "p05_low": round(p05, 3),
        "p50_median": round(p50, 3),
        "p95_high": round(p95, 3),
        "description": "5th to 95th percentile (90% subjective confidence interval)"
    }


def monte_carlo_timeline(mean: float, std: float, trials: int = 10000, target_threshold: float = None) -> dict:
    """Run lognormal Monte Carlo simulation for time-to-event or financial metric."""
    # generate lognormal samples
    # If mean/std are given in natural units:
    variance = std ** 2
    mu = math.log((mean ** 2) / math.sqrt(variance + mean ** 2))
    sigma = math.sqrt(math.log(1.0 + (variance / (mean ** 2))))
    
    samples = np.random.lognormal(mu, sigma, trials)
    
    res = {
        "mean": round(float(np.mean(samples)), 3),
        "median": round(float(np.median(samples)), 3),
        "p10": round(float(np.percentile(samples, 10)), 3),
        "p25": round(float(np.percentile(samples, 25)), 3),
        "p75": round(float(np.percentile(samples, 75)), 3),
        "p90": round(float(np.percentile(samples, 90)), 3)
    }
    
    if target_threshold is not None:
        prob_under = float(np.mean(samples <= target_threshold))
        prob_over = float(np.mean(samples > target_threshold))
        res["prob_le_target"] = f"{prob_under * 100:.2f}%"
        res["prob_gt_target"] = f"{prob_over * 100:.2f}%"
        res["target"] = target_threshold
        
    return res


def brier_score(predictions: list[float], outcomes: list[int]) -> float:
    """Calculate Brier score for probabilistic accuracy: sum((p_i - o_i)^2) / N.
    
    0 is perfect prediction, 0.25 is random coin flip, 1.0 is completely wrong.
    """
    if len(predictions) != len(outcomes) or len(predictions) == 0:
        raise ValueError("Predictions and outcomes must have equal non-zero length.")
    
    score = sum((p - o) ** 2 for p, o in zip(predictions, outcomes)) / len(predictions)
    return round(score, 4)


def main():
    parser = argparse.ArgumentParser(description="Superforecasting Toolkit")
    subparsers = parser.add_subparsers(dest="cmd")
    
    # Bayes
    p_bayes = subparsers.add_parser("bayes", help="Update prior probability with likelihood ratio")
    p_bayes.add_argument("prior", type=float, help="Prior probability (0.0 to 1.0)")
    p_bayes.add_argument("lr", type=float, help="Likelihood ratio / Bayes factor (>0)")
    
    # Fermi
    p_fermi = subparsers.add_parser("fermi", help="Combine 90%% confidence factors: low1,high1 low2,high2 ...")
    p_fermi.add_argument("pairs", nargs="+", help="Pairs as low,high (e.g. 10,20 0.5,0.8)")
    
    # Monte Carlo
    p_mc = subparsers.add_parser("mc", help="Monte Carlo projection")
    p_mc.add_argument("mean", type=float, help="Expected mean value / time")
    p_mc.add_argument("std", type=float, help="Standard deviation / uncertainty")
    p_mc.add_argument("--target", type=float, default=None, help="Specific target threshold to check probability")
    p_mc.add_argument("--trials", type=int, default=10000, help="Number of trials")
    
    # Brier
    p_brier = subparsers.add_parser("brier", help="Brier score evaluator")
    p_brier.add_argument("--preds", nargs="+", type=float, required=True, help="List of predicted probabilities (0 to 1)")
    p_brier.add_argument("--outcomes", nargs="+", type=int, required=True, help="List of actual outcomes (0 or 1)")
    
    args = parser.parse_args()
    
    if args.cmd == "bayes":
        res = bayesian_update(args.prior, args.lr)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "fermi":
        factors = []
        for pair in args.pairs:
            l, h = map(float, pair.split(","))
            factors.append((l, h))
        res = fermi_bounds(factors)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "mc":
        res = monte_carlo_timeline(args.mean, args.std, args.trials, args.target)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "brier":
        res = brier_score(args.preds, args.outcomes)
        print(f"Brier Score: {res} (0.00 = perfect, 0.25 = random 50/50, 1.00 = always wrong)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
