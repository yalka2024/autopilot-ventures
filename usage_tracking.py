
            import sqlite3
            import json
            from datetime import datetime
            
            class UsageTracker:
                def __init__(self):
                    self.db_path = "usage_analytics.db"
                    self.init_tracking_database()
                
                def init_tracking_database(self):
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS usage_events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            customer_id TEXT NOT NULL,
                            event_type TEXT NOT NULL,
                            event_data TEXT,
                            timestamp TEXT,
                            metadata TEXT
                        )
                    ''')
                    
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS daily_metrics (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT NOT NULL,
                            metric_name TEXT NOT NULL,
                            metric_value REAL,
                            customer_id TEXT
                        )
                    ''')
                    
                    conn.commit()
                    conn.close()
                
                def track_event(self, customer_id, event_type, event_data=None):
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO usage_events (customer_id, event_type, event_data, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (customer_id, event_type, json.dumps(event_data), datetime.now().isoformat()))
                    
                    conn.commit()
                    conn.close()
                
                def get_daily_metrics(self, customer_id=None):
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    if customer_id:
                        cursor.execute('''
                            SELECT * FROM daily_metrics WHERE customer_id = ? ORDER BY date DESC
                        ''', (customer_id,))
                    else:
                        cursor.execute('''
                            SELECT * FROM daily_metrics ORDER BY date DESC
                        ''')
                    
                    results = cursor.fetchall()
                    conn.close()
                    return results
            