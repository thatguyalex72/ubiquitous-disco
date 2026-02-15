“””
Masscan XML/JSON output parser
“””

import xml.etree.ElementTree as ET
import json
from typing import Dict, List

class MasscanParser:
“”“Parse masscan XML or JSON output”””

```
def parse(self, filepath: str) -> Dict:
    """Parse masscan output file"""
    # Determine file type
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        first_line = f.readline().strip()
    
    if first_line.startswith('<?xml') or first_line.startswith('<'):
        return self._parse_xml(filepath)
    elif first_line.startswith('{') or first_line.startswith('['):
        return self._parse_json(filepath)
    else:
        # Try as JSON list format
        return self._parse_json(filepath)

def _parse_xml(self, filepath: str) -> Dict:
    """Parse masscan XML output"""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    hosts = {}
    
    for host_elem in root.findall('host'):
        # Get IP address
        address_elem = host_elem.find('address')
        if address_elem is None:
            continue
        
        ip = address_elem.get('addr')
        
        if ip not in hosts:
            hosts[ip] = {
                'ip': ip,
                'state': 'up',
                'services': []
            }
        
        # Parse ports
        ports = host_elem.find('ports')
        if ports is not None:
            for port_elem in ports.findall('port'):
                protocol = port_elem.get('protocol', 'tcp')
                portid = int(port_elem.get('portid'))
                
                state_elem = port_elem.find('state')
                state = state_elem.get('state', 'open') if state_elem is not None else 'open'
                
                service_elem = port_elem.find('service')
                service_name = service_elem.get('name', 'unknown') if service_elem is not None else 'unknown'
                
                service = {
                    'port': portid,
                    'protocol': protocol,
                    'name': service_name,
                    'state': state
                }
                
                hosts[ip]['services'].append(service)
    
    return {'hosts': list(hosts.values())}

def _parse_json(self, filepath: str) -> Dict:
    """Parse masscan JSON output"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Masscan JSON format is a list of results
    hosts = {}
    
    for result in data:
        ip = result.get('ip')
        if not ip:
            continue
        
        if ip not in hosts:
            hosts[ip] = {
                'ip': ip,
                'state': 'up',
                'services': []
            }
        
        # Parse ports
        ports = result.get('ports', [])
        for port_info in ports:
            service = {
                'port': port_info.get('port'),
                'protocol': port_info.get('proto', 'tcp'),
                'name': port_info.get('service', 'unknown'),
                'state': port_info.get('status', 'open')
            }
            hosts[ip]['services'].append(service)
    
    return {'hosts': list(hosts.values())}
```
