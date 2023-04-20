CREATE SCHEMA devbilava;
CREATE SCHEMA dogs;

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


-- Status 3: Subfigure.Predicted

INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('a', '', 1, 1, NULL, 3, 'a', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'terrier.1', 'kennel1', 1, NULL); -- id 1
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('a', '', 1, 1, NULL, 3, 'a', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'terrier.1', 'kennel1', 1, NULL); -- id 2
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('a', '', 1, 1, NULL, 3, 'a', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'terrier.1', 'kennel1', 1, NULL); -- id 3
INSERT INTO dogs.figures(name, caption, num_panes, fig_type, doc_id, status, uri, parent_id, width, height, coordinates, last_update_by, owner, migration_key, notes, label, source, page, ground_truth) VALUES ('a', '', 1, 1, NULL, 3, 'a', NULL, 10, 10, '{0.2, 0.2, 2, 2}', NULL, NULL, NULL, NULL, 'bulldog.2', 'kennel1', 1, NULL); -- id 4

-- Assume a dog classifier by breeds
--  BREEDS ---- TERRIER --- 1
--                    |---- 2
--           ---BULLDOG --- 1
--                    |---- 2
-- There are 4 images inserted and 8 records because one record is duplicated for the parent classifier.
-- There are 3 updates were 2 are errors, and 1 is a label correction.

INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'dogs', 'breeds',         '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'terrier.1', 'terrier',    NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (1, 'dogs', 'breeds.terrier', '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'terrier.1', 'terrier.1',  NULL, NULL);
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'dogs', 'breeds',         '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'terrier.1', 'terrier',   'bulldog.1', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (2, 'dogs', 'breeds.terrier', '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'terrier.1', 'terrier.2', 'bulldog.1', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'dogs', 'breeds',         '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'terrier.1', 'terrier.1', 'error.cat', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (3, 'dogs', 'breeds.terrier', '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'terrier.1', 'terrier.1', 'error.cat', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'dogs', 'breeds',         '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bulldog.2', 'bulldog.2', 'error.bird', '2023-04-18');
INSERT INTO devbilava.features (id, schema, classifier, name, uri, width, height, source, status, split_set, x_pca, y_pca, x_tsne, y_tsne, x_umap, y_umap, pred_probs, ms, en, hit_pca, hit_tsne, hit_umap, label, prediction, upt_label, upt_date) VALUES (4, 'dogs', 'breeds.bulldog', '1', 'uri', 10, 10, 'kennel1', 3, 'UNL', 1, 1, 2, 2, 3, 3, '{0.1, 0.9}', 0.4, 0.3, 0.2, 0.2, 0.2, 'bulldog.2', 'bulldog.2', 'error.bird', '2023-04-18');