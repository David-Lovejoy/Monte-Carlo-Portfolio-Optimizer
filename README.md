# Monte-Carlo-Portfolio-Optimizer

Monte Carlo Portfolio Simulator & Optimizer:
A portfolio simulation and optimization tool built with a Python/Flask backend and JavaScript frontend. The user sets a time horizon, starting principal, asset allocation, and financial goal — the simulator runs 1,000 Monte Carlo trials and returns outcome distributions, probability of hitting the goal, and optimal allocations.

Architecture:
Backend (Python/Flask): Pulls historical price data from Yahoo Finance across user-defined year bounds (e.g. 2000–2020). Computes annualized mean returns, standard deviations, and a 5x5 covariance matrix from monthly log returns across 5 asset classes: US equities (SPY), bonds (AGG), gold (GLD), international equities (VXUS), and REITs (VNQ). Returns these to the frontend. Changing the year bounds lets the users test allocations against different historical market regimes.
Frontend (JavaScript): Runs the simulation engine and optimizer entirely in the browser.

How the simulation works:
Asset returns are modeled as a Geometric Brownian Motion process with correlated Gaussian shocks. At each time step, 5 independent standard normal draws are generated and transformed via Cholesky decomposition of the historical covariance matrix — producing 5 correlated random variables that respect the correlation structure between asset classes. Returns are accumulated additively in log-space and exponentiated to final portfolio value.

Two Optimizer modes:
Goal attainment mode: Given a principal and time horizon, find the asset allocation that maximizes the probability of reaching a target dollar amount. The SPSA optimizer's loss function is the fraction of Monte Carlo trials that hit the goal.
Ruin management mode: Find the most aggressive allocation that keeps the probability of falling below a ruin threshold under a user-specified tolerance. Formally: maximize expected portfolio value subject to P(final value < threshold) < risk tolerance.
Both modes use a derivative-free stochastic hill climber with zero-sum perturbation vectors (to maintain the allocation constraint) and shrink-factor decay near boundaries.
Variance reduction via Common Random Numbers (CRN)
The optimizer evaluates the same loss function at perturbed allocations each iteration. Without CRN, each evaluation draws fresh random shocks — making the loss function non-deterministic and causing erratic optimizer behavior. CRN pre-generates 1,000 fixed shock universes before optimization begins, so all allocation comparisons within an iteration use identical randomness. This isolates the effect of allocation changes from noise, significantly stabilizing convergence.

How to run:
pip install flask yfinance pandas numpy
python server.py
Open Start_2.html in a browser (served from localhost:8000)
Set year bounds and pull market data before running simulations
