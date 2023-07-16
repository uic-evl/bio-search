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
