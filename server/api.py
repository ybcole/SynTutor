"""Compatibility import for existing callers of the analysis core."""

import sys

import analysis_api

sys.modules[__name__] = analysis_api
