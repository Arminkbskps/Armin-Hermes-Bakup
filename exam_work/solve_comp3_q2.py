import sympy as sp

# Half-lives:
# T_A = 40 min
# T_B = 50 min

# Let initial masses be m_A0 and m_B0.

# Statement I:
# t = 120 min for A: number of half-lives n_A = 120 / 40 = 3.
# Remaining fraction = (1/2)^3 = 1/8.
# Decayed fraction of A = 1 - 1/8 = 7/8.
# Decayed mass of A = (7/8) * m_A0.

# For B at t = 200 min: n_B = 200 / 50 = 4 half-lives.
# Remaining fraction = (1/2)^4 = 1/16.
# Decayed fraction of B = 1 - 1/16 = 15/16.
# Decayed mass of B = (15/16) * m_B0.

# Condition I: Decayed mass of A = 70% of decayed mass of B:
# (7/8) * m_A0 = 0.70 * (15/16) * m_B0
# (7/8) * m_A0 = (7/10) * (15/16) * m_B0
# Divide both sides by 7:
# (1/8) * m_A0 = (15/160) * m_B0 = (3/32) * m_B0
# Multiply by 8:
# m_A0 = (3/4) * m_B0  =>  m_B0 = (4/3) * m_A0.

# Statement II:
# At t = 200 min for A: n_A = 200 / 40 = 5 half-lives.
# Remaining mass of A = m_A0 / 2^5 = m_A0 / 32.
# At t = 300 min for B: n_B = 300 / 50 = 6 half-lives.
# Remaining mass of B = m_B0 / 2^6 = m_B0 / 64.

# Condition II: Remaining mass of A is 0.75 g more than remaining mass of B:
# m_A0 / 32 - m_B0 / 64 = 0.75
# Substitute m_B0 = (4/3) * m_A0:
# m_A0 / 32 - (4/3 * m_A0) / 64 = 0.75
# m_A0 / 32 - m_A0 / 48 = 0.75
# (3 m_A0 - 2 m_A0) / 96 = 0.75
# m_A0 / 96 = 3/4
# m_A0 = 96 * (3/4) = 72 g!

print("Comp3-Q2: m_A0 = 72 g -> Option 4")
