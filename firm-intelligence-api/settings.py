"""
Setting read from the environment in one place
"""
import os

ASURE_SEARCH_ENDPOINT = os.environ.get("ASURE_SEARCH_ENDPOINT", "")

ASURE_SEARCH_INDEX = os.environ.get("ASURE_SEARCH_INDEX", "firm-chunks-v1")

SEMANTIC_CONFIG = "firm_semantic"

RERANKER_FLOOR = float(os.environ.get("RERANKER_FLOOR", "2.0"))

EXACT_MATCH_RULE = os.environ.get("EXACT_MATCH_RULE", "1") == "1"
