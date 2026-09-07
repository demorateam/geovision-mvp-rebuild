"""Service layer.

Business logic lives here. Services coordinate repositories (database access)
and the external service integrations (ai, neshan, otp) and raise FastAPI
HTTPExceptions exactly like the original route handlers did.
"""
