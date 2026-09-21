# ChronoMiner Reference

## Recommended Defaults

- model: `gpt-5.6-luna`, high reasoning, original image detail, flex
  processing with `timeouts.total: 900`, `concurrency_limit: 12`
  (OpenAI API tier 3)
- Requires ChronoMiner >= 2.9.0 for `original` image detail on
  `gpt-5.6-luna` and `gpt-5.6-terra`.
- Each image is a separate input FILE, not a chunk: a folder of N images
  is N files, so `concurrency_limit` (chunks within a file) does not
  govern page-image throughput. `max_concurrent_files` does, and it is 1
  while `daily_token_limit.enabled` is true, 2 for visual input
  otherwise. For large page sets, partition the input across parallel
  processes.

## model_config.yaml

Top-level key is **`extraction_model`** (not `transcription_model`).

```yaml
extraction_model:
  # provider: openai | anthropic | google | openrouter (auto-detected if omitted)
  name: gpt-5.6-luna
  max_output_tokens: 128000
  reasoning:
    effort: high            # low | medium | high | xhigh | none
  text:
    verbosity: medium       # low | medium | high (GPT-5 family only)
  temperature: 0.0          # auto-disabled for reasoning models
  top_p: 1.0
  frequency_penalty: 0.0
  presence_penalty: 0.0
```

### Supported Models by Provider

- OpenAI: gpt-5.6(-sol, -terra, -luna), gpt-5.4(-pro), gpt-5.3(-chat-latest,
  -codex), gpt-5.2, gpt-5.1(-instant, -thinking), gpt-5(-mini, -nano),
  gpt-4.1(-mini, -nano), gpt-4o(-mini), o4-mini, o3(-mini, -pro), o1(-mini)
- Anthropic: claude-opus-4-6, claude-sonnet-4-6, claude-opus-4-5, claude-sonnet-4-5,
  claude-haiku-4-5, claude-opus-4-1, claude-opus-4, claude-sonnet-4, claude-3-7-sonnet,
  claude-3-5-sonnet, claude-3-5-haiku
- Google: gemini-3-pro(-preview), gemini-3-flash-preview, gemini-2.5-pro,
  gemini-2.5-flash(-lite), gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash;
  Gemma via Gemini API: gemma-4-31b-it, gemma-4-26b-a4b-it
- OpenRouter: `provider/model` format (e.g., `anthropic/claude-sonnet-4-5`,
  `deepseek/deepseek-r1`, `meta/llama-3.3-70b`, `google/gemma-4-31b-it`,
  `qwen/qwen3-235b-a22b`)

## paths_config.yaml

```yaml
general:
  interactive_mode: true          # false for CLI mode; also overridable
                                   # per-run via --interactive/--non-interactive
  retain_temporary_jsonl: true    # keep .jsonl tracking files after processing
  input_paths_is_output_path: true  # overridden by --output-mode
  logs_dir: ''
  state_dir: ''                   # token-budget + wizard state dir; empty =
                                   # ~/.chronominer/ (user-level, CWD-independent)
schemas_paths:
  SchemaName:
    input: ""
    output: ""
    csv_output: false
    docx_output: false
    txt_output: false
```

## image_processing_config.yaml

Controls visual input preprocessing. Provider-specific sections applied automatically
based on active model.

```yaml
target_dpi: 300                        # PDF page rendering resolution
max_pixels_per_page: 24000000          # safety cap (~72 MB worst-case raw page)

api_image_processing:                  # OpenAI / OpenRouter
  grayscale_conversion: false
  handle_transparency: true
  jpeg_quality: 95
  resize_profile: original
  llm_detail: original                 # low | high | auto | original
  low_max_side_px: 512
  high_target_box: [768, 1536]
  original_max_side_px: 6000
  original_max_pixels: 10240000

anthropic_image_processing:            # Anthropic Claude
  grayscale_conversion: true
  handle_transparency: true
  jpeg_quality: 95
  resize_profile: auto
  high_max_side_px: 1568
  low_max_side_px: 512

google_image_processing:               # Google Gemini
  grayscale_conversion: true
  handle_transparency: true
  jpeg_quality: 95
  resize_profile: auto
  media_resolution: high               # low | high | auto
  high_target_box: [768, 1536]
  low_max_side_px: 512
```

