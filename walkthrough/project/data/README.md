# Data

This folder holds two rent datasets. Both are local snapshots of public
APIs; the `fetch-swiss-rents` skill downloads fresh copies and falls
back to these files when a request fails.

## bfs_mietpreis_kanton.xlsx

This dataset reports average rents in Swiss francs by number of rooms
and canton for the years 2000, 2003, and 2010-2024. It is published by
the Swiss Federal Statistical Office (BFS) as "Durchschnittlicher
Mietpreis in Franken nach Zimmerzahl und Kanton".

Source URL:
`https://dam-api.bfs.admin.ch/hub/api/dam/assets/36398431/master`

The file is in XLSX format and can be loaded with `pandas.read_excel`.
Column headers are in German; keep them as-is in the raw data and
translate only in figures and tables.

The dataset is licensed under opendata.swiss **OPEN-BY**, which allows
free use, sharing, and adaptation but requires that the source be
named. Credit "Bundesamt für Statistik (BFS)" in every output that uses
the data.

## zurich_mietpreise_od5161.csv

This dataset contains rent price statistics for the City of Zurich. It
reports `mean`, `qu25`, `qu50`, and `qu75` by year, district, room
count, and cooperative versus market housing. The City of Zurich
publishes it via its CKAN API.

Source URL:
`https://data.stadt-zuerich.ch/api/3/action/datastore_search?resource_id=1faf7e1b-0017-4a0a-8ffe-6077b4d597e4&limit=1000`

The API returns JSON; this file holds the same records as CSV. The API
intermittently answers requests without a browser-like `User-Agent`
header with 403, so set one (for example `Mozilla/5.0`) when fetching.

The dataset is licensed under **CC0** (public domain dedication); no
attribution is required.

## Fallback logic

Prefer the live APIs so the data stays current. If a request fails for
any reason, fall back to the local file and state in the output which
path was taken. Do not edit these files by hand.
