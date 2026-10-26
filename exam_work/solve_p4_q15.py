# Isotopes in increasing mass order:
# A1 = 3a + 4
# A2 = 4a - 3
# A3 = 4a - 1
# Notice: A3 - A2 = (4a - 1) - (4a - 3) = 2.
# Given: atomic mass of lightest (A1) is 3 amu less than heaviest (A3):
# A3 - A1 = 3 => (4a - 1) - (3a + 4) = 3
# a - 5 = 3 => a = 8!
# Then the isotope masses are:
# A1 = 3(8) + 4 = 28.
# A2 = 4(8) - 3 = 29.
# A3 = 4(8) - 1 = 31.
# Notice: 28, 29, 31 (increasing order: 28 < 29 < 31). Lightest is 28, heaviest is 31 (31 - 28 = 3).
# Abundances:
# F1 = F3 + 45 => F3 = F1 - 45.
# Let F2 be the middle abundance.
# F1 + F2 + F3 = 100 => F1 + F2 + (F1 - 45) = 100 => 2 F1 + F2 = 145 => F2 = 145 - 2 F1.
# Average atomic mass M_avg = 28.75:
# M_avg = (28 F1 + 29 F2 + 31 F3) / 100 = 28.75
# 28 F1 + 29 (145 - 2 F1) + 31 (F1 - 45) = 2875
# 28 F1 + 4205 - 58 F1 + 31 F1 - 1395 = 2875
# (28 - 58 + 31) F1 + (4205 - 1395) = 2875
# -1 F1 + 2810 = 2875 => -F1 = 2875 - 2810 = 65? Wait:
# -F1 + 2810 = 2875 => F1 = 2810 - 2875 = -65? Wait!
# Let's check:
# 28 F1 + 29 F2 + 31 F3:
# Base = 28:
# M_avg - 28 = 28.75 - 28 = 0.75
# 0.75 * 100 = 75
# 1 * F2 + 3 * F3 = 75
# Substitute F3 = F1 - 45 and F2 = 145 - 2 F1:
# (145 - 2 F1) + 3 (F1 - 45) = 75
# 145 - 2 F1 + 3 F1 - 135 = 75
# F1 + 10 = 75 => F1 = 65%!
# WOW! F1 = 65%!
# Let's verify:
# F1 = 65%
# F3 = 65 - 45 = 20%
# F2 = 100 - 65 - 20 = 15%
# M_avg = (28*65 + 29*15 + 31*20) / 100 = (1820 + 435 + 620) / 100 = 2875 / 100 = 28.75!
# EXACT MATCH! F1 = 65%!
# Options: 1) 65  2) 60  3) 55  4) 70
# Option 1 is 65!
print("P4-Q15: F1 = 65% -> Option 1")