The `--image-detail` CLI flag overrides the per-provider default detail level.

`original` acts on two layers. In preprocessing it skips the
`high_target_box` fit-and-pad and caps only at `original_max_side_px` /
`original_max_pixels`, so the model receives full-resolution pixels. As an
API parameter it is accepted on the OpenAI Responses route only (Chat
Completions allows `auto`/`low`/`high`); ChronoMiner routes models whose
capabilities set `supports_chat_completions: False` there, namely the
GPT-5.6 family, `gpt-5.5-pro`, `gpt-5.4-pro` and `gpt-5.4`. On other models
the parameter is downgraded to `high` with a once-per-model warning while
the pixels stay full-resolution; token counts from such a run match neither
a true `original` nor a true `high` run.

## Available Schemas (13)

| Schema Name | Schema File | Description |
|---|---|---|
| `BibliographicEntries` | `bibliographic_schema.json` | Bibliographic records (books, editions, authors) |
| `StructuredSummaries` | `summary_schema.json` | Structured text summaries |
| `HistoricalAddressBookEntries` | `address_schema.json` | Historical address book entries |
| `BrazilianMilitaryRecords` | `military_record_schema.json` | Brazilian military personnel records |
| `CulinaryWorksEntries` | `culinary_works_schema.json` | Culinary works / cookbook entries |
| `CulinaryPersonsEntries` | `culinary_persons.json` | Culinary-related persons |
| `CulinaryPlacesEntries` | `culinary_places.json` | Culinary-related places |
| `CulinaryEntitiesEntries` | `culinary_entities.json` | Culinary entities (general) |
| `HistoricalRecipesEntriesProductionV3` | `historical_recipes_schema_production.json` | Historical recipes (production schema v3; prompts and modernity anchors reconciled in ChronoMiner v2.14.0) |
| `MichelinGuidesLight` | `michelin_guides_light.json` | Michelin guide entries (lightweight page schema) |
| `CookbookMetadataEntries` | `cookbook_metadata_schema.json` | Cookbook-level metadata |
| `HistoricalPriceEntries` | `historical_price_entries_schema.json` | Historical commodity price observations |
| `InequalityBenchmarks` | `inequality_benchmarks_schema.json` | Inequality benchmark figures (Gini, top shares, ratios) |

Custom schemas: create JSON schema in `schemas/`, register in
`modules/extract/schema_handlers.py`, add paths in `paths_config.yaml`.

## Daily Token Budget Config

In `concurrency_config.yaml` (shape below with the shipped example defaults;
the live values may differ in your `config/concurrency_config.yaml`, so read
that file at run time):

```yaml
daily_token_limit:
  enabled: false             # shipped default
  daily_tokens: 10_000_000   # combined cap across tools (secondary guard)
  scope: pooled              # pooled = cap only calls in a defined pool; all = legacy
  per_key_pool_caps:         # per-(API key, pool) daily caps (primary gate)
    enabled: true
    openai:
      small: 9_750_000       # bare int: cap; models from built-in defaults
      large:
        cap: 975_000         # mapping form: custom cap and/or models list
        # models: ["gpt-5", "o3"]
```

Tracks every API call, resets at 00:01 UTC (one minute after OpenAI's
00:00 UTC free-token reset), displays usage at startup/completion, and
pauses when budget is exhausted (resumes after reset or Ctrl+C). For
Anthropic, cache-specific tokens are also tracked.
Chunk-level token counting uses the target model's own encoding when known.
Usage is stamped per (provider, key env var, pool) into the shared ledger;
a pool is a named model set sharing one daily allowance per key, definable
per provider (built-in OpenAI defaults apply when no models list is
configured). Exhausting one key's pool never blocks another key or a
pool-less (local/non-OpenAI) endpoint under `scope: pooled`. A manual
mid-wait `api_keys_config.yaml` remap is picked up at the next chunk/file
boundary without a restart.

State persists to `~/.chronominer/.chronominer_token_state.json` by default
(user-level, shared across runs regardless of working directory); override
the directory via `general.state_dir` in `paths_config.yaml`. A legacy
`.chronominer_token_state.json` in the working directory is adopted once
into the new location if the user-level file is absent.
