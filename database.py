“””
Database management for the framework
Uses pickle for simple persistence
“””

import pickle
import os
from typing import Dict, List, Optional
from pathlib import Path
from core.models import Host, Service, Vulnerability, WebPath

class Database:
“”“Simple database using pickle for persistence”””

```
def __init__(self, data_dir: str = "./data"):
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(exist_ok=True)
    self.current_workspace = "default"
    self.hosts: Dict[str, Host] = {}
    self._load_workspace(self.current_workspace)

def _get_workspace_file(self, workspace: str) -> Path:
    """Get the file path for a workspace"""
    return self.data_dir / f"{workspace}.pkl"

def _load_workspace(self, workspace: str):
    """Load a workspace from disk"""
    filepath = self._get_workspace_file(workspace)
    if filepath.exists():
        with open(filepath, 'rb') as f:
            self.hosts = pickle.load(f)
    else:
        self.hosts = {}

def _save_workspace(self):
    """Save current workspace to disk"""
    filepath = self._get_workspace_file(self.current_workspace)
    with open(filepath, 'wb') as f:
        pickle.dump(self.hosts, f)

def list_workspaces(self) -> List[str]:
    """List all available workspaces"""
    workspaces = []
    for file in self.data_dir.glob("*.pkl"):
        workspaces.append(file.stem)
    if not workspaces:
        workspaces.append("default")
    return sorted(workspaces)

def create_workspace(self, name: str):
    """Create a new workspace"""
    filepath = self._get_workspace_file(name)
    if not filepath.exists():
        with open(filepath, 'wb') as f:
            pickle.dump({}, f)

def set_workspace(self, workspace: str):
    """Switch to a different workspace"""
    self._save_workspace()  # Save current workspace
    self.current_workspace = workspace
    self._load_workspace(workspace)

def delete_workspace(self, workspace: str):
    """Delete a workspace"""
    if workspace == "default":
        return  # Don't delete default
    filepath = self._get_workspace_file(workspace)
    if filepath.exists():
        filepath.unlink()

def get_or_create_host(self, ip: str) -> Host:
    """Get existing host or create new one"""
    if ip not in self.hosts:
        self.hosts[ip] = Host(ip=ip)
    return self.hosts[ip]

def get_host(self, ip: str) -> Optional[Host]:
    """Get a host by IP address"""
    return self.hosts.get(ip)

def get_hosts(self) -> List[Host]:
    """Get all hosts"""
    return list(self.hosts.values())

def search_hosts(self, keyword: str) -> List[Host]:
    """Search hosts by keyword in IP, hostname, or OS"""
    keyword = keyword.lower()
    results = []
    for host in self.hosts.values():
        if (keyword in host.ip.lower() or
            (host.hostname and keyword in host.hostname.lower()) or
            (host.os_info and keyword in host.os_info.lower())):
            results.append(host)
    return results

def get_all_services(self) -> List[Service]:
    """Get all services across all hosts"""
    services = []
    for host in self.hosts.values():
        services.extend(host.services)
    return services

def get_services_by_port(self, port: int) -> List[Service]:
    """Get all services on a specific port"""
    services = []
    for host in self.hosts.values():
        for service in host.services:
            if service.port == port:
                services.append(service)
    return services

def get_services_by_name(self, name: str) -> List[Service]:
    """Get all services by name"""
    name = name.lower()
    services = []
    for host in self.hosts.values():
        for service in host.services:
            if name in service.name.lower():
                services.append(service)
    return services

def get_all_vulnerabilities(self) -> List[Vulnerability]:
    """Get all vulnerabilities across all hosts"""
    vulns = []
    for host in self.hosts.values():
        vulns.extend(host.vulnerabilities)
    return vulns

def get_vulnerabilities_by_severity(self, severity: str) -> List[Vulnerability]:
    """Get vulnerabilities by severity level"""
    severity = severity.lower()
    vulns = []
    for host in self.hosts.values():
        for vuln in host.vulnerabilities:
            if vuln.severity.lower() == severity:
                vulns.append(vuln)
    return vulns

def import_data(self, scanner_type: str, data: Dict):
    """Import parsed scanner data"""
    if scanner_type == "nmap":
        self._import_nmap_data(data)
    elif scanner_type == "masscan":
        self._import_nmap_data(data)  # Same format as nmap
    elif scanner_type == "ffuf":
        self._import_ffuf_data(data)
    elif scanner_type == "dirbuster":
        self._import_dirbuster_data(data)
    elif scanner_type == "gobuster":
        self._import_dirbuster_data(data)  # Same format as dirbuster
    elif scanner_type == "nikto":
        self._import_nikto_data(data)
    elif scanner_type == "nuclei":
        self._import_nuclei_data(data)
    elif scanner_type == "wpscan":
        self._import_wpscan_data(data)
    elif scanner_type == "testssl":
        self._import_testssl_data(data)
    
    self._save_workspace()

def _import_nmap_data(self, data: Dict):
    """Import nmap scan data"""
    for host_data in data.get('hosts', []):
        ip = host_data['ip']
        host = self.get_or_create_host(ip)
        
        if 'hostname' in host_data:
            host.hostname = host_data['hostname']
        if 'os' in host_data:
            host.os_info = host_data['os']
        if 'mac' in host_data:
            host.mac_address = host_data['mac']
        if 'state' in host_data:
            host.state = host_data['state']
        
        for service_data in host_data.get('services', []):
            service = Service(
                port=service_data['port'],
                protocol=service_data['protocol'],
                name=service_data['name'],
                state=service_data['state'],
                version=service_data.get('version'),
                banner=service_data.get('banner')
            )
            host.add_service(service)

def _import_ffuf_data(self, data: Dict):
    """Import ffuf scan data"""
    target_ip = data.get('target_ip', 'unknown')
    host = self.get_or_create_host(target_ip)
    
    for result in data.get('results', []):
        path = WebPath(
            url=result['url'],
            status_code=result['status'],
            size=result.get('length'),
            words=result.get('words'),
            lines=result.get('lines'),
            discovered_by='ffuf'
        )
        host.add_web_path(path)

def _import_dirbuster_data(self, data: Dict):
    """Import dirbuster scan data"""
    target_ip = data.get('target_ip', 'unknown')
    host = self.get_or_create_host(target_ip)
    
    for result in data.get('results', []):
        path = WebPath(
            url=result['url'],
            status_code=result['status'],
            size=result.get('size'),
            discovered_by='dirbuster'
        )
        host.add_web_path(path)

def _import_nikto_data(self, data: Dict):
    """Import nikto scan data"""
    for host_data in data.get('hosts', []):
        ip = host_data['ip']
        host = self.get_or_create_host(ip)
        
        for vuln_data in host_data.get('vulnerabilities', []):
            vuln = Vulnerability(
                title=vuln_data['title'],
                severity=vuln_data.get('severity', 'info'),
                description=vuln_data.get('description'),
                port=vuln_data.get('port'),
                discovered_by='nikto'
            )
            host.add_vulnerability(vuln)

def _import_nuclei_data(self, data: Dict):
    """Import nuclei scan data"""
    for host_data in data.get('hosts', []):
        ip = host_data['ip']
        host = self.get_or_create_host(ip)
        
        for vuln_data in host_data.get('vulnerabilities', []):
            vuln = Vulnerability(
                title=vuln_data['title'],
                severity=vuln_data.get('severity', 'info'),
                description=vuln_data.get('description'),
                cve=vuln_data.get('cve'),
                references=vuln_data.get('references', []),
                discovered_by='nuclei'
            )
            host.add_vulnerability(vuln)

def _import_wpscan_data(self, data: Dict):
    """Import wpscan scan data"""
    for host_data in data.get('hosts', []):
        ip = host_data['ip']
        host = self.get_or_create_host(ip)
        
        for vuln_data in host_data.get('vulnerabilities', []):
            vuln = Vulnerability(
                title=vuln_data['title'],
                severity=vuln_data.get('severity', 'info'),
                description=vuln_data.get('description'),
                references=vuln_data.get('references', []),
                discovered_by='wpscan'
            )
            host.add_vulnerability(vuln)

def _import_testssl_data(self, data: Dict):
    """Import testssl scan data"""
    for host_data in data.get('hosts', []):
        ip = host_data['ip']
        host = self.get_or_create_host(ip)
        
        # Import services
        for service_data in host_data.get('services', []):
            service = Service(
                port=service_data['port'],
                protocol=service_data['protocol'],
                name=service_data['name'],
                state=service_data['state']
            )
            host.add_service(service)
        
        # Import vulnerabilities
        for vuln_data in host_data.get('vulnerabilities', []):
            vuln = Vulnerability(
                title=vuln_data['title'],
                severity=vuln_data.get('severity', 'info'),
                description=vuln_data.get('description'),
                port=vuln_data.get('port'),
                cve=vuln_data.get('cve'),
                discovered_by='testssl'
            )
            host.add_vulnerability(vuln)

def export_json(self) -> Dict:
    """Export all data as JSON-serializable dict"""
    export_data = {
        'workspace': self.current_workspace,
        'hosts': []
    }
    
    for host in self.hosts.values():
        host_data = {
            'ip': host.ip,
            'hostname': host.hostname,
            'os_info': host.os_info,
            'mac_address': host.mac_address,
            'state': host.state,
            'services': [
                {
                    'port': s.port,
                    'protocol': s.protocol,
                    'name': s.name,
                    'state': s.state,
                    'version': s.version
                } for s in host.services
            ],
            'vulnerabilities': [
                {
                    'title': v.title,
                    'severity': v.severity,
                    'description': v.description,
                    'port': v.port,
                    'cve': v.cve
                } for v in host.vulnerabilities
            ],
            'web_paths': [
                {
                    'url': p.url,
                    'status_code': p.status_code,
                    'size': p.size
                } for p in host.web_paths
            ],
            'notes': [
                {
                    'content': n.content,
                    'category': n.category,
                    'created_at': n.created_at,
                    'author': n.author
                } for n in host.notes
            ]
        }
        export_data['hosts'].append(host_data)
    
    return export_data
```
