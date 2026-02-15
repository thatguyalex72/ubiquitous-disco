“””
Nuclei JSON output parser
“””

import json
from typing import Dict, List
from urllib.parse import urlparse

class NucleiParser:
“”“Parse nuclei JSON output”””

```
def parse(self, filepath: str) -> Dict:
    """Parse nuclei JSONL (JSON Lines) output"""
    hosts = {}
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                result = json.loads(line)
                self._process_result(result, hosts)
            except json.JSONDecodeError:
                continue
    
    return {'hosts': list(hosts.values())}

def _process_result(self, result: Dict, hosts: Dict):
    """Process a single nuclei result"""
    # Extract target info
    host_url = result.get('host', result.get('matched-at', ''))
    if not host_url:
        return
    
    # Parse URL to get IP/hostname
    parsed = urlparse(host_url)
    ip = parsed.hostname or host_url
    
    if ip not in hosts:
        hosts[ip] = {
            'ip': ip,
            'vulnerabilities': []
        }
    
    # Extract vulnerability information
    template_id = result.get('template-id', result.get('templateID', 'unknown'))
    info = result.get('info', {})
    
    title = info.get('name', template_id)
    description = info.get('description', '')
    severity = info.get('severity', 'info').lower()
    
    # Map nuclei severity to our severity levels
    severity_map = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
        'info': 'info',
        'unknown': 'info'
    }
    severity = severity_map.get(severity, 'info')
    
    # Extract tags
    tags = info.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',')]
    
    # Get CVE/CWE references
    classification = info.get('classification', {})
    cve_id = classification.get('cve-id')
    cwe_id = classification.get('cwe-id')
    
    # Build references
    references = info.get('reference', [])
    if isinstance(references, str):
        references = [references]
    
    vuln = {
        'title': title,
        'severity': severity,
        'description': description,
        'cve': cve_id,
        'references': references,
        'discovered_by': 'nuclei'
    }
    
    # Add matched URL info
    matched_at = result.get('matched-at', host_url)
    if matched_at:
        vuln['description'] = f"{description}\n\nMatched at: {matched_at}".strip()
    
    # Add extracted data if available
    extracted = result.get('extracted-results')
    if extracted:
        vuln['description'] = f"{vuln['description']}\n\nExtracted: {', '.join(map(str, extracted))}".strip()
    
    hosts[ip]['vulnerabilities'].append(vuln)
```
