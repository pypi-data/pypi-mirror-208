---
-- Migrate Scan Table:
--  ID becomes GUID
---

PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS scan_id_mapping;
CREATE TABLE scan_id_mapping (id INTEGER, uuid VARCHAR);
INSERT INTO scan_id_mapping SELECT id, shortuuid() FROM scan;

DROP TABLE IF EXISTS scan_new;
CREATE TABLE scan_new (
        id VARCHAR NOT NULL PRIMARY KEY,
        scantype_id INTEGER, 
        name VARCHAR, 
        created TIMESTAMP, 
        modified TIMESTAMP, 
        snapshot_id VARCHAR, 
        start_time DATETIME, 
        end_time DATETIME, 
        status VARCHAR(9), 
        log VARCHAR, 
        meta JSON,
        FOREIGN KEY(scantype_id) REFERENCES scantype (id), 
        FOREIGN KEY(snapshot_id) REFERENCES snapshot (id)
);

INSERT INTO scan_new
    SELECT m.uuid as id, scantype_id, name, created, modified, snapshot_id, 
           start_time, end_time, status, log, meta
    FROM scan s
    LEFT JOIN scan_id_mapping m USING (id);

--

DROP TABLE IF EXISTS issueaggregate_new;
CREATE TABLE issueaggregate_new (
    id INTEGER NOT NULL, 
    scan_id VARCHAR, 
    issue_name VARCHAR, 
    feature_count FLOAT, 
    segment_count FLOAT, 
    issues_tested_count FLOAT, 
    issues_found_count FLOAT, 
    metric VARCHAR, 
    measure VARCHAR, 
    lower_threshold FLOAT, 
    upper_threshold FLOAT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(scan_id) REFERENCES scan (id)
);

INSERT INTO issueaggregate_new
    SELECT  i.id, m.uuid, issue_name, feature_count, segment_count, issues_tested_count,
            issues_found_count, metric, measure, lower_threshold, upper_threshold
    FROM issueaggregate as i
    LEFT JOIN scan_id_mapping as m ON (i.scan_id = m.id);
--
DROP TABLE IF EXISTS segment_new;
CREATE TABLE segment_new (
    id INTEGER NOT NULL,
    parent_id INTEGER,
    scan_id VARCHAR,
    name VARCHAR,
    business_rule VARCHAR,
    volume FLOAT,
    volume_percent_total FLOAT, 
    metric_tag TEXT DEFAULT '',
    PRIMARY KEY (id),
    FOREIGN KEY(scan_id) REFERENCES scan (id),
    FOREIGN KEY(parent_id) REFERENCES segment (id)
);

INSERT INTO segment_new
    SELECT s.id, parent_id, m.uuid, name, business_rule, volume, volume_percent_total,
           metric_tag
    FROM segment s
    LEFT JOIN scan_id_mapping m ON (s.scan_id = m.id);
--
DROP TABLE IF EXISTS issue_new;
CREATE TABLE issue_new (
    id INTEGER NOT NULL, 
    scan_id VARCHAR,
    segment_id INTEGER, 
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
    SELECT i.id, m.uuid, segment_id, issue, feature, metric, metric_value, 
           measure, measure_value, lower_threshold, upper_threshold, value, record
    FROM issue i
    LEFT JOIN scan_id_mapping m ON (i.scan_id = m.id);

--

DROP TABLE IF EXISTS metric_new;
CREATE TABLE metric_new (
    id INTEGER NOT NULL, 
    scan_id VARCHAR, 
    name VARCHAR, 
    value FLOAT, 
    privileged FLOAT, 
    unprivileged FLOAT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(scan_id) REFERENCES scan (id)
);

INSERT INTO metric_new
    SELECT metric.id, uuid, name, value, privileged, unprivileged
    FROM metric
    LEFT JOIN scan_id_mapping m ON (metric.scan_id = m.id);

--

DROP TABLE IF EXISTS scanconfig_new;

CREATE TABLE scanconfig_new (
    id INTEGER NOT NULL, 
    scan_id VARCHAR, 
    config JSON, 
    PRIMARY KEY (id), 
    FOREIGN KEY(scan_id) REFERENCES scan (id)
);

INSERT INTO scanconfig_new
    SELECT s.id, m.uuid, config
    FROM scanconfig s
    LEFT JOIN scan_id_mapping m ON (s.scan_id = m.id);

--

-- ScanResult is related but unused.

DROP TABLE IF EXISTS scanresult;

-- Now move all tables into place
DROP TABLE scan;
ALTER TABLE scan_new RENAME TO scan;

DROP TABLE issueaggregate;
ALTER TABLE issueaggregate_new RENAME TO issueaggregate;

DROP TABLE segment;
ALTER TABLE segment_new RENAME TO segment;

DROP TABLE issue;
ALTER TABLE issue_new RENAME TO issue;

DROP TABLE metric;
ALTER TABLE metric_new RENAME TO metric;

DROP TABLE scanconfig;
ALTER TABLE scanconfig_new RENAME TO scanconfig;


-- Finally remove the mapping table
DROP TABLE scan_id_mapping;


PRAGMA foreign_keys=on;