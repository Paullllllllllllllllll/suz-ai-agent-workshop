## Recommended Defaults

- Both steps: model `gpt-5.6-luna`, high reasoning, `image_size: original`
  (transcription), flex service tier with `api_timeout: 900`,
  `concurrency_limit: 80` (OpenAI API tier 3)

## app.yaml -- Application settings, paths, feature toggles

```yaml
cli_mode: false                    # true = CLI arguments, false = interactive prompts
summarize: true                    # false = transcription only (no summary phase)
summary_output:
  docx: true                       # Generate .docx formatted summary
  markdown: true                   # Generate .md summary for version control
input_folder_path: ''              # Directory with PDFs/image folders
output_folder_path: ''             # Empty = use input_folder_path as output location
input_paths_is_output_path: true   # true = write outputs beside each input file
delete_temp_working_dir: true      # Delete extracted images and temp files after completion
citation:
  openalex_email: ''               # Email for OpenAlex polite pool (faster responses)
  max_api_requests: 300            # Cap enrichment API calls per document (every request counts)
  enable_openalex_enrichment: true # false = skip API calls (faster summary generation)
  merge_ratio: 0.90                # SequenceMatcher similarity gate for fuzzy merge (0-1)
  merge_jaccard: 0.85              # Token-set Jaccard gate for fuzzy merge (0-1)
  match_title_overlap: 0.5         # Min title-word overlap to accept an OpenAlex link
paths:
  state_dir: ''                    # Empty = ~/.autoexcerpter; override with an absolute path
# Shape below with the shipped example defaults; the live values may differ
# in your config/defaults/app.yaml, so read that file at run time.
daily_token_limit:
  enabled: false                   # shipped default
  daily_tokens: 10_000_000         # Combined cap, secondary guard (resets at 00:01 UTC)
  chunk_estimate_seed: 25_000      # Cold-start per-page token estimate before usage is observed
  estimate_smoothing: 0.3          # EWMA smoothing factor (0-1) for the rolling per-page estimate
  scope: pooled                    # pooled = cap only calls in a defined pool; all = legacy
  per_key_pool_caps:               # per-(API key, pool) daily caps (primary gate)
    enabled: true
    openai:
      small: 9_750_000             # bare int: cap; models from built-in defaults
      large: 975_000               # a mapping form with cap/models keys is also accepted
```

Usage is stamped per (provider, key env var, pool) into the shared ledger;
pools are definable per provider (built-in OpenAI defaults otherwise). The
transcription and summary roles stamp independent buckets, so an exhausted
pooled summary key never blocks a pool-less transcription endpoint. A manual
mid-wait `api_keys.yaml` remap is picked up at the next item without a
restart.

**Citation deduplication tuning**: extracted citations are
folded (accents/case/quotes/dashes) and keyed by `(author, year, volume,
title)`; a conservative fuzzy pass then merges near-identical variants only
within a `(first-author surname, year)` block, gated by `merge_ratio` or
`merge_jaccard`. Different years or volumes never merge, and every merge is
logged. `match_title_overlap` gates OpenAlex link acceptance (also requires a
corroborating year-or-author signal). Lower the thresholds to merge/link more
aggressively (riskier).

**State directory**: daily token-budget state and the persistent OpenAlex
cache live under `paths.state_dir` (`config/state.py`), default
`~/.autoexcerpter`. A legacy `.autoexcerpter_token_state.json` in the
working directory is adopted once into the state dir if present.

## model.yaml -- LLM provider and model settings

```yaml
transcription_model:
  name: "gpt-5.6-luna"
  provider: "openai"               # openai | anthropic | google | openrouter | custom (auto-detected from name)
  max_output_tokens: 128000
  reasoning:
    effort: high                   # Maps to: OpenAI reasoning_effort | Anthropic extended_thinking | Google thinking_level
  text:
    verbosity: medium              # GPT-5 family only; ignored for other providers via capability guarding
  temperature: 1.0                 # 0.0-2.0 (null = provider default)
  image_size: original             # low | high | auto | original (original: GPT-5.6 family,
                                   # full input resolution, no patch cap)

summary_model:
  name: "gpt-5.6-luna"
  provider: "openai"
  max_output_tokens: 128000
  reasoning:
    effort: high
  text:
    verbosity: low
  temperature: 1.0
```

Provider detection: explicit `"provider:model"` format or automatic
inference from model name prefix (gpt- = openai, claude- = anthropic,
gemini- = google, contains `/` = openrouter).

