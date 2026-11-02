# Triage Summary

| Test | Category | Reasoning | Action |
|---|---|---|---|
| test_problem_user_sort_price_low_to_high | app_bug | Failed 3/3 reruns; sort option leaves order unchanged, test expectation is reasonable | BUG-001 |
| test_problem_user_can_enter_last_name | app_bug | Failed 3/3 reruns; last name value lands in the First Name field | BUG-002 |
| test_wrong_expected_title | test_bug | Failed 3/3 reruns; page correctly shows "Products", test expects "Product List" | Fix the test: expect "Products" |
