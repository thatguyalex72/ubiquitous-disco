“””
Gobuster output parser
“””

import re
from typing import Dict, List
from urllib.parse import urlparse

class GobusterParser:
“”“Parse gobuster text output”””

```
def parse(self, filepath: str) -> Dict:
    """Parse gobuster output file"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    results = []
    target_ip = None
    base_url = None
    
    # Extract target URL from header
    url_match = re.search(r'Target\s+URL:\s+(\S+)', content, re.IGNORECASE)
    if url_match:
        base_url = url_match.group(1)
        parsed = urlparse(base_url)
        target_ip = parsed.hostname
    
    # Parse found paths
    # Pattern: /path (Status: 200) [Size: 1234]
    pattern1 = re.compile(r'^(/\S+)\s+\(Status:\s+(\d+)\)\s+\[Size:\s+(\d+)\]', re.MULTILINE)
    for match in pattern1.finditer(content):
        path = match.group(1)
        status = int(match.group(2))
        size = int(match.group(3))
        
        # Construct full URL
        if base_url:
            url = base_url.rstrip('/') + path
        else:
            url = path
        
        results.append({
            'url': url,
            'status': status,
            'size': size
        })
    
    # Pattern 2: found: /path (Status: 200) [Size: 1234]
    pattern2 = re.compile(r'found:\s+(/\S+)\s+\(Status:\s+(\d+)\)\s+\[Size:\s+(\d+)\]', re.IGNORECASE | re.MULTILINE)
    for match in pattern2.finditer(content):
        path = match.group(1)
        status = int(match.group(2))
        size = int(match.group(3))
        
        if base_url:
            url = base_url.rstrip('/') + path
        else:
            url = path
        
        # Avoid duplicates
        if not any(r['url'] == url for r in results):
            results.append({
                'url': url,
                'status': status,
                'size': size
            })
    
    # Pattern 3: Simple format without status code details
    # https://example.com/path
    if not results:
        pattern3 = re.compile(r'(https?://[^\s]+)')
        for match in pattern3.finditer(content):
            url = match.group(1)
            
            if not target_ip:
                parsed = urlparse(url)
                target_ip = parsed.hostname
            
            if not any(r['url'] == url for r in results):
                results.append({
                    'url': url,
                    'status': 200,  # Assume 200 if not specified
                    'size': None
                })
    
    # If still no target IP, try to extract from first result
    if not target_ip and results:
        parsed = urlparse(results[0]['url'])
        target_ip = parsed.hostname
    
    return {
        'target_ip': target_ip or 'unknown',
        'results': results
    }
```
