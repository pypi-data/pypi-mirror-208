---
-- Schame change v9
-- Change snapshot and scans id to guid
---

PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS snapshot_id_mapping;
CREATE TABLE snapshot_id_mapping (id INTEGER, uuid VARCHAR);
INSERT INTO snapshot_id_mapping SELECT id, shortuuid() FROM snapshot;

DROP TABLE IF EXISTS snapshot_migrate;

CREATE TABLE IF NOT EXISTS snapshot_migrate (
        id VARCHAR PRIMARY KEY,
        created TIMESTAMP,
        name VARCHAR,
        project_id VARCHAR,
        model_id INTEGER,
        data_id INTEGER,
        comparison_data_id INTEGER,
        stage VARCHAR(14),
        status VARCHAR(7),
        significant_features VARCHAR,
        meta JSON,
        CONSTRAINT FK_snapshot_data FOREIGN KEY (comparison_data_id) REFERENCES "data"(id),
        CONSTRAINT FK_snapshot_data_2 FOREIGN KEY (data_id) REFERENCES "data"(id),
        CONSTRAINT FK_snapshot_model_3 FOREIGN KEY (model_id) REFERENCES model(id),
        CONSTRAINT FK_snapshot_project_4 FOREIGN KEY (project_id) REFERENCES "project"(id)
);

INSERT INTO snapshot_migrate
    SELECT  uuid, created, name, project_id, model_id, data_id, comparison_data_id,
            stage, status, significant_features, meta
    FROM snapshot
    LEFT JOIN snapshot_id_mapping USING (id);

-- Migrate scan table
DROP TABLE IF EXISTS scan_migrate;

CREATE TABLE scan_migrate (
        id INTEGER NOT NULL,
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
        PRIMARY KEY (id), 
        FOREIGN KEY(scantype_id) REFERENCES scantype (id), 
        FOREIGN KEY(snapshot_id) REFERENCES snapshot (id)
);

INSERT INTO scan_migrate
    SELECT  scan.id, scantype_id, name, created, modified,
            map.uuid, start_time, end_time, status, log, meta
    FROM scan
    LEFT join snapshot_id_mapping AS map ON (scan.snapshot_id = map.id);

-- Settings table is unused. Let's just remove it.

DROP TABLE IF EXISTS settings;

-- MOVE NEW TABLES INTO PLACE
DROP TABLE snapshot;
ALTER TABLE snapshot_migrate RENAME TO snapshot;

DROP TABLE scan;
ALTER TABLE scan_migrate RENAME TO scan;

-- DROP mapping table
DROP TABLE snapshot_id_mapping;

PRAGMA foreign_keys=on;