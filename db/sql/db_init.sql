CREATE TABLE IF NOT EXISTS net_samples (
    timestamp REAL,
    adapter TEXT,
    down_mbps REAL,
    up_mbps REAL,
    rx_bytes INTEGER,
    tx_bytes INTEGER
);

CREATE INDEX IF NOT EXISTS idx_net_time ON net_samples (timestamp);