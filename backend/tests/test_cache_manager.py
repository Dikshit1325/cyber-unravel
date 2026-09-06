import threading
from unittest import mock
import pandas as pd
from services.cache_manager import CacheManager

def teardown_cache():
    CacheManager._instance = None
    CacheManager._initialized = False

def test_cache_singleton():
    teardown_cache()
    cache1 = CacheManager()
    cache2 = CacheManager()
    assert cache1 is cache2
    teardown_cache()

@mock.patch("services.cache_manager.load_all_data")
@mock.patch("services.cache_manager.EntityResolver")
@mock.patch("services.cache_manager.build_investigation_graph")
def test_cache_get_data(mock_build_graph, mock_resolver, mock_load_data):
    teardown_cache()
    mock_load_data.return_value = {"persons": pd.DataFrame()}
    mock_resolver.return_value = "mock_resolver_instance"
    mock_build_graph.return_value = "mock_graph_instance"

    cache = CacheManager()
    cache.clear()

    # First call: should call the mocks
    data, resolver, graph = cache.get_data()
    
    assert "persons" in data
    assert resolver == "mock_resolver_instance"
    assert graph == "mock_graph_instance"
    
    mock_load_data.assert_called_once()
    mock_resolver.assert_called_once()
    mock_build_graph.assert_called_once()

    # Second call: should NOT call the mocks again
    data2, resolver2, graph2 = cache.get_data()
    
    assert data is data2
    assert resolver is resolver2
    assert graph is graph2
    
    # Still called only once
    mock_load_data.assert_called_once()
    mock_resolver.assert_called_once()
    mock_build_graph.assert_called_once()

    # clear cache
    cache.clear()
    
    assert cache.data is None
    assert cache.resolver is None
    assert cache.graph is None

    # Third call after clear: should call the mocks again
    data3, resolver3, graph3 = cache.get_data()
    assert mock_load_data.call_count == 2
    assert mock_resolver.call_count == 2
    assert mock_build_graph.call_count == 2
    
    teardown_cache()

def test_thread_safety():
    teardown_cache()
    cache = CacheManager()
    cache.clear()
    
    results = []
    
    # We don't want to actually load CSVs in this thread safety test
    # so we mock load_all_data
    with mock.patch("services.cache_manager.load_all_data") as mock_load:
        mock_load.return_value = {"persons": pd.DataFrame()}
        with mock.patch("services.cache_manager.EntityResolver"):
            with mock.patch("services.cache_manager.build_investigation_graph"):
                
                def worker():
                    # Every thread gets the singleton and gets data
                    c = CacheManager()
                    d, r, g = c.get_data()
                    results.append((d, r, g))

                threads = [threading.Thread(target=worker) for _ in range(10)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                
                # Should only be called once despite 10 threads asking for it simultaneously
                mock_load.assert_called_once()
                
                # All threads should get the exact same objects
                first_result = results[0]
                for r in results[1:]:
                    assert r[0] is first_result[0]
                    assert r[1] is first_result[1]
                    assert r[2] is first_result[2]

    teardown_cache()
