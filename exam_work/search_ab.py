# Let's search all integer isotope values for A and B:
print("Searching for A:")
for A2 in range(12, 16):
    for A3 in range(A2+1, 17):
        for f1 in range(1, 100):
            for f2 in range(1, 100 - f1):
                f3 = 100 - f1 - f2
                if 12*f1 + A2*f2 + A3*f3 == 1225:
                    if f1 in [50, 55, 80, 85] or f3 in [5, 10, 15]:
                        print(f"A: 12({f1}%), {A2}({f2}%), {A3}({f3}%) -> diff_A = {A3 - 12}")

print("\nSearching for B:")
for B2 in range(79, 85):
    for B3 in range(B2+1, 86):
        # We know from II: F(79) + F(81) = 85, F(79) - F(81) = 75 => F(79) = 80%, F(81) = 5%, so third isotope has F = 15%.
        # So B has 79 (80%), 81 (5%), and B3 (15%) or B2 (15%).
        # If the three isotopes are 79, 81, and B_other:
        for B_other in range(78, 86):
            if B_other not in [79, 81]:
                m_avg = (79*80 + 81*5 + B_other*15) / 100
                if abs(m_avg - 79.5) < 0.05 or abs(m_avg - 79.9) < 0.05:
                    b_min = min(79, 81, B_other)
                    b_max = max(79, 81, B_other)
                    print(f"B: 79(80%), 81(5%), {B_other}(15%) -> m_avg={m_avg}, diff_B = {b_max - b_min}")
