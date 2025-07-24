"""
BigQuery Analytics Pipeline for AutoPilot Ventures
Pipes request logs and business metrics to BigQuery for analytics
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import time

# BigQuery imports
try:
    from google.cloud import bigquery
    from google.cloud.bigquery import SchemaField
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    logging.warning("BigQuery not available. Install: pip install google-cloud-bigquery")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RequestLog:
    """Request log entry for analytics"""
    timestamp: str
    request_id: str
    method: str
    path: str
    status_code: int
    response_time_ms: float
    user_agent: str
    ip_address: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    business_id: Optional[str] = None
    language: str = "en"
    error_message: Optional[str] = None

@dataclass
class BusinessMetric:
    """Business metric for analytics"""
    timestamp: str
    business_id: str
    metric_name: str
    metric_value: float
    metric_unit: str
    category: str
    tags: Dict[str, str] = None

@dataclass
class SystemMetric:
    """System metric for analytics"""
    timestamp: str
    metric_name: str
    metric_value: float
    metric_unit: str
    component: str
    tags: Dict[str, str] = None

class BigQueryAnalytics:
    def __init__(self, project_id: str = "autopilot-ventures-core-466708"):
        self.project_id = project_id
        self.client = None
        self.dataset_id = "autopilot_ventures_analytics"
        self.request_logs_table = "request_logs"
        self.business_metrics_table = "business_metrics"
        self.system_metrics_table = "system_metrics"
        self.batch_size = 1000
        self.batch_timeout = 60  # seconds
        
        # Initialize BigQuery client
        self._init_client()
        
        # Batch processing queues
        self.request_logs_queue: List[RequestLog] = []
        self.business_metrics_queue: List[BusinessMetric] = []
        self.system_metrics_queue: List[SystemMetric] = []
        
        # Start background processing
        self._start_background_processing()
    
    def _init_client(self):
        """Initialize BigQuery client"""
        if not BIGQUERY_AVAILABLE:
            logger.warning("BigQuery not available - analytics disabled")
            return
        
        try:
            # Try to use service account credentials
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = bigquery.Client(project=self.project_id, credentials=credentials)
            else:
                # Use default credentials
                self.client = bigquery.Client(project=self.project_id)
            
            logger.info(f"✅ BigQuery client initialized for project: {self.project_id}")
            self._create_tables()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize BigQuery client: {e}")
            self.client = None
    
    def _create_tables(self):
        """Create BigQuery tables if they don't exist"""
        if not self.client:
            return
        
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            
            # Create dataset if it doesn't exist
            try:
                self.client.get_dataset(dataset_ref)
            except Exception:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                self.client.create_dataset(dataset)
                logger.info(f"✅ Created dataset: {self.dataset_id}")
            
            # Create request logs table
            self._create_request_logs_table()
            
            # Create business metrics table
            self._create_business_metrics_table()
            
            # Create system metrics table
            self._create_system_metrics_table()
            
        except Exception as e:
            logger.error(f"❌ Failed to create BigQuery tables: {e}")
    
    def _create_request_logs_table(self):
        """Create request logs table"""
        if not self.client:
            return
        
        schema = [
            SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            SchemaField("request_id", "STRING", mode="REQUIRED"),
            SchemaField("method", "STRING", mode="REQUIRED"),
            SchemaField("path", "STRING", mode="REQUIRED"),
            SchemaField("status_code", "INTEGER", mode="REQUIRED"),
            SchemaField("response_time_ms", "FLOAT", mode="REQUIRED"),
            SchemaField("user_agent", "STRING", mode="NULLABLE"),
            SchemaField("ip_address", "STRING", mode="NULLABLE"),
            SchemaField("user_id", "STRING", mode="NULLABLE"),
            SchemaField("session_id", "STRING", mode="NULLABLE"),
            SchemaField("business_id", "STRING", mode="NULLABLE"),
            SchemaField("language", "STRING", mode="REQUIRED"),
            SchemaField("error_message", "STRING", mode="NULLABLE"),
        ]
        
        table_ref = self.client.dataset(self.dataset_id).table(self.request_logs_table)
        table = bigquery.Table(table_ref, schema=schema)
        
        try:
            self.client.get_table(table)
            logger.info(f"✅ Request logs table exists: {self.request_logs_table}")
        except Exception:
            self.client.create_table(table)
            logger.info(f"✅ Created request logs table: {self.request_logs_table}")
    
    def _create_business_metrics_table(self):
        """Create business metrics table"""
        if not self.client:
            return
        
        schema = [
            SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            SchemaField("business_id", "STRING", mode="REQUIRED"),
            SchemaField("metric_name", "STRING", mode="REQUIRED"),
            SchemaField("metric_value", "FLOAT", mode="REQUIRED"),
            SchemaField("metric_unit", "STRING", mode="REQUIRED"),
            SchemaField("category", "STRING", mode="REQUIRED"),
            SchemaField("tags", "JSON", mode="NULLABLE"),
        ]
        
        table_ref = self.client.dataset(self.dataset_id).table(self.business_metrics_table)
        table = bigquery.Table(table_ref, schema=schema)
        
        try:
            self.client.get_table(table)
            logger.info(f"✅ Business metrics table exists: {self.business_metrics_table}")
        except Exception:
            self.client.create_table(table)
            logger.info(f"✅ Created business metrics table: {self.business_metrics_table}")
    
    def _create_system_metrics_table(self):
        """Create system metrics table"""
        if not self.client:
            return
        
        schema = [
            SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            SchemaField("metric_name", "STRING", mode="REQUIRED"),
            SchemaField("metric_value", "FLOAT", mode="REQUIRED"),
            SchemaField("metric_unit", "STRING", mode="REQUIRED"),
            SchemaField("component", "STRING", mode="REQUIRED"),
            SchemaField("tags", "JSON", mode="NULLABLE"),
        ]
        
        table_ref = self.client.dataset(self.dataset_id).table(self.system_metrics_table)
        table = bigquery.Table(table_ref, schema=schema)
        
        try:
            self.client.get_table(table)
            logger.info(f"✅ System metrics table exists: {self.system_metrics_table}")
        except Exception:
            self.client.create_table(table)
            logger.info(f"✅ Created system metrics table: {self.system_metrics_table}")
    
    def _start_background_processing(self):
        """Start background processing for batch uploads"""
        if not self.client:
            return
        
        async def background_processor():
            while True:
                try:
                    # Process request logs
                    if len(self.request_logs_queue) >= self.batch_size:
                        await self._upload_request_logs_batch()
                    
                    # Process business metrics
                    if len(self.business_metrics_queue) >= self.batch_size:
                        await self._upload_business_metrics_batch()
                    
                    # Process system metrics
                    if len(self.system_metrics_queue) >= self.batch_size:
                        await self._upload_system_metrics_batch()
                    
                    # Wait before next check
                    await asyncio.sleep(10)
                    
                except Exception as e:
                    logger.error(f"❌ Background processing error: {e}")
                    await asyncio.sleep(30)
        
        # Start background task
        asyncio.create_task(background_processor())
        logger.info("✅ Started BigQuery background processing")
    
    def log_request(self, request_log: RequestLog):
        """Log a request for analytics"""
        if not self.client:
            return
        
        self.request_logs_queue.append(request_log)
        
        # Upload immediately if queue is full
        if len(self.request_logs_queue) >= self.batch_size:
            asyncio.create_task(self._upload_request_logs_batch())
    
    def log_business_metric(self, metric: BusinessMetric):
        """Log a business metric for analytics"""
        if not self.client:
            return
        
        self.business_metrics_queue.append(metric)
        
        # Upload immediately if queue is full
        if len(self.business_metrics_queue) >= self.batch_size:
            asyncio.create_task(self._upload_business_metrics_batch())
    
    def log_system_metric(self, metric: SystemMetric):
        """Log a system metric for analytics"""
        if not self.client:
            return
        
        self.system_metrics_queue.append(metric)
        
        # Upload immediately if queue is full
        if len(self.system_metrics_queue) >= self.batch_size:
            asyncio.create_task(self._upload_system_metrics_batch())
    
    async def _upload_request_logs_batch(self):
        """Upload batch of request logs to BigQuery"""
        if not self.client or not self.request_logs_queue:
            return
        
        try:
            batch = self.request_logs_queue[:self.batch_size]
            self.request_logs_queue = self.request_logs_queue[self.batch_size:]
            
            # Convert to BigQuery format
            rows = []
            for log in batch:
                row = {
                    'timestamp': log.timestamp,
                    'request_id': log.request_id,
                    'method': log.method,
                    'path': log.path,
                    'status_code': log.status_code,
                    'response_time_ms': log.response_time_ms,
                    'user_agent': log.user_agent,
                    'ip_address': log.ip_address,
                    'user_id': log.user_id,
                    'session_id': log.session_id,
                    'business_id': log.business_id,
                    'language': log.language,
                    'error_message': log.error_message,
                }
                rows.append(row)
            
            # Upload to BigQuery
            table_ref = self.client.dataset(self.dataset_id).table(self.request_logs_table)
            errors = self.client.insert_rows_json(table_ref, rows)
            
            if errors:
                logger.error(f"❌ BigQuery upload errors: {errors}")
            else:
                logger.info(f"✅ Uploaded {len(rows)} request logs to BigQuery")
                
        except Exception as e:
            logger.error(f"❌ Failed to upload request logs batch: {e}")
            # Put items back in queue for retry
            self.request_logs_queue.extend(batch)
    
    async def _upload_business_metrics_batch(self):
        """Upload batch of business metrics to BigQuery"""
        if not self.client or not self.business_metrics_queue:
            return
        
        try:
            batch = self.business_metrics_queue[:self.batch_size]
            self.business_metrics_queue = self.business_metrics_queue[self.batch_size:]
            
            # Convert to BigQuery format
            rows = []
            for metric in batch:
                row = {
                    'timestamp': metric.timestamp,
                    'business_id': metric.business_id,
                    'metric_name': metric.metric_name,
                    'metric_value': metric.metric_value,
                    'metric_unit': metric.metric_unit,
                    'category': metric.category,
                    'tags': json.dumps(metric.tags) if metric.tags else None,
                }
                rows.append(row)
            
            # Upload to BigQuery
            table_ref = self.client.dataset(self.dataset_id).table(self.business_metrics_table)
            errors = self.client.insert_rows_json(table_ref, rows)
            
            if errors:
                logger.error(f"❌ BigQuery upload errors: {errors}")
            else:
                logger.info(f"✅ Uploaded {len(rows)} business metrics to BigQuery")
                
        except Exception as e:
            logger.error(f"❌ Failed to upload business metrics batch: {e}")
            # Put items back in queue for retry
            self.business_metrics_queue.extend(batch)
    
    async def _upload_system_metrics_batch(self):
        """Upload batch of system metrics to BigQuery"""
        if not self.client or not self.system_metrics_queue:
            return
        
        try:
            batch = self.system_metrics_queue[:self.batch_size]
            self.system_metrics_queue = self.system_metrics_queue[self.batch_size:]
            
            # Convert to BigQuery format
            rows = []
            for metric in batch:
                row = {
                    'timestamp': metric.timestamp,
                    'metric_name': metric.metric_name,
                    'metric_value': metric.metric_value,
                    'metric_unit': metric.metric_unit,
                    'component': metric.component,
                    'tags': json.dumps(metric.tags) if metric.tags else None,
                }
                rows.append(row)
            
            # Upload to BigQuery
            table_ref = self.client.dataset(self.dataset_id).table(self.system_metrics_table)
            errors = self.client.insert_rows_json(table_ref, rows)
            
            if errors:
                logger.error(f"❌ BigQuery upload errors: {errors}")
            else:
                logger.info(f"✅ Uploaded {len(rows)} system metrics to BigQuery")
                
        except Exception as e:
            logger.error(f"❌ Failed to upload system metrics batch: {e}")
            # Put items back in queue for retry
            self.system_metrics_queue.extend(batch)
    
    async def flush_all(self):
        """Flush all pending data to BigQuery"""
        if not self.client:
            return
        
        logger.info("🔄 Flushing all pending data to BigQuery...")
        
        await self._upload_request_logs_batch()
        await self._upload_business_metrics_batch()
        await self._upload_system_metrics_batch()
        
        logger.info("✅ All data flushed to BigQuery")
    
    def get_analytics_query(self, query_type: str = "request_analysis") -> str:
        """Get sample analytics queries"""
        queries = {
            "request_analysis": f"""
                SELECT 
                    DATE(timestamp) as date,
                    path,
                    method,
                    status_code,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(*) as request_count,
                    COUNTIF(status_code >= 400) as error_count
                FROM `{self.project_id}.{self.dataset_id}.{self.request_logs_table}`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                GROUP BY date, path, method, status_code
                ORDER BY date DESC, request_count DESC
            """,
            
            "business_performance": f"""
                SELECT 
                    business_id,
                    metric_name,
                    AVG(metric_value) as avg_value,
                    MAX(metric_value) as max_value,
                    MIN(metric_value) as min_value,
                    COUNT(*) as data_points
                FROM `{self.project_id}.{self.dataset_id}.{self.business_metrics_table}`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
                GROUP BY business_id, metric_name
                ORDER BY business_id, metric_name
            """,
            
            "system_health": f"""
                SELECT 
                    component,
                    metric_name,
                    AVG(metric_value) as avg_value,
                    MAX(metric_value) as max_value,
                    MIN(metric_value) as min_value
                FROM `{self.project_id}.{self.dataset_id}.{self.system_metrics_table}`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
                GROUP BY component, metric_name
                ORDER BY component, metric_name
            """
        }
        
        return queries.get(query_type, queries["request_analysis"])

# Global BigQuery analytics instance
bigquery_analytics = BigQueryAnalytics() 