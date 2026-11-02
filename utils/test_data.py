"""Test data in one place, so tests never hard-code credentials."""

PASSWORD = "secret_sauce"

USERS = {
    "standard": "standard_user",
    "locked": "locked_out_user",
    "problem": "problem_user",
    "glitch": "performance_glitch_user",
    "error": "error_user",
}

CHECKOUT_INFO = {
    "first_name": "Test",
    "last_name": "User",
    "postal_code": "12345",
}
