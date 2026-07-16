# 1. Check abstract
grep -n -A 15 '\\abstract{' main3.tex

# 2. Check 6.8 Statistical protocol
grep -n -A 10 'Statistical protocol' main3.tex

# 3. Check Proposition 1
grep -n -A 5 'Proposition.*Decision soundness' main3.tex

# 4. Check Complexity statement
grep -n -A 5 'operations for explicit positive tables' main3.tex

# 5. Check Section 8 (Limitations)
grep -n -A 15 'Limitations and Threats' main3.tex

# 6. Check References dates
grep -n '2026' main3.tex
