"""Split honeycomb scroll case generator.

The mesh stage (`lining`, `pipeline`) uses meshlib and the B-rep stage (`case`,
`mount_disc`) uses build123d. Never import both in one process; `pipeline`
runs the B-rep stage in subprocesses.
"""

from .config import CaseConfig, Layout, load_config

__all__ = ["CaseConfig", "Layout", "load_config"]
