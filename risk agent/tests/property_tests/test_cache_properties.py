"""Property-based tests for Redis Caching Layer.

Validates Property 11: Cache Transparency.
Requirements: 15.2
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.risk_intelligence_agent.cache import RiskCache, generate_cache_key


@st.composite
def cache_data_strategy(draw):
    """Generate random valid cache data payloads."""
    gstin = draw(st.text(min_size=15, max_size=15, alphabet="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    pan = draw(st.text(min_size=10, max_size=10, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
    timestamps = {
        "gst": draw(st.text(min_size=5, max_size=10)),
        "upi": draw(st.text(min_size=5, max_size=10)),
        "aa": draw(st.text(min_size=5, max_size=10))
    }
    payload = {
        "gstin": gstin,
        "pan": pan,
        "score": draw(st.floats(min_value=0.0, max_value=100.0)),
        "recommendation": draw(st.sampled_from(["APPROVE", "REJECT", "MANUAL_REVIEW"]))
    }
    return gstin, pan, timestamps, payload


@given(data=cache_data_strategy())
@settings(max_examples=50, deadline=None)
def test_property_cache_transparency_and_metrics(data):
    """**Validates: Requirements 15.2**
    
    Property 11: Cache Transparency & Metrics Accuracy
    - Verify that caching is transparent (the retrieved value exactly matches what was written).
    - Verify that get_cache_metrics updates hits, misses, and total requests correctly.
    """
    gstin, pan, timestamps, payload = data
    
    # Initialize a clean mock cache
    cache = RiskCache()
    
    # Generate cache key
    key = generate_cache_key(gstin, pan, timestamps)
    
    # 1. First get must be a miss
    retrieved_1 = cache.get_cached_validated_data(key)
    assert retrieved_1 is None
    assert cache.cache_misses == 1
    assert cache.cache_hits == 0
    assert cache.total_requests == 1
    
    # 2. Write to cache
    success = cache.cache_validated_data(key, payload)
    assert success is True
    
    # 3. Second get must be a hit and match payload
    retrieved_2 = cache.get_cached_validated_data(key)
    assert retrieved_2 == payload
    assert cache.cache_misses == 1
    assert cache.cache_hits == 1
    assert cache.total_requests == 2
    
    # 4. Third get must be a hit
    retrieved_3 = cache.get_cached_validated_data(key)
    assert retrieved_3 == payload
    assert cache.cache_misses == 1
    assert cache.cache_hits == 2
    assert cache.total_requests == 3
    
    # Metrics assertion
    metrics = cache.get_cache_metrics()
    assert metrics["cache_hits"] == 2
    assert metrics["cache_misses"] == 1
    assert metrics["total_requests"] == 3
    assert metrics["hit_rate_percentage"] == pytest.approx(66.67, abs=0.01)
