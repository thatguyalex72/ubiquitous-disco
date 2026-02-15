“””
testssl.sh JSON output parser
“””

import json
from typing import Dict, List
from urllib.parse import urlparse

class TestSSLParser:
“”“Parse testssl.sh JSON output”””

```
def parse(self, filepath: str) -> Dict:
    """Parse testssl.sh JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # testssl outputs an array of scan results
    if not isinstance(data, list):
        data = [data]
    
    hosts = {}
    
    for scan_result in data:
        # Extract target info
        target_host = scan_result.get('targetHost', scan_result.get('target_host', ''))
        target_port = scan_result.get('targetPort', scan_result.get('target_port', 443))
        
        # Parse hostname/IP
        if ':' in target_host and '://' not in target_host:
            # Remove port if included in hostname
            target_host = target_host.split(':')[0]
        
        ip = target_host or 'unknown'
        
        if ip not in hosts:
            hosts[ip] = {
                'ip': ip,
                'services': [],
                'vulnerabilities': []
            }
        
        # Add TLS service if not already present
        service_exists = any(s['port'] == target_port for s in hosts[ip]['services'])
        if not service_exists:
            hosts[ip]['services'].append({
                'port': target_port,
                'protocol': 'tcp',
                'name': 'https' if target_port == 443 else 'ssl',
                'state': 'open'
            })
        
        # Parse scan results for vulnerabilities
        scan_results = scan_result.get('scanResult', [])
        
        for result in scan_results:
            finding_id = result.get('id', '')
            severity = result.get('severity', 'INFO')
            finding = result.get('finding', '')
            
            # Skip OK and INFO findings unless they're interesting
            if severity in ['OK', 'INFO'] and not self._is_interesting_finding(finding_id):
                continue
            
            # Map severity
            mapped_severity = self._map_severity(severity)
            
            # Build vulnerability
            vuln = {
                'title': self._format_title(finding_id, finding),
                'severity': mapped_severity,
                'description': finding,
                'port': target_port,
                'discovered_by': 'testssl'
            }
            
            # Add CVE if available
            cve = result.get('cve')
            if cve and cve != 'N/A':
                vuln['cve'] = cve
            
            # Add CWE if available
            cwe = result.get('cwe')
            if cwe and cwe != 'N/A':
                vuln['description'] = f"{finding}\nCWE: {cwe}"
            
            hosts[ip]['vulnerabilities'].append(vuln)
    
    return {'hosts': list(hosts.values())}

def _is_interesting_finding(self, finding_id: str) -> bool:
    """Determine if an INFO/OK finding is interesting enough to report"""
    interesting_ids = [
        'cert_trust',
        'cert_expiration',
        'heartbleed',
        'ccs',
        'ticketbleed',
        'robot',
        'secure_renego',
        'crime',
        'breach',
        'poodle',
        'beast',
        'lucky13',
        'freak',
        'logjam',
        'drown',
        'sweet32'
    ]
    
    finding_lower = finding_id.lower()
    return any(interesting in finding_lower for interesting in interesting_ids)

def _map_severity(self, severity: str) -> str:
    """Map testssl severity to our severity levels"""
    severity_map = {
        'CRITICAL': 'critical',
        'HIGH': 'high',
        'MEDIUM': 'medium',
        'LOW': 'low',
        'WARN': 'medium',
        'INFO': 'info',
        'OK': 'info'
    }
    return severity_map.get(severity.upper(), 'info')

def _format_title(self, finding_id: str, finding: str) -> str:
    """Format a readable title from finding ID and result"""
    # Clean up finding ID
    title = finding_id.replace('_', ' ').title()
    
    # If finding is short, include it in title
    if len(finding) < 50:
        return f"{title}: {finding}"
    
    return title
```
