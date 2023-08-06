"""Elephant Specification Language format support."""

try:
    from raesl.compile import to_graph as from_esl  # noqa
except ImportError:
    raise ImportError("Package 'raesl' needs to be available to convert the ESL format.")