## concurrency.yaml -- API concurrency, rate limits, retries

```yaml
api_requests:
  api_timeout: 900                 # Request timeout in seconds (flex-tier queuing)
  rate_limits:                     # [max_requests, window_seconds] sliding windows
    - [10, 1]
    - [600, 60]
    - [600, 3600]
  transcription:
    concurrency_limit: 80          # Parallel API requests (OpenAI tier 3)
    service_tier: flex             # default | flex | priority (OpenAI only)
  # No separate summary: block — summaries run inline in the transcription
  # workers and share their concurrency and rate limiter.

retry:
  max_attempts: 8                  # Total attempts for API errors
  max_elapsed: 900                 # Time-based retry horizon (s) per request; retries
                                   # continue while attempts OR the window remain
                                   # (0 = attempts-only behavior)
  backoff_base: 0.5                # Initial backoff in seconds
  backoff_cap: 120                 # Hard ceiling (s) on any single wait, incl. Retry-After
  backoff_multipliers:
    rate_limit: 2.0                # 429 Too Many Requests
    timeout: 1.5                   # Connection/read timeouts
    server_error: 2.0              # 5xx errors
    other: 2.0
  jitter:
    min: 0.5
    max: 1.0
  schema_retries:                  # Retries based on model output flags (not API errors)
    transcription:
      validation_failure:          # Invalid JSON or missing required schema keys
        enabled: true              # Fires BEFORE flag-specific retries
        max_attempts: 3
        backoff_base: 0.5
        backoff_multiplier: 1.5
      no_transcribable_text:       # Image contains no text
        enabled: false
        max_attempts: 0
        backoff_base: 0.1
        backoff_multiplier: 1.5
      transcription_not_possible:  # Illegible/corrupted image
        enabled: true
        max_attempts: 3
        backoff_base: 0.1
        backoff_multiplier: 1.5
    summary:
      validation_failure:          # Invalid JSON or missing required schema keys
        enabled: true
        max_attempts: 3
        backoff_base: 0.5
        backoff_multiplier: 1.5
      page_type_null_bullets:      # Non-content page with null bullet_points
        enabled: false
        max_attempts: 0
        backoff_base: 0.5
        backoff_multiplier: 1.5
```

## image_processing.yaml -- Image preprocessing and text cleaning

```yaml
resampling_algorithm: bilinear     # bilinear (fast) or lanczos (quality)

# OpenAI image preprocessing
api_image_processing:
  target_dpi: 300
  grayscale_conversion: true
  handle_transparency: true
  llm_detail: original             # high | low | auto | original (OpenAI Vision detail parameter)
  jpeg_quality: 100
  resize_profile: high             # high | low | auto | none
  low_max_side_px: 512
  high_target_box: [768, 1536]
  original_max_side_px: 6000       # caps for llm_detail: original
  original_max_pixels: 10240000

# Google Gemini image preprocessing
google_image_processing:
  target_dpi: 300
  grayscale_conversion: true
  handle_transparency: true
  media_resolution: high           # ultra_high | high | medium | low | auto
  jpeg_quality: 100
  resize_profile: high
  low_max_side_px: 512
  high_target_box: [768, 1536]

# Anthropic Claude image preprocessing
anthropic_image_processing:
  target_dpi: 300
  grayscale_conversion: true
  handle_transparency: true
  jpeg_quality: 100
  resize_profile: auto
  low_max_side_px: 512
  high_max_side_px: 1568           # Anthropic optimal; max-side capping, no box fitting

# Text cleaning pipeline (post-transcription, before summarization/export)
text_cleaning:
  enabled: true
  unicode_normalization: true      # NFC normalization, remove control chars, soft hyphens
  latex_fixing:
    enabled: true
    balance_dollar_signs: true
    close_unclosed_braces: true
    fix_common_commands: true
    normalize_math_delimiters: true
    balance_left_right: true
    convert_html_subsup: true
  merge_hyphenation: true          # Rejoin line-break splits
  whitespace_normalization:
    enabled: true
    collapse_internal_spaces: true  # 3+ spaces -> 2
    max_blank_lines: 2
    tab_size: 4
  line_wrapping:
    enabled: false                 # WARNING: keep disabled
    auto_width: true               # Compute width from text statistics
    fixed_width: 80                # Used if auto_width is false
```

The correct provider-specific image preprocessing section is auto-selected
at runtime based on the configured provider and model name.
