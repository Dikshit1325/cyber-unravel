import sys
sys.path.append('c:/Users/HP/OneDrive/Desktop/cyber-unravel')
from backend.services.cache_manager import CacheManager
from backend.services.anomaly_engine import AnomalyEngine

cache = CacheManager()
investigation = cache.get_investigation_data()
engine = AnomalyEngine(investigation)
result = engine.detect_all()
print('Financial:', len(result['financial']))
print('Telecom:', len(result['telecom']))
print('Network:', len(result['network']))
print('Cross-domain:', len(result['cross_domain']))
# Top 10 anomalies
top = result['all'][:10]
for f in top:
    score = f.get('score') if 'score' in f else f.get('correlation_score')
    print(f"{f['finding_id']} | {f['anomaly_type']} | score {score} | severity {f['severity']}")
