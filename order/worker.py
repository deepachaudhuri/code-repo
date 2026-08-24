#!/usr/bin/env python3
"""
Order Processing Service

Background worker for e-commerce checkout and order fulfillment tasks.
"""

import os
import time
import logging
import socket
from datetime import datetime

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('order')

HOSTNAME = socket.gethostname()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
ORDER_WORKER_ID = os.getenv('ORDER_WORKER_ID', 'order-worker-1')
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', 30))

class OrderWorker:
    def __init__(self):
        self.running = True
        self.orders_processed = 0
        self.errors = 0
        self.start_time = datetime.utcnow()

        logger.info(f"Order worker initialized: {ORDER_WORKER_ID}")
        logger.info(f"Environment: {ENVIRONMENT}")
        logger.info(f"Hostname: {HOSTNAME}")

    def process_order(self):
        try:
            order_id = f"ord-{self.orders_processed + 1}"
            logger.info(f"Processing order: {order_id}")
            time.sleep(2)
            self.orders_processed += 1
            logger.info(f"Completed order: {order_id}")
        except Exception as e:
            self.errors += 1
            logger.error(f"Error processing order: {str(e)}")

    def health_check(self):
        try:
            with open('/tmp/worker_healthy', 'w') as f:
                f.write(f"OK - {datetime.utcnow().isoformat()}\n")
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")

    def log_stats(self):
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        logger.info(f"Stats - Orders processed: {self.orders_processed}, Errors: {self.errors}, Uptime: {uptime}s")

    def run(self):
        logger.info(f"Order worker started: {ORDER_WORKER_ID}")
        heartbeat_counter = 0

        try:
            while self.running:
                self.process_order()
                heartbeat_counter += 1
                if heartbeat_counter % 5 == 0:
                    self.health_check()
                    self.log_stats()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Order worker interrupted")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            logger.info(f"Order worker shutdown: {ORDER_WORKER_ID}")
            logger.info(f"Summary - Processed: {self.orders_processed}, Errors: {self.errors}")

if __name__ == '__main__':
    worker = OrderWorker()
    worker.run()
