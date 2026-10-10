# Datasets: Standbai

The data Standbai uses or plans to use, with what each dataset is for, how it's accessed, its licence and the attribution to show.

- **Status:** **in use** (wired in code on `main`), **P0** (needed today), **P1** (after the core is live), **P2** (roadmap).
- **Verify before use:** licence and quota lines marked *verify* must be checked on the provider's page before relying on them. Record the result in [`SOURCES.md`](SOURCES.md).

## 1. Hazards and air quality

| Dataset | Used for | Access | Licence / terms | Attribution | Status · Owner |
|---|---|---|---|---|---|
| **NASA FIRMS** active fires (VIIRS S-NPP / NOAA-20 375 m, MODIS 1 km), NRT | `/fires`, map hotspots, outlook signal "hotspots within 300 km", engine smoke sources (FRP) | Area API `https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{W,S,E,N}/{DAY_RANGE}[/{DATE}]`; free `MAP_KEY`; `DAY_RANGE` 1–5; 5,000 transactions per 10 min | NASA open data | "NASA FIRMS" | in use (scripts, presets) → P0 live · Arya |
| **NASA FIRMS archive** (MODIS from Nov 2000, VIIRS from Jan 2012; standard-processing `_SP` sources) | History heatmaps (Merapi 2010 via MODIS; 2019 haze via VIIRS) | Same area API with `_SP` sources and a date, or the FIRMS archive download | NASA open data | "NASA FIRMS" | P1 · Arya |
| **Kaggle export of FIRMS VIIRS 2020–2025** | Training the fire scorer and the 7-day outlook | Kaggle dataset attached to the notebook | Per the Kaggle dataset page (*verify*); underlying data NASA FIRMS | "NASA FIRMS (via Kaggle)" | in use (AI) · Arkan |
| **CAMS global atmospheric composition forecasts via the Open-Meteo Air Quality API** | `/area/now`, `/area/series`, map frames: PM2.5, PM10, dust (plus AOD and US AQI if needed); 3 days past, up to ~5 days forecast; 0.4° | `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=…&longitude=…&hourly=pm2_5,pm10,dust&past_days=3&forecast_days=4` (comma lists for many points); no key | Open-Meteo free tier for non-commercial use; CAMS data under the Copernicus licence | "Air quality: CAMS / Copernicus via Open-Meteo" | P0 · Hikari |
| **Open-Meteo Ensemble API** (ECMWF IFS ENS, AIFS, GFS ensemble, WeatherNext 2) | Engine winds per level and per member, rain | `https://ensemble-api.open-meteo.com/v1/ensemble` (`models` required) | Open-Meteo terms | "Weather: Open-Meteo" | in use · Arya |
| **Open-Meteo Forecast API** | Wind for "right now", 850 hPa wind for ash direction, 16-day rain for the dryness outlook | `https://api.open-meteo.com/v1/forecast` | Open-Meteo terms | "Weather: Open-Meteo" | P0 · Hikari |
| **Open-Meteo Historical Weather (ERA5)** | Past 7-day rain; approximate replays of past events (surface winds) | `https://archive-api.open-meteo.com/v1/archive` | Open-Meteo terms; ERA5 Copernicus licence | "ERA5 / Copernicus via Open-Meteo" | P0 (rain) / P1 (replays) · Hikari / Arya |
| **Open-Meteo Geocoding** | Free-text place → coordinates for chat | `https://geocoding-api.open-meteo.com/v1/search?name=…&countryCode=ID` | Open-Meteo terms; GeoNames data (CC BY 4.0) | "Geocoding: Open-Meteo / GeoNames" | P1 · Hikari |
| **PVMBG / MAGMA Indonesia** volcano levels and VONA | `/volcanoes`, nearest-volcano outlook, eruption presets | Curated into `data/layers/volcanoes_indonesia.geojson`; live MAGMA pages for updates (*verify*) | Government public information | "Volcano status: PVMBG / MAGMA Indonesia" | in use (static) · Arya |
| **Smithsonian Global Volcanism Program** | Eruption history and dates for history events | https://volcano.si.edu (*verify* terms) | Smithsonian terms (*verify*) | "Global Volcanism Program, Smithsonian" | P1 · Arya |
| **ISPU thresholds** (Permen LHK P.14/2020) | PM2.5 category bands 15.5 / 55.4 / 150.4 / 250.4 µg/m³ | `config/assumptions.yaml` (status `sourced_secondary`) | Regulation (public) | "ISPU, KLHK" | in use · Hikari |
| **WHO Air Quality Guidelines 2021** | Health context and stricter advice for sensitive people | Published guideline | WHO terms | "WHO AQG 2021" | P0 (text only) · Hikari |
| **OpenAQ v3** | Validation against station measurements | API with `X-API-Key` | OpenAQ terms (data licences vary by provider) | "OpenAQ" | P2 · Arya |
| **BMKG open data** | Cross-check of hotspots and weather | https://data.bmkg.go.id (*verify*) | BMKG terms (*verify*) | "BMKG" | P2 |
| **SiPongi+ (Ministry of Forestry)** | Official fire and land-fire information (link in sources table) | Web | Government public information | "SiPongi+" | link only |
| **Copernicus ERA5 pressure levels** | Accurate ash replays of older eruptions | Copernicus CDS API (account) | Copernicus licence | "ERA5, Copernicus Climate Change Service" | P2 |
| **GDELT DOC 2.0** | News for *current* events (rolling window of about 3 months) | `https://api.gdeltproject.org/api/v2/doc/doc` | GDELT terms (*verify*) | "GDELT Project" | P2 |
| **ReliefWeb API v2** | Situation reports (needs: masks, water, health) | Needs a pre-approved `appname` (since 2025-11-01) | ReliefWeb terms | "ReliefWeb / UN OCHA" | P2 |

