# BUG-002: Checkout: typing a last name overwrites the first name field (problem_user)

**Severity:** high  
**Labels:** app-bug

## Steps to reproduce
1. Log in as `problem_user`.
2. Add the Backpack to the cart, open the cart and click Checkout.
3. Type a first name, then type a last name.

## Expected
The last name appears in the Last Name field and the first name stays as typed.

## Actual
Last Name stays empty and the First Name field shows "User", the last name value.

## Evidence
- Test: tests/test_known_failures.py::test_problem_user_can_enter_last_name[chromium]
- Screenshot: reports/artifacts/tests-test-known-failures-py-test-problem-user-can-enter-last-name-chromium/test-failed-1.png
- Reruns: failed 3 of 3
