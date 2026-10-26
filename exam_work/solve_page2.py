# Page 2 questions:
# Q7 (top of page 2):
# Natural isotopes of H (1H, 2H, 3H), C (12C, 13C, 14C), O (16O, 17O, 18O) are present in EQUAL NUMBERS in a glucose molecule (C6 H12 O6).
# In this specific molecule:
# C has 6 atoms: 2 atoms of 12C, 2 atoms of 13C, 2 atoms of 14C.
# H has 12 atoms: 4 atoms of 1H, 4 atoms of 2H, 4 atoms of 3H.
# O has 6 atoms: 2 atoms of 16O, 2 atoms of 17O, 2 atoms of 18O.
# Mass of this molecule:
# M_C = 2*12 + 2*13 + 2*14 = 2*(12+13+14) = 2*39 = 78 g/mol
# M_H = 4*1 + 4*2 + 4*3 = 4*(1+2+3) = 4*6 = 24 g/mol
# M_O = 2*16 + 2*17 + 2*18 = 2*(16+17+18) = 2*51 = 102 g/mol
# M_glucose = 78 + 24 + 102 = 204 g/mol.
# We have 36.12e22 H atoms.
# Since 1 molecule has 12 H atoms:
# Number of glucose molecules = 36.12e22 / 12 = 3.01e22 molecules.
# Number of moles of glucose = 3.01e22 / 6.02e23 = 0.05 mol.
# Mass of glucose = 0.05 * 204 = 10.2 g!
# Options: 1) 10.3  2) 10.2  3) 10  4) 10.1
# Correct: Option 2!

print("P2-Q7: Mass = 10.2 g -> Option 2")

# Q8 (top of page 2):
# In ion 78_X^2-, difference between neutrons and electrons is 8: N - e = 8.
# In 78_X^2-:
# Mass number A = 78 => p + N = 78 => N = 78 - p.
# Charge is -2 => e = p + 2.
# N - e = (78 - p) - (p + 2) = 76 - 2p = 8 => 2p = 68 => p = 34.
# Then N = 78 - 34 = 44 neutrons per ion.
# Molar mass of ion ≈ 78 g/mol.
# In 31.2 g of this ion:
# Moles of ion = 31.2 / 78 = 0.4 mol.
# Total neutrons = 0.4 mol * 44 neutrons/ion * 6.02e23 = 17.6 * 6.02e23 = 1.05952e25 ≈ 1.06e25.
# Options: 1) 1.06e25  2) 1.87e25  3) 8.2e24  4) 8.6e24
# Correct: Option 1!

print("P2-Q8: Neutrons = 1.06e25 -> Option 1")

# Q9 (top of page 2):
# Natural Mg sample, mass = 81 g. Three isotopes: 24Mg, 25Mg, 26Mg.
# Abundance of lightest (24Mg): F1 = 4 * (F2 + F3).
# And F2 = F3.
# Since F1 + F2 + F3 = 100:
# F1 = 4 * (2 F2) = 8 F2.
# 8 F2 + F2 + F2 = 100 => 10 F2 = 100 => F2 = 10%, F3 = 10%, F1 = 80%.
# Average atomic mass:
# M_avg = (24*80 + 25*10 + 26*10) / 100 = (1920 + 250 + 260) / 100 = 2430 / 100 = 24.3 amu!
# In 81 g sample:
# Total moles of Mg = 81 / 24.3 = 10/3 mol.
# Moles of 24Mg = 80% * (10/3) = 0.8 * 10/3 = 8/3 mol.
# Mass of 24Mg = (8/3) mol * 24 g/mol = 8 * 8 = 64 g!
# From right to left: M_avg then mass of 24Mg:
# 24.3 and 64 g.
# Options: 1) 24.3 - 64  2) 24.4 - 68  3) 24.3 - 68  4) 24.4 - 64
# Correct: Option 1!

print("P2-Q9: M_avg = 24.3, mass = 64 -> Option 1")

# Q10 (top of page 2):
# Mg sample with 24Mg (70%), 25Mg, 26Mg.
# In Mg3 N2, mass = 30.45 g, total ions = 9.03e23.
# Total moles of ions = 9.03e23 / 6.02e23 = 1.5 mol ions.
# Each formula unit of Mg3 N2 has 3 Mg^2+ and 2 N^3- => 5 ions per unit.
# Moles of Mg3 N2 = 1.5 / 5 = 0.3 mol!
# Molar mass of Mg3 N2 = 30.45 / 0.3 = 101.5 g/mol.
# Formula mass: 3 * M_Mg + 2 * 14 = 101.5 => 3 * M_Mg + 28 = 101.5 => 3 * M_Mg = 73.5 => M_Mg = 24.5 amu!
# Now find abundance of heavier isotope (26Mg):
# Let F(25Mg) = x, F(26Mg) = y.
# 70 + x + y = 100 => x + y = 30 => x = 30 - y.
# M_avg = (24*70 + 25*x + 26*y) / 100 = 24.5
# 1680 + 25(30 - y) + 26y = 2450
# 1680 + 750 + y = 2450 => 2430 + y = 2450 => y = 20% (abundance of 26Mg)!
# Second part: cations in this amount of Mg3N2 (0.3 mol * 3 = 0.9 mol Mg^2+).
# Atoms of O in 1.6 g of SO2:
# Molar mass of SO2 = 32 + 32 = 64 g/mol.
# Moles of SO2 = 1.6 / 64 = 0.025 mol.
# Moles of O atoms = 0.025 * 2 = 0.05 mol O.
# Ratio: moles of cations / moles of O atoms = 0.9 / 0.05 = 18? Wait!
# Let's check the options for Q10:
# Options: 1) 2 - 16  2) 2 - 20  3) 3 - 20  4) 3 - 10
# Wait! In Q10, is SO2 mass 1.6 g or 9.6 g or 0.6 g?
# In OCR: "شمار اتم‌های اکسیژن در ۰/۶ کرم گوگرد دی اکسید (SO2)" or is it 9.6 g?
# If SO2 is 9.6 g: 9.6 / 64 = 0.15 mol SO2 => 0.3 mol O. Ratio = 0.9 / 0.3 = 3!
# Then F = 20% and ratio = 3 => Option 3! (20 - 3).
