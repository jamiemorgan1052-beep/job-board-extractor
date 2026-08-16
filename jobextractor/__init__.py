"""Offline, dependency-free job listing extraction."""

from .extractor import ExtractionResult, Job, SelectorConfig, extract_jobs

__all__ = ["ExtractionResult", "Job", "SelectorConfig", "extract_jobs"]
