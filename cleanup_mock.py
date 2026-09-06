import os
import re

files_to_fix = [
    'src/routes/timeline.tsx',
    'src/routes/reports.tsx',
    'src/routes/graph.tsx',
    'src/routes/entities.index.tsx',
    'src/routes/entities.$entityId.tsx',
    'src/routes/data-sources.tsx',
    'src/routes/dashboard.tsx',
    'src/routes/cross-domain.tsx',
    'src/routes/clusters.tsx',
    'src/routes/cases.tsx',
    'src/routes/anomalies.tsx',
    'src/components/investigation/AppShell.tsx',
    'src/components/investigation/EntityDrawer.tsx'
]

for fpath in files_to_fix:
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove import from mock-data
    content = re.sub(r'import\s+\{.*?\}.*?mock-data.*?;\n', '', content)
    
    # dashboard.tsx
    content = content.replace('platform.motto', '"Uncovering the truth hidden in the data."')
    
    # anomalies.tsx
    content = content.replace('return anomalies;', 'return [];')
    
    # timeline.tsx
    content = re.sub(r'cases\[0\]\?\.id \?\? "CASE-2026-1024"', '"CASE-2026-1024"', content)
    content = re.sub(r'cases\.map', '[{id: "CASE-2026-1024"}].map', content)
    
    # cases.tsx
    content = content.replace('seedCases', '[]')
    content = content.replace('investigator.name', '"Investigator"')
    
    # AppShell.tsx
    content = content.replace('platform.name', '"SENTINEL"')
    content = content.replace('investigator.name', '"Investigator"')
    content = content.replace('investigator.role', '"Analyst"')
    content = content.replace('investigator.initials', '"INV"')
    content = content.replace('primaryCase.id', '"CASE-2026-1024"')
    content = content.replace('primaryCase.name', '"Primary Case"')
    content = content.replace('alerts.length', '0')
    content = content.replace('alerts.filter', '[].filter')
    content = content.replace('alerts.map', '[].map')
    content = content.replace('alerts', '[]') # for any stray alerts
    
    # reports.tsx
    content = content.replace('entities.length', '0')
    content = content.replace('anomalies.length', '0')
    content = content.replace('timelineEvents.length', '0')
    
    # graph.tsx
    content = content.replace('clusters[0]', '{}')
    content = content.replace('clusters.length', '0')
    content = content.replace('clusters', '[]')
    content = content.replace('hiddenRelationships.slice', '[].slice')
    content = content.replace('hiddenRelationships', '[]')
    
    # entities.index.tsx
    content = content.replace('entities', '[]')
    
    # entities.$entityId.tsx
    content = content.replace('return entities', 'return []')
    content = content.replace('entities.find', '[].find')
    content = content.replace('entities.filter', '[].filter')
    
    # data-sources.tsx
    content = content.replace('datasets', '[]')
    
    # cross-domain.tsx
    content = content.replace('crossDomainChain', '[]')
    
    # clusters.tsx
    content = content.replace('clusters.map', '[].map')
    
    # EntityDrawer.tsx
    content = content.replace('entities.find', '[].find')
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Mock data removed.")