## 2. Exposure and context

| Dataset | Used for | Access | Licence | Attribution | Status · Owner |
|---|---|---|---|---|---|
| **OpenStreetMap** (via Overpass) | Schools, health facilities, airports in `facilities` | Overpass API; curated JSON in `data/layers/` | ODbL | "© OpenStreetMap contributors" | in use · Arya |
| **OSRM** (OpenStreetMap routing) | Evacuation routes to safe hospitals | Public OSRM demo server (fair use) | ODbL data | "Routing: OSRM, © OpenStreetMap contributors" | in use · Arya |
| **WorldPop** (100 m, 2020, age/sex) | Population, children and elderly exposed | Download | CC BY 4.0 | "WorldPop" | in use · Arya |
| **Indonesia coastline** (`data/layers/indonesia_coastline.geojson`) | Land mask; candidate outline for the web map | Bundled file | *verify the original source and licence* | as per source | in use · Arya |
| **Forest and peatland areas** (`forests_indonesia.json`, `forest_boundaries.geojson`) | Forest layer, hotspot context | Bundled files | *verify the original sources* | as per source | in use · Arya |
| Peatland map (BBSDLP, via Global Forest Watch) | Peat multiplier for smoke emissions | Download | *verify* | "Global Forest Watch" | P2 |
| geoBoundaries ADM2 | District boundaries for "my district" | Download | CC BY 4.0 | "geoBoundaries" | P2 |

## 3. News and history (P1)

| Dataset | Used for | Access | Terms | Notes |
|---|---|---|---|---|
| **Google News RSS search** | Headlines from the period of a past event | `https://news.google.com/rss/search?q=<query>+after:YYYY-MM-DD+before:YYYY-MM-DD&hl=en-ID&gl=ID&ceid=ID:en`; no key | Unofficial feed | Store only title, publisher, date, URL; link to the publisher; at most 30 items per event; tolerate failures |
| **Wikipedia REST API** | Short background summary per event | `https://en.wikipedia.org/api/rest_v1/page/summary/<title>` | CC BY-SA 4.0 | Credit Wikipedia with a link |

## 4. Maps in the web app

| Source | Where | Attribution shown |
|---|---|---|
| OpenStreetMap standard tiles | `/simulate` | "© OpenStreetMap contributors" (follow the OSM tile usage policy; low traffic only) |
| Esri World Imagery | `/simulate` satellite toggle | "Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics" |
| Prototype canvas outline (`GEO` constant) | `/map` | Source to be confirmed (FE-06); otherwise use the backend coastline |
| OpenFreeMap (vector, no key) | P2 option for a nicer basemap | "OpenFreeMap © OpenMapTiles Data from OpenStreetMap" |

## 5. Why no Kafka, Spark or MinIO today

- **Sizes:**
  - Indonesia's FIRMS archive is in the hundreds of MB as CSV and much smaller as Parquet.
  - The city air-quality cache is 29 series.
  - Map frames are about 2 MB.
- **Where it fits:** SQLite with R*Tree (serving) and pandas/DuckDB (training) handle this on one machine.
- **When to scale:** if Standbai grows to many countries or live streams, the cloud equivalents are:
  - **Google Cloud Storage** (S3-compatible object store, the MinIO role);
  - **Pub/Sub** (the Kafka role);
  - **BigQuery** or **Dataproc** (the Spark role).
