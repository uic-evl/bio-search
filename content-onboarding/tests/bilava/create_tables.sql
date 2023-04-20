CREATE SCHEMA devbilava;
CREATE SCHEMA dogs;
CREATE SCHEMA unlabeled;

CREATE TABLE devbilava.archivevault
(
  id SERIAL PRIMARY KEY,
  subfig_id integer NOT NULL,
	schema text NOT NULL,
  label text NOT NULL,
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
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-1', '', 1, 1, NULL, 3, 'p1', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'kennel1', 1, 'bul.2'); -- id 1
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-2', '', 1, 1, NULL, 3, 'p2', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'kennel1', 1, 'ter.1'); -- id 2
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-3', '', 1, 1, NULL, 3, 'p3', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'kennel1', 1, 'ter.1'); -- id 3
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('img-4', '', 1, 1, NULL, 3, 'p4', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.2', 'kennel1', 1, 'ter.1'); -- id 4

INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-1', '', 1, 1, NULL, 3, 'pu-1', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'ter.1', 'unldogs', 1, NULL); -- id 1
INSERT INTO unlabeled.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('unl-2', '', 1, 1, NULL, 3, 'pu-2', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bul.1', 'unldogs', 1, NULL); -- id 2

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

-- Some images from the labeled sources
---                                                                                                                                                                                                                                                                                                                                                                                              label(gt) pred   upt_label 
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'dogs', 'breeds',         'img-1', 'uri', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'ter',    NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'dogs', 'breeds.terrier', 'img-1', 'uri', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'ter.1',  NULL, NULL);

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'dogs', 'breeds',         'img-2', 'uri', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter',   'bul.1', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'dogs', 'breeds.terrier', 'img-2', 'uri', 10, 10, 'kennel1', 3, 'TRAIN', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.2', 'bul.1', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'dogs', 'breeds',         'img-3', 'uri', 10, 10, 'kennel1', 3, 'TEST', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', 'error.cat', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'dogs', 'breeds.terrier', 'img-3', 'uri', 10, 10, 'kennel1', 3, 'TEST', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', 'error.cat', '2023-04-18');

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'dogs', 'breeds',         'img-4', 'uri', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'bul.2', 'error.bird', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'dogs', 'breeds.bulldog', 'img-4', 'uri', 10, 10, 'kennel1', 3, 'VAL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.2', 'bul.2', 'error.bird', '2023-04-18');

-- Some images from the unlabeled sources
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'unlabeled', 'breeds',         'unl-1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', NULL, '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'unlabeled', 'breeds.terrier', 'unl-1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'ter.1', 'ter.1', NULL, '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'unlabeled', 'breeds',         'unl-2', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.1', 'bul.1', 'bul.2', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'unlabeled', 'breeds.bulldog', 'unl-2', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bul.1', 'bul.1', 'bul.2', '2023-04-18');