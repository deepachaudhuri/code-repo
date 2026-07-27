#!/usr/bin/env python3
"""
Worker Service

Background job processor for scheduled and async tasks.
"""

import os
import time
import logging
import socket
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('worker')

# Get environment info
HOSTNAME = socket.gethostname()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
WORKER_ID = os.getenv('WORKER_ID', 'worker-1')
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', 30))

class Worker:
    def __init__(self):
        self.running = True
        self.tasks_processed = 0
        self.errors = 0
        self.start_time = datetime.utcnow()
        
        logger.info(f"Worker initialized: {WORKER_ID}")
        logger.info(f"Environment: {ENVIRONMENT}")
        logger.info(f"Hostname: {HOSTNAME}")
    
    def process_job(self):
        """Process a single job"""
        try:
            # Simulate job processing
            job_name = f"job-{self.tasks_processed}"
            logger.info(f"Processing: {job_name}")
            
            # Simulate work
            time.sleep(2)
            
            self.tasks_processed += 1
            logger.info(f"Completed: {job_name}")
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Error processing job: {str(e)}")
    
    def health_check(self):
        """Write health check file"""
        try:
            with open('/tmp/worker_healthy', 'w') as f:
                f.write(f"OK - {datetime.utcnow().isoformat()}\n")
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
    
    def log_stats(self):
        """Log worker statistics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        logger.info(f"Stats - Processed: {self.tasks_processed}, Errors: {self.errors}, Uptime: {uptime}s")
    
    def run(self):
        """Main worker loop"""
        logger.info(f"Worker started: {WORKER_ID}")
        
        heartbeat_counter = 0
        
        try:
            while self.running:
                # Process job
                self.process_job()
                
                # Periodic health check
                heartbeat_counter += 1
                if heartbeat_counter % 5 == 0:
                    self.health_check()
                    self.log_stats()
                
                # Wait before next job
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Worker interrupted")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            logger.info(f"Worker shutdown: {WORKER_ID}")
            logger.info(f"Summary - Processed: {self.tasks_processed}, Errors: {self.errors}")

if __name__ == '__main__':
    worker = Worker()
    worker.run()
