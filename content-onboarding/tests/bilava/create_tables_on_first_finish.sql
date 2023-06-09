-- Test scenario for first attempt to do BI-LAVA on-finish, in other words,
-- we populated BI-LAVA for the first time and it's our first attempt to 
-- update the data and then generate the updated files for training our
-- classifiers.

CREATE SCHEMA devbilava;
CREATE SCHEMA dogs;
CREATE SCHEMA unlabeled;

CREATE TABLE devbilava.archivevault
(
  id SERIAL PRIMARY KEY,
  subfig_id integer NOT NULL,
	schema text NOT NULL,
  label text NOT NULL,
  prediction text NOT NULL,
	upt_label text NOT NULL,
  upt_date date NOT NULL,
	session_number integer NOT NULL
);

CREATE TABLE devbilava.session
(
  id SERIAL PRIMARY KEY,
  end_date timestamp with time zone NOT NULL,
  "number" integer NOT NULL,
  num_updates integer NOT NULL,
  num_errors integer NOT NULL,
  num_classifiers integer NOT NULL
);

CREATE TABLE devbilava.features
(
    id integer NOT NULL,
    schema text NOT NULL,
    classifier text NOT NULL,
    name text NOT NULL,
    uri text NOT NULL,
    width numeric NOT NULL,
    height numeric NOT NULL,
    source text NOT NULL,
    status text NOT NULL,
    split_set text NOT NULL,
    x_pca numeric NOT NULL,
    y_pca numeric NOT NULL,
    x_tsne numeric NOT NULL,
    y_tsne numeric NOT NULL,
    x_umap numeric NOT NULL,
    y_umap numeric NOT NULL,
    pred_probs numeric[] NOT NULL,
    ms numeric NOT NULL,
    en numeric NOT NULL,
    hit_pca numeric NOT NULL,
    hit_tsne numeric NOT NULL,
    hit_umap numeric NOT NULL,
    label text ,
    prediction text NOT NULL,
    upt_label text,
    upt_date date,
    CONSTRAINT features_pkey PRIMARY KEY (id, schema, classifier)
);

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
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-1', '', 1, 1, NULL, 3, 'pu-1', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'unldogs', 1, NULL); -- id 1
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-2', '', 1, 1, NULL, 3, 'pu-2', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.1', 'unldogs', 1, NULL); -- id 2
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-3', '', 1, 1, NULL, 3, 'pu-3', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.2', 'unldogs', 1, NULL); -- id 3
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-4', '', 1, 1, NULL, 3, 'pu-4', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul-2', 'unldogs', 1, NULL); -- id 4
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-5', '', 1, 1, NULL, 3, 'pu-5', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter-1', 'unldogs', 1, NULL); -- id 5
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-6', '', 1, 1, NULL, 3, 'pu-6', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul-1', 'unldogs', 1, NULL); -- id 6

-- Assume a dog classifier by breeds
--  BREEDS ---- TERRIER --- 1
--                    |---- 2
--           ---BULLDOG --- 1
--                    |---- 2

-- From the labeled data
-- There are 4 images inserted and 8 records because one record is duplicated for the parent classifier.
-- updates: 1
-- errors: 2

-- From the unlabeled data:
-- 2 images, and 1 update

-- Total errors: 2, Total updates: 3


-- Session updates including updates to labeled and unlabeled sources like detecting errors, correcting mislabels, and confirming predictions on unlabeled data.
---                                                                                                                                                                                                                                                                                                                                                                                              label(gt) pred   upt_label 
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'dogs', 'breeds',         'img-1', 'p1', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'bul',    NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'dogs', 'breeds-bulldog', 'img-1', 'p1', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'bul.1',  NULL, NULL);

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'dogs', 'breeds',         'img-2', 'p2', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter',   'bul.1', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'dogs', 'breeds-terrier', 'img-2', 'p2', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', 'bul.1', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'dogs', 'breeds',         'img-3', 'p3', 10, 10, 'kennel1', 3, 'TEST', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter',   'error.cat', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'dogs', 'breeds-terrier', 'img-3', 'p3', 10, 10, 'kennel1', 3, 'TEST', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', 'error.cat', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'dogs', 'breeds',         'img-4', 'p4', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'ter.1', 'ter',   'error.bird', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'dogs', 'breeds-terrier', 'img-4', 'p4', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'ter.1', 'ter.2', 'error.bird', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (5, 'dogs', 'breeds',         'img-5', 'p5', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.1', 'bul',   NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (5, 'dogs', 'breeds-bulldog', 'img-5', 'p5', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.1', 'bul.1', NULL, NULL);

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (6, 'dogs', 'breeds',         'img-6', 'p6', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.1', 'bul',   'bul.2', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (6, 'dogs', 'breeds-bulldog', 'img-6', 'p6', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.1', 'bul.2', 'bul.2', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (7, 'dogs', 'breeds',         'img-7', 'p7', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.2', 'bul',   'ter.2', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (7, 'dogs', 'breeds-bulldog', 'img-7', 'p7', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.2', 'bul.2', 'ter.2', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (8, 'dogs', 'breeds',         'img-8', 'p8', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.2', 'bul',   NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (8, 'dogs', 'breeds-bulldog', 'img-8', 'p8', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'bul.2', 'bul.1', NULL, NULL);

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (9, 'dogs', 'breeds',         'img-9', 'p9', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'ter.2', 'ter',   'ter.1', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (9, 'dogs', 'breeds-terrier', 'img-9', 'p9', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'ter.2', 'ter.2', 'ter.1', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (10, 'dogs', 'breeds',         'img-10', 'p10', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'ter.2', 'ter',   NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (10, 'dogs', 'breeds-terrier', 'img-10', 'p10', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2,  'ter.2', 'ter.2', NULL, NULL);

-- Some images from the unlabeled sources
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'unlabeled', 'breeds',         'unl-1', 'pu-1', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter', NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'unlabeled', 'breeds-terrier', 'unl-1', 'pu-1', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', NULL, NULL);

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'unlabeled', 'breeds',         'unl-2', 'pu-2', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.1', 'bul', 'bul.2', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'unlabeled', 'breeds-bulldog', 'unl-2', 'pu-2', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.1', 'bul.1', 'bul.2', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'unlabeled', 'breeds',         'unl-3', 'pu-3', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.2', 'ter',   'ter.2', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'unlabeled', 'breeds-terrier', 'unl-3', 'pu-3', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.2', 'ter.2', 'ter.2', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'unlabeled', 'breeds',         'unl-4', 'pu-4', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'bul',   'bul.2', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'unlabeled', 'breeds-bulldog', 'unl-4', 'pu-4', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'bul.2', 'bul.2', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (5, 'unlabeled', 'breeds',         'unl-5', 'pu-5', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter',   'ter.1', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (5, 'unlabeled', 'breeds-terrier', 'unl-5', 'pu-5', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', 'ter.1', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (6, 'unlabeled', 'breeds',         'unl-6', 'pu-6', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.1', 'bull',   'error.cat', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (6, 'unlabeled', 'breeds-bulldog', 'unl-6', 'pu-6', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.1', 'bul.1', 'error.cat', '2023-04-18');