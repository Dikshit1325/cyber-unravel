import threading
from typing import Any, Tuple
import pandas as pd
import networkx as nx

from services.data_loader import load_all_data
from services.entity_resolution import EntityResolver
from services.graph_engine import build_investigation_graph

class CacheManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CacheManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.data: dict[str, pd.DataFrame] = None
        self.resolver: EntityResolver = None
        self.graph: nx.MultiDiGraph = None
        self._data_lock = threading.Lock()
        self._initialized = True

    def get_data(self) -> Tuple[dict[str, pd.DataFrame], EntityResolver, nx.MultiDiGraph]:
        with self._data_lock:
            if self.data is None or self.resolver is None or self.graph is None:
                self.data = load_all_data()
                self.resolver = EntityResolver(self.data["persons"])
                self.graph = build_investigation_graph(self.data)
            return self.data, self.resolver, self.graph

    def clear(self):
        with self._data_lock:
            self.data = None
            self.resolver = None
            self.graph = None
