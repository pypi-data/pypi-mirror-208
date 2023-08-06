--
-- Schema Change V8:
-- CHANGING THE COLUMN "project.id" TO A UUID
--

PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS project_id_mapping;

CREATE TABLE project_id_mapping (id INTEGER NOT NULL, uuid VARCHAR NOT NULL);
INSERT INTO project_id_mapping (id, uuid)
    SELECT id, shortuuid() FROM project;

DROP TABLE IF EXISTS project_new;

CREATE TABLE project_new (
	id VARCHAR NOT NULL PRIMARY KEY,
	name VARCHAR,
	owner_id INTEGER,
	created TIMESTAMP,
	modified TIMESTAMP,
	selection_criteria VARCHAR,
	FOREIGN KEY (owner_id) REFERENCES "user"(id)
);

INSERT INTO project_new (id, name, owner_id, created, modified, selection_criteria)
    SELECT uuid, name, owner_id, created, modified, selection_criteria
    FROM project
    LEFT JOIN project_id_mapping USING (id);

DROP TABLE IF EXISTS contributor_new;

CREATE TABLE contributor_new (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    project_id VARCHAR,
    read_only BOOLEAN,
	CONSTRAINT FK_contributor_project FOREIGN KEY (project_id) REFERENCES project_new(id),
	CONSTRAINT FK_contributor_user_2 FOREIGN KEY (user_id) REFERENCES "user"(id)
);

INSERT INTO contributor_new (id, user_id, project_id, read_only)
    SELECT id, user_id, uuid, read_only
    FROM contributor
    LEFT JOIN project_id_mapping USING (id);


DROP TABLE IF EXISTS snapshot_new;
CREATE TABLE snapshot_new (
	id INTEGER PRIMARY KEY,
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
	CONSTRAINT FK_snapshot_project_4 FOREIGN KEY (project_id) REFERENCES project_new(id)
);

INSERT INTO snapshot_new (id, created, name, project_id, model_id, data_id, comparison_data_id, stage, status, significant_features, meta)
    SELECT id, created, name, uuid, model_id, data_id, comparison_data_id, stage, status, significant_features, meta
    FROM snapshot
    LEFT JOIN project_id_mapping USING (id);

DROP TABLE project;
ALTER TABLE project_new RENAME TO project;

DROP TABLE contributor;
ALTER TABLE contributor_new RENAME TO contributor;

DROP TABLE snapshot;
ALTER TABLE snapshot_new RENAME TO snapshot;

PRAGMA foreign_keys=on;
