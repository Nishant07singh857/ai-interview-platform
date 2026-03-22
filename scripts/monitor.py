#!/usr/bin/env python3
"""
System Monitoring Script
Run: python scripts/monitor.py
"""

import asyncio
import aiohttp
import psutil
import json
import logging
from datetime import datetime
from typing import Dict, Any
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring utility"""
    
    def __init__(self, config_path: str = "monitor_config.json"):
        self.config = self.load_config(config_path)
        self.metrics = {}
        
    def load_config(self, path: str) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "services": [
                {"name": "backend", "url": "http://localhost:8000/health", "port": 8000},
                {"name": "frontend", "url": "http://localhost:3000", "port": 3000},
                {"name": "redis", "port": 6379},
                {"name": "postgres", "port": 5432}
            ],
            "alerts": {
                "cpu_threshold": 80,
                "memory_threshold": 80,
                "disk_threshold": 90,
                "response_time_threshold": 5.0
            },
            "check_interval": 60
        }
        
        config_file = Path(path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return default_config
    
    async def check_system_resources(self):
        """Check system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.metrics['system'] = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available': memory.available / (1024**3),  # GB
            'disk_percent': disk.percent,
            'disk_free': disk.free / (1024**3),  # GB
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check thresholds
        alerts = []
        if cpu_percent > self.config['alerts']['cpu_threshold']:
            alerts.append(f"High CPU usage: {cpu_percent}%")
        
        if memory.percent > self.config['alerts']['memory_threshold']:
            alerts.append(f"High memory usage: {memory.percent}%")
        
        if disk.percent > self.config['alerts']['disk_threshold']:
            alerts.append(f"High disk usage: {disk.percent}%")
        
        return alerts
    
    async def check_service_health(self, session: aiohttp.ClientSession, service: Dict) -> Dict:
        """Check individual service health"""
        result = {
            'name': service['name'],
            'status': 'unknown',
            'response_time': None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check port availability
        if 'port' in service:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            port_open = sock.connect_ex(('localhost', service['port'])) == 0
            sock.close()
            
            if not port_open and 'url' not in service:
                result['status'] = 'down'
                return result
        
        # Check HTTP endpoint
        if 'url' in service:
            try:
                start_time = asyncio.get_event_loop().time()
                async with session.get(service['url'], timeout=5) as response:
                    response_time = asyncio.get_event_loop().time() - start_time
                    
                    result['status'] = 'up' if response.status == 200 else 'degraded'
                    result['response_time'] = round(response_time, 3)
                    result['status_code'] = response.status
                    
                    # Check response time threshold
                    if response_time > self.config['alerts']['response_time_threshold']:
                        result['slow'] = True
                        
            except Exception as e:
                result['status'] = 'down'
                result['error'] = str(e)
        
        return result
    
    async def check_all_services(self):
        """Check all services"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for service in self.config['services']:
                tasks.append(self.check_service_health(session, service))
            
            results = await asyncio.gather(*tasks)
            self.metrics['services'] = results
    
    async def check_database(self):
        """Check database connectivity and performance"""
        try:
            import asyncpg
            
            conn = await asyncpg.connect(
                host='localhost',
                port=5432,
                database='ai_interview',
                user='ai_user',
                password='ai_password'
            )
            
            # Check connection
            version = await conn.fetchval('SELECT version()')
            
            # Check active connections
            connections = await conn.fetchval('SELECT count(*) FROM pg_stat_activity')
            
            # Check database size
            size = await conn.fetchval("""
                SELECT pg_database_size('ai_interview') / (1024*1024*1024) as size_gb
            """)
            
            await conn.close()
            
            self.metrics['database'] = {
                'status': 'up',
                'version': version.split()[1],
                'active_connections': connections,
                'size_gb': round(size, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.metrics['database'] = {
                'status': 'down',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_redis(self):
        """Check Redis connectivity"""
        try:
            import redis.asyncio as redis
            
            client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )
            
            # Check connection
            pong = await client.ping()
            
            # Get info
            info = await client.info()
            
            await client.close()
            
            self.metrics['redis'] = {
                'status': 'up' if pong else 'down',
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', ''),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.metrics['redis'] = {
                'status': 'down',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def run_checks(self):
        """Run all monitoring checks"""
        logger.info("Running system monitoring checks...")
        
        # Check system resources
        system_alerts = await self.check_system_resources()
        
        # Check services
        await self.check_all_services()
        
        # Check database
        await self.check_database()
        
        # Check Redis
        await self.check_redis()
        
        # Combine alerts
        all_alerts = system_alerts.copy()
        
        for service in self.metrics.get('services', []):
            if service['status'] == 'down':
                all_alerts.append(f"Service {service['name']} is down")
            elif service.get('slow'):
                all_alerts.append(f"Service {service['name']} is slow ({service['response_time']}s)")
        
        if all_alerts:
            logger.warning(f"Alerts detected: {len(all_alerts)}")
            for alert in all_alerts:
                logger.warning(f"  - {alert}")
        else:
            logger.info("All systems healthy ✓")
        
        self.metrics['alerts'] = all_alerts
        self.metrics['timestamp'] = datetime.utcnow().isoformat()
        
        return self.metrics
    
    async def continuous_monitor(self):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {self.config['check_interval']}s)")
        
        while True:
            try:
                metrics = await self.run_checks()
                
                # Save metrics
                self.save_metrics(metrics)
                
                # Send alerts if needed
                if metrics['alerts']:
                    await self.send_alerts(metrics['alerts'])
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(self.config['check_interval'])
    
    def save_metrics(self, metrics: Dict):
        """Save metrics to file"""
        metrics_file = Path("monitoring/metrics.json")
        metrics_file.parent.mkdir(exist_ok=True)
        
        # Load existing metrics
        existing = []
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                existing = json.load(f)
        
        # Add new metrics
        existing.append(metrics)
        
        # Keep only last 1000 entries
        if len(existing) > 1000:
            existing = existing[-1000:]
        
        with open(metrics_file, 'w') as f:
            json.dump(existing, f, indent=2)
    
    async def send_alerts(self, alerts: List[str]):
        """Send alerts to configured channels"""
        # Slack webhook
        slack_webhook = self.config.get('slack_webhook')
        if slack_webhook:
            async with aiohttp.ClientSession() as session:
                await session.post(slack_webhook, json={
                    'text': f"🚨 *System Alerts*\n" + "\n".join(f"• {alert}" for alert in alerts)
                })
        
        # Email alerts
        email_config = self.config.get('email')
        if email_config:
            # Send email via SMTP
            pass

async def main():
    parser = argparse.ArgumentParser(description="System monitoring utility")
    parser.add_argument('--continuous', '-c', action='store_true', help="Run continuous monitoring")
    parser.add_argument('--interval', '-i', type=int, default=60, help="Check interval in seconds")
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    if args.continuous:
        monitor.config['check_interval'] = args.interval
        await monitor.continuous_monitor()
    else:
        metrics = await monitor.run_checks()
        print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    asyncio.run(main())