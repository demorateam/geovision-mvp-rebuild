"""HTTP/API layer.

Thin route modules: each endpoint only handles HTTP concerns (parsing,
dependencies, response shaping) and delegates to services.
Route paths, methods, function names, dependencies and response payloads are
kept identical to the pre-refactor single-module main.py.
"""
