--
-- Schema 8: Project id to varchar uuid
--

PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS usercharts_new;

CREATE TABLE usercharts_new (
    owner_id INTEGER NOT NULL,
    project_id VARCHAR NOT NULL,
    settings JSON,
    PRIMARY KEY (owner_id, project_id)
);

INSERT INTO usercharts_new (owner_id, project_id, settings)
    SELECT owner_id, uuid, settings
    FROM usercharts
    LEFT JOIN project_id_mapping ON (usercharts.project_id=project_id_mapping.id);

DROP TABLE usercharts;
ALTER TABLE usercharts_new RENAME TO usercharts;


DROP TABLE IF EXISTS objectmapping_new;

CREATE TABLE objectmapping_new (
	user_id INTEGER,
	table_name VARCHAR,
	local_id INTEGER,
	dashboard_id VARCHAR,
    PRIMARY KEY (user_id, table_name, local_id)
);

-- Insert Project ID rows
INSERT INTO objectmapping_new (user_id, table_name, local_id, dashboard_id)
    SELECT user_id, table_name, local_id, uuid
    FROM objectmapping
    LEFT JOIN project_id_mapping ON (dashboard_id = project_id_mapping.id)
    WHERE table_name = "project";

-- Insert other rows
INSERT INTO objectmapping_new (user_id, table_name, local_id, dashboard_id)
    SELECT user_id, table_name, local_id, CAST(dashboard_id AS TEXT)
    FROM objectmapping
    LEFT JOIN project_id_mapping ON (dashboard_id = project_id_mapping.id)
    WHERE table_name != "project";

DROP TABLE objectmapping;
ALTER TABLE objectmapping_new RENAME TO objectmapping;

PRAGMA foreign_keys=on;
