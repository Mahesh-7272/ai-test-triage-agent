# BUG-001: Sorting by Price (low to high) does not reorder products (problem_user)

**Severity:** medium  
**Labels:** app-bug

## Steps to reproduce
1. Log in as `problem_user`.
2. On the Products page, choose "Price (low to high)" in the sort dropdown.
3. Read the product prices.

## Expected
Prices are ascending (7.99, 9.99, 15.99, 15.99, 29.99, 49.99).

## Actual
Order is unchanged and starts 29.99, 9.99, 15.99, 49.99. The dropdown still shows "Name (A to Z)".

## Evidence
- Test: tests/test_known_failures.py::test_problem_user_sort_price_low_to_high[chromium]
- Screenshot: reports/artifacts/tests-test-known-failures-py-test-problem-user-sort-price-low-to-high-chromium/test-failed-1.png
- Reruns: failed 3 of 3
