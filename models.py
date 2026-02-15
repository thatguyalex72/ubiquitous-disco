“””
Core data models for the framework
“””

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Service:
“”“Represents a network service”””
port: int
protocol: str
name: str
state: str
version: Optional[str] = None
host_ip: str = “”
banner: Optional[str] = None
extra_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Vulnerability:
“”“Represents a vulnerability finding”””
title: str
severity: str
description: Optional[str] = None
host_ip: str = “”
port: Optional[int] = None
cve: Optional[str] = None
cvss: Optional[float] = None
references: List[str] = field(default_factory=list)
solution: Optional[str] = None
discovered_by: str = “”
discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class WebPath:
“”“Represents a discovered web path”””
url: str
status_code: int
host_ip: str = “”
size: Optional[int] = None
redirect_location: Optional[str] = None
content_type: Optional[str] = None
words: Optional[int] = None
lines: Optional[int] = None
discovered_by: str = “”

@dataclass
class Note:
“”“Represents a note attached to a host, service, or vulnerability”””
content: str
created_at: str = field(default_factory=lambda: datetime.now().isoformat())
category: str = “general”  # general, important, todo, exploit, credentials
author: str = “pentester”

@dataclass
class Host:
“”“Represents a target host”””
ip: str
hostname: Optional[str] = None
os_info: Optional[str] = None
mac_address: Optional[str] = None
state: str = “unknown”
services: List[Service] = field(default_factory=list)
vulnerabilities: List[Vulnerability] = field(default_factory=list)
web_paths: List[WebPath] = field(default_factory=list)
notes: List[Note] = field(default_factory=list)
first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

```
def add_service(self, service: Service):
    """Add a service to the host"""
    service.host_ip = self.ip
    # Check if service already exists
    for i, existing in enumerate(self.services):
        if existing.port == service.port and existing.protocol == service.protocol:
            # Update existing service
            self.services[i] = service
            return
    self.services.append(service)
    self.last_updated = datetime.now().isoformat()

def add_vulnerability(self, vuln: Vulnerability):
    """Add a vulnerability to the host"""
    vuln.host_ip = self.ip
    self.vulnerabilities.append(vuln)
    self.last_updated = datetime.now().isoformat()

def add_web_path(self, path: WebPath):
    """Add a web path to the host"""
    path.host_ip = self.ip
    # Avoid duplicates
    if not any(p.url == path.url for p in self.web_paths):
        self.web_paths.append(path)
        self.last_updated = datetime.now().isoformat()

def add_note(self, note: Note):
    """Add a note to the host"""
    self.notes.append(note)
    self.last_updated = datetime.now().isoformat()

def get_open_ports(self) -> List[int]:
    """Get list of open ports"""
    return [s.port for s in self.services if s.state == "open"]

def get_service_by_port(self, port: int) -> Optional[Service]:
    """Get service by port number"""
    for service in self.services:
        if service.port == port:
            return service
    return None
```

@dataclass
class ScanMetadata:
“”“Metadata about a scan”””
scanner: str
scan_time: str
command: Optional[str] = None
version: Optional[str] = None
args: Optional[str] = None
