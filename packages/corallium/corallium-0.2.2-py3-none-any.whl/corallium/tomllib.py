"""Export tomllib."""

try:
    import tomllib  # pyright: ignore[reportMissingImports]  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # noqa: F401
