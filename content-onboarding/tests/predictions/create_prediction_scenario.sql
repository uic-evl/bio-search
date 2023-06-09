-- Test scenario for predicting labels on the figures in the database

CREATE SCHEMA dogs;
CREATE SCHEMA unlabeled;

CREATE TABLE dogs.figures
(
    id SERIAL PRIMARY KEY,
    name text,
    caption text,
    num_panes integer,
    fig_type integer,
    doc_id integer,
    status integer,
    uri text NOT NULL,
    parent_id integer DEFAULT 0,
    width numeric NOT NULL,
    height numeric NOT NULL,
    coordinates numeric[],
    last_update_by text,
    owner text,
    migration_key character varying(30),
    notes text,
    label text,
    source text NOT NULL,
    page numeric,
    ground_truth text
);

CREATE TABLE unlabeled.figures
(
    id SERIAL PRIMARY KEY,
    name text,
    caption text,
    num_panes integer,
    fig_type integer,
    doc_id integer,
    status integer,
    uri text NOT NULL,
    parent_id integer DEFAULT 0,
    width numeric NOT NULL,
    height numeric NOT NULL,
    coordinates numeric[],
    last_update_by text,
    owner text,
    migration_key character varying(30),
    notes text,
    label text,
    source text NOT NULL,
    page numeric,
    ground_truth text
);


-- Status 3: Subfigure.Predicted
-- Status 4: Subfigure.GroundTruth
---                                                                                                                                                                                                                                                                                                           label                ground_truth
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-1',  '', 1, 1, NULL, 4, 'p1',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.1', 'kennel1', 1, 'bul.2'); -- id 1
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-2',  '', 1, 1, NULL, 4, 'p2',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'kennel1', 1, 'ter.1'); -- id 2
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-3',  '', 1, 1, NULL, 4, 'p3',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'kennel1', 1, 'ter.1'); -- id 3
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-4',  '', 1, 1, NULL, 4, 'p4',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.2', 'kennel1', 1, 'ter.1'); -- id 4
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-5',  '', 1, 1, NULL, 4, 'p5',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.1', 'kennel1', 1, 'bul.1'); -- id 5
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-6',  '', 1, 1, NULL, 4, 'p6',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.2', 'kennel1', 1, 'bul.1'); -- id 6
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-7',  '', 1, 1, NULL, 4, 'p7',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.2', 'kennel1', 1, 'bul.2'); -- id 7
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-8',  '', 1, 1, NULL, 4, 'p8',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.1', 'kennel1', 1, 'bul.2'); -- id 8
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-9',  '', 1, 1, NULL, 4, 'p9',  NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.2', 'kennel1', 1, 'ter.2'); -- id 9
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-10', '', 1, 1, NULL, 4, 'p10', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.2', 'kennel1', 1, 'ter.2'); -- id 10

--                                                                                                                                                                                                                                                                                                                   label     source page ground_truth
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-1', '', 1, 1, NULL, 4, 'pu-1', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'unldogs', 1, 'ter.1'); -- id 1
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-2', '', 1, 1, NULL, 2, 'pu-2', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.1', 'unldogs', 1, NULL); -- id 2
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-3', '', 1, 1, NULL, 2, 'pu-3', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.2', 'unldogs', 1, NULL); -- id 3
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-4', '', 1, 1, NULL, 3, 'pu-4', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul-2', 'unldogs', 1, NULL); -- id 4
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-5', '', 1, 1, NULL, 3, 'pu-5', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter-1', 'unldogs', 1, NULL); -- id 5
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-6', '', 1, 1, NULL, 3, 'pu-6', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul-1', 'unldogs', 1, NULL); -- id 6