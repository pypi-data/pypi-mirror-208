---
-- Version 12 - Correct column type segment_id on issue table.
---
PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS issue_new;
CREATE TABLE issue_new (
    id VARCHAR NOT NULL, 
    scan_id VARCHAR,
    segment_id VARCHAR,   -- This was left as int previously :|
    issue VARCHAR, 
    feature VARCHAR, 
    metric VARCHAR, 
    metric_value FLOAT, 
    measure VARCHAR, 
    measure_value FLOAT, 
    lower_threshold FLOAT, 
    upper_threshold FLOAT, 
    value TEXT DEFAULT '', 
    record TEXT DEFAULT '', 
    PRIMARY KEY (id), 
    FOREIGN KEY(scan_id) REFERENCES scan (id), 
    FOREIGN KEY(segment_id) REFERENCES segment (id)
);

INSERT INTO issue_new
    SELECT  id, scan_id, segment_id, issue, feature, metric, metric_value,
            measure, measure_value, lower_threshold, upper_threshold, value,
            record
    FROM issue;

DROP TABLE issue;
ALTER TABLE issue_new RENAME TO issue;

PRAGMA foreign_keys=on;