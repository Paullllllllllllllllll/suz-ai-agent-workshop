---
name: fetch-swiss-rents
description: Fetch the two Swiss rent datasets (BFS cantonal XLSX, City of Zurich CKAN JSON) from their public APIs, falling back to the local copies in data/ if a request fails. Use when the user asks to fetch, download, or refresh the rent data.
---

Fetch both datasets in order. After each fetch, tell the user which path
was taken: live download or local fallback.

## 1. Primary: BFS cantonal average rents (XLSX)

```text
GET https://dam-api.bfs.admin.ch/hub/api/dam/assets/36398431/master
```

- Source: BFS, "Durchschnittlicher Mietpreis in Franken nach Zimmerzahl
  und Kanton". Covers the years 2000, 2003, and 2010-2024.
- Load the response body with `pandas.read_excel`. Column headers are in
  German; do not translate them in the raw data, only in outputs.
- License: opendata.swiss OPEN-BY. Attribution to BFS is required in any
  output that uses the data.
- On any request failure (network error, non-200 status, unparseable
  body): use the local copy `data/bfs_mietpreis_kanton.xlsx` instead and
  say so.

## 2. Secondary: City of Zurich rent prices (CKAN JSON)

```text
GET https://data.stadt-zuerich.ch/api/3/action/datastore_search?resource_id=1faf7e1b-0017-4a0a-8ffe-6077b4d597e4&limit=1000
```

- JSON response; records carry `mean`, `qu25`, `qu50`, `qu75` by year,
  district, room count, and cooperative versus market housing.
- License: CC0.
- Send a browser-like `User-Agent` header (for example `Mozilla/5.0`).
  The API intermittently answers bare library requests with 403.
- On any request failure: use the local copy
  `data/zurich_mietpreise_od5161.csv` instead and say so.

## Degradation rule

Never abort the task because a download failed. The local files in
`data/` are complete snapshots; fall back to them automatically and
report which dataset came from where.
