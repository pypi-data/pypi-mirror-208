---
--- Version 11 - moving final tables to guids
---

PRAGMA foreign_keys=off;

-- chartsubmission ???
-- data - Hash should be primary key.
-- datafeatureprofile - Hash should be primary key.

-- issue

DROP TABLE IF EXISTS mapping;
CREATE TABLE mapping (id INTEGER, uuid VARCHAR);
INSERT INTO mapping SELECT id, shortuuid() FROM issue;

DROP TABLE IF EXISTS issue_new;
CREATE TABLE issue_new (
    id VARCHAR NOT NULL, 
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
    SELECT  uuid, scan_id, segment_id, issue, feature, metric, metric_value,
            measure, measure_value, lower_threshold, upper_threshold, value,
            record
    FROM issue
    LEFT JOIN mapping USING (id);

DROP TABLE mapping;
DROP TABLE issue;
ALTER TABLE issue_new RENAME TO issue;

-- issueaggregate -- MIGRATE

DROP TABLE IF EXISTS issueaggregate_new;
CREATE TABLE issueaggregate_new (
    id VARCHAR NOT NULL, 
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

DROP TABLE IF EXISTS mapping;
CREATE TABLE mapping (id INTEGER, uuid VARCHAR);
INSERT INTO mapping SELECT id, shortuuid() FROM issueaggregate;

INSERT INTO issueaggregate_new 
    SELECT  uuid, scan_id, issue_name, feature_count, segment_count,
            issues_tested_count, issues_found_count, metric, measure,
            lower_threshold, upper_threshold
    FROM issueaggregate
    LEFT JOIN mapping USING (id);

DROP TABLE mapping;
DROP TABLE issueaggregate;
ALTER TABLE issueaggregate_new RENAME TO issueaggregate;


-- metric
DROP TABLE IF EXISTS mapping;
CREATE TABLE mapping (id INTEGER, uuid VARCHAR);
INSERT INTO mapping SELECT id, shortuuid() FROM metric;

DROP TABLE IF EXISTS metric_new;

CREATE TABLE metric_new (
    id VARCHAR NOT NULL, 
    scan_id VARCHAR, 
    name VARCHAR, 
    value FLOAT, 
    privileged FLOAT, 
    unprivileged FLOAT, 
    PRIMARY KEY (id), 
    FOREIGN KEY(scan_id) REFERENCES scan (id)
);

INSERT INTO metric_new
    SELECT uuid, scan_id, name, value, privileged, unprivileged
    FROM metric
    LEFT JOIN mapping USING (id);

DROP TABLE metric;
DROP TABLE mapping;
ALTER TABLE metric_new RENAME TO metric;

-- model
DROP TABLE IF EXISTS mapping;
CREATE TABLE mapping (id INTEGER, uuid VARCHAR);
INSERT INTO mapping SELECT id, shortuuid() FROM model;

DROP TABLE IF EXISTS model_new;
CREATE TABLE model_new (
    id VARCHAR NOT NULL, 
    architecture VARCHAR, 
    label VARCHAR, 
    created TIMESTAMP, 
    PRIMARY KEY (id)
);

INSERT INTO model_new
    SELECT uuid, architecture, label, created
    FROM model
    LEFT JOIN mapping USING (id);

-- Update Snapshot Table model ids.

ALTER TABLE snapshot ADD COLUMN new_model_id VARCHAR;
UPDATE snapshot
    SET new_model_id=(SELECT uuid FROM mapping WHERE id=snapshot.id);
    
-- This only works as sqlite is liberal with the data types.
-- We can't change the column type, but can happily insert
-- varchar into a declared INT column :(
UPDATE snapshot SET model_id = new_model_id;
-- ALTER TABLE snapshot DROP COLUMN new_model_id;

DROP TABLE model;
DROP TABLE mapping;

ALTER TABLE model_new RENAME TO model;

-- scanconfig 
DROP TABLE IF EXISTS mapping;
CREATE TABLE mapping (id INTEGER, uuid VARCHAR);
INSERT INTO mapping SELECT id, shortuuid() FROM scanconfig;

DROP TABLE IF EXISTS scanconfig_new;
CREATE TABLE scanconfig_new (
    id VARCHAR NOT NULL, 
    scan_id VARCHAR, 
    config JSON, 
    PRIMARY KEY (id), 
    FOREIGN KEY(scan_id) REFERENCES scan (id)
);

INSERT INTO scanconfig_new
    SELECT m.uuid, scan_id, config
    FROM scanconfig
    LEFT JOIN mapping m USING (id);

DROP TABLE mapping;
DROP TABLE scanconfig;
ALTER TABLE scanconfig_new RENAME TO scanconfig;

-- segment
-- Segment Table
DROP TABLE IF EXISTS mapping;
CREATE TABLE mapping (id INTEGER, uuid VARCHAR);
INSERT INTO mapping SELECT id, shortuuid() FROM segment;

DROP TABLE IF EXISTS segment_new;
CREATE TABLE segment_new (
    id VARCHAR NOT NULL,
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
    SELECT  uuid, parent_id, scan_id, name, business_rule, volume, volume_percent_total,
            metric_tag
    FROM segment
    LEFT JOIN mapping USING (id);

DROP TABLE segment;
ALTER TABLE segment_new RENAME TO segment;

-- issue.segment_id
ALTER TABLE issue ADD COLUMN new_segment_id;
UPDATE issue SET new_segment_id = (SELECT uuid FROM mapping WHERE issue.segment_id = mapping.id);
UPDATE issue SET segment_id = new_segment_id;
-- ALTER TABLE issue DROP COLUMN new_segment_id;


PRAGMA foreign_keys=on;