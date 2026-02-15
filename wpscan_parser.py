“””
WPScan JSON output parser
“””

import json
from typing import Dict, List
from urllib.parse import urlparse

class WPScanParser:
“”“Parse WPScan JSON output”””

```
def parse(self, filepath: str) -> Dict:
    """Parse WPScan JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Extract target info
    target_url = data.get('target_url', '')
    parsed = urlparse(target_url)
    target_ip = parsed.hostname or 'unknown'
    
    host_data = {
        'ip': target_ip,
        'vulnerabilities': []
    }
    
    # Parse interesting findings
    interesting_findings = data.get('interesting_findings', [])
    for finding in interesting_findings:
        vuln = {
            'title': finding.get('type', 'Unknown Finding'),
            'severity': self._determine_severity(finding),
            'description': self._build_description(finding),
            'references': finding.get('references', {}).get('url', []),
            'discovered_by': 'wpscan'
        }
        host_data['vulnerabilities'].append(vuln)
    
    # Parse WordPress version vulnerabilities
    version = data.get('version', {})
    if version:
        version_vulns = version.get('vulnerabilities', [])
        for vuln_data in version_vulns:
            vuln = {
                'title': vuln_data.get('title', 'WordPress Core Vulnerability'),
                'severity': self._map_severity(vuln_data.get('severity', {}).get('type', 'info')),
                'description': self._build_vuln_description(vuln_data),
                'references': [ref.get('url') for ref in vuln_data.get('references', []) if 'url' in ref],
                'discovered_by': 'wpscan'
            }
            host_data['vulnerabilities'].append(vuln)
    
    # Parse plugin vulnerabilities
    plugins = data.get('plugins', {})
    for plugin_name, plugin_data in plugins.items():
        plugin_vulns = plugin_data.get('vulnerabilities', [])
        for vuln_data in plugin_vulns:
            vuln = {
                'title': f"Plugin '{plugin_name}': {vuln_data.get('title', 'Vulnerability')}",
                'severity': self._map_severity(vuln_data.get('severity', {}).get('type', 'info')),
                'description': self._build_vuln_description(vuln_data),
                'references': [ref.get('url') for ref in vuln_data.get('references', []) if 'url' in ref],
                'discovered_by': 'wpscan'
            }
            host_data['vulnerabilities'].append(vuln)
    
    # Parse theme vulnerabilities
    themes = data.get('themes', {})
    for theme_name, theme_data in themes.items():
        theme_vulns = theme_data.get('vulnerabilities', [])
        for vuln_data in theme_vulns:
            vuln = {
                'title': f"Theme '{theme_name}': {vuln_data.get('title', 'Vulnerability')}",
                'severity': self._map_severity(vuln_data.get('severity', {}).get('type', 'info')),
                'description': self._build_vuln_description(vuln_data),
                'references': [ref.get('url') for ref in vuln_data.get('references', []) if 'url' in ref],
                'discovered_by': 'wpscan'
            }
            host_data['vulnerabilities'].append(vuln)
    
    return {'hosts': [host_data]}

def _determine_severity(self, finding: Dict) -> str:
    """Determine severity from interesting finding"""
    finding_type = finding.get('type', '').lower()
    
    if 'backup' in finding_type or 'config' in finding_type:
        return 'medium'
    elif 'upload' in finding_type or 'directory listing' in finding_type:
        return 'low'
    else:
        return 'info'

def _map_severity(self, severity_type: str) -> str:
    """Map WPScan severity to our severity levels"""
    severity_map = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
        'informational': 'info',
        'info': 'info'
    }
    return severity_map.get(severity_type.lower(), 'info')

def _build_description(self, finding: Dict) -> str:
    """Build description from interesting finding"""
    desc_parts = []
    
    if 'to_s' in finding:
        desc_parts.append(finding['to_s'])
    
    if 'url' in finding:
        desc_parts.append(f"URL: {finding['url']}")
    
    if 'found_by' in finding:
        desc_parts.append(f"Found by: {finding['found_by']}")
    
    return '\n'.join(desc_parts) if desc_parts else 'No description available'

def _build_vuln_description(self, vuln_data: Dict) -> str:
    """Build description from vulnerability data"""
    desc_parts = []
    
    # Add fixed in version if available
    fixed_in = vuln_data.get('fixed_in')
    if fixed_in:
        desc_parts.append(f"Fixed in version: {fixed_in}")
    
    # Add CVE if available
    cve = vuln_data.get('cve')
    if cve:
        desc_parts.append(f"CVE: {cve}")
    
    # Add WPVDB ID if available
    wpvdb_id = vuln_data.get('wpvdb_id')
    if wpvdb_id:
        desc_parts.append(f"WPVDB ID: {wpvdb_id}")
    
    return '\n'.join(desc_parts) if desc_parts else 'No description available'
```
