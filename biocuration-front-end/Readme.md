# Biocuration Front-End

NX monorepo for the search applications `scholar`, `gxd`, and the labeling
visual analytics system `bi-lava`.

## Prepare your development environment

This project has been tested on Node 16.14 with npm, and those are the only
pre-requisites. You can install Node by using `nvm`, `homebrew`, `volta`, or
your preferred package manager. If you are using `volta`, you don't need to
setup anything because Volta's shim will detect the version in `package.json`
and setup the environment for you. Follow the sections below to setup the
environmental variables for each application.

## Image Scholar

`Image Scholar` is a search interface for biomedical documents that explores
enhancing the search experience with images and image modalities. You can find
our publication
[here](https://academic.oup.com/bioinformaticsadvances/article/3/1/vbad095/7225231).

### Pre-requisites

The front-end application does not hold much logic besides calling the search
endpoint and displaying the content onto the search results. Therefore, it
requires the connection to the search API and the web servers serving the static
assets (images and pdfs). The search API project can be found in this repository
under `XXX`.

Configure the following environmental variables:

```bash
NX_SEARCH_API=
NX_PDFS_ENDPOINT=
NX_FIGURES_ENDPOINT=
NX_COLLECTION=cord19
NX_FULL_TEXT=true
```

An easy way to add these variables for local development is to create a file
`.local.env` inside `apps/cord19-scholar`.

### Start

```bash
npm run cord19-scholar
# connect to localhost:4201
```

You can further use NX flags to run it in development or production modes:

```
npm run cord19-scholar:serve:(development|production)
```

## Serve

```
nx run cord19-scholar:serve:(development|production)
nx run gdx:serve:(development|production)
nx run bilava:serve:(development|production)
```

## Build

Place the .env file inside the corresponding app folder, then:

```bash
nx run cord19-scholar:build:production
nx run gdx:build:production
nx run bilava:build:production
```

### CORD19 environmental variables

```vim
NX_SEARCH_API=
NX_PDFS_ENDPOINT=
NX_FIGURES_ENDPOINT=
NX_COLLECTION=cord19
```

### GXD environmental variables

### BI-LAVA environmental variables

can only build js lib with buildable false
https://github.com/nrwl/nx/issues/10990

process.env https://bobbyhadz.com/blog/typescript-process-env-type

test deployment npx http-server dist/apps/my-new-app

todo add compression to node https://www.npmjs.com/package/compression
https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs/deployment

run node node dist/app/api/main.js
