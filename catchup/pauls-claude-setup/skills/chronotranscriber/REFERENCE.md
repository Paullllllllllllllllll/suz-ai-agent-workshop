## Recommended Defaults

- model: `gpt-5.6-luna`, high reasoning, original image detail, flex
  processing with `request_timeout: 900`, `concurrency_limit: 16`
  (OpenAI API tier 3)

## model_config.yaml

```yaml
transcription_model:
  provider: openai                # openai | anthropic | google | openrouter | custom (auto-detected if omitted)
  name: gpt-5.6-luna             # Model ID (see README for full list per provider)
  max_output_tokens: 128000       # Max tokens per response (covers reasoning + output for reasoning models)
  expects_image_inputs: true      # Fail fast if model lacks vision
  reasoning:
    effort: high                  # low | medium | high (cross-provider; OpenAI also: none, xhigh)
  text:
    verbosity: medium             # concise | medium | verbose (GPT-5 family only)
  temperature: 1                  # Sampler (filtered for reasoning models; Anthropic: 0-1; OpenAI/Google: 0-2)
  top_p: 1.0
  frequency_penalty: 0.01        # OpenAI only
  presence_penalty: 0.01         # OpenAI only
  user_instruction: ""           # Extra instruction appended to the prompt
  context_image_instruction: ""  # Label shown before an injected context image
  # service_tier: configured in concurrency_config.yaml
```

GPT-5.4+ models support `original` image detail mode (full-resolution, no tiling), configured via
`llm_detail: original` in `image_processing_config.yaml` under `api_image_processing`.

## paths_config.yaml

```yaml
general:
  interactive_mode: true          # true = interactive prompts; false = CLI mode
                                   # (overridable per run via --interactive / --non-interactive)
  retain_temporary_jsonl: true    # Keep .jsonl tracking files (batch always retains)
  keep_preprocessed_images: false # Retain preprocessed images after transcription
  input_paths_is_output_path: false # true = write outputs next to inputs; false = use
                                   # the configured output directories below (a separate
                                   # axis from --output-mode, which controls hash-vs-
                                   # mirror layout of the output directory)
  # state_dir: ''                 # Cross-run state dir (daily token-budget
                                   # counter). Empty/unset = user-level default
                                   # (~/.chronotranscriber/). A legacy per-CWD
                                   # .chronotranscriber_token_state.json is adopted once.
  output_format: 'txt'           # Default output format: txt | md | json
  resume_mode: 'skip'            # Default resume: skip | overwrite (CLI: --resume / --force)
  logs_dir: ''                   # Log file path or directory (empty = project root)
  # Auto mode settings
  auto_mode_pdf_use_ocr_for_scanned: true
  auto_mode_pdf_use_ocr_for_searchable: true
  auto_mode_pdf_ocr_method: 'gpt'       # gpt | tesseract
  auto_mode_image_ocr_method: 'gpt'     # gpt | tesseract

file_paths:
  PDFs:
    input: ''
    output: ''
  Images:
    input: ''
    output: ''
  EPUBs:
    input: ''
    output: ''
  MOBIs:                          # Covers MOBI, AZW, AZW3, KFX (unencrypted only)
    input: ''
    output: ''
  Auto:
    input: ''
    output: ''

postprocessing:                   # Used by postprocess.py and --use-config
  enabled: true
  merge_hyphenation: false
  collapse_internal_spaces: true
  max_blank_lines: 2
  tab_size: 4
  wrap_lines: true
  auto_wrap: true
  wrap_width: null                # null = auto-detect when auto_wrap is true
```

## concurrency_config.yaml

```yaml
concurrency:
  transcription:
    concurrency_limit: 16         # Max concurrent LLM API calls (sync mode); 16 = OpenAI
                                   # tier 3, also bounds in-flight drain past per-key caps
    delay_between_tasks: 0.5      # Seconds between tasks (0 = max throughput)
    service_tier: flex            # OpenAI service tier: auto | default | flex | priority
    batch_chunk_size: 20          # Images per batch file (<=150 MB per chunk); a chunk
                                   # additionally auto-splits into provider-limited
                                   # parts on oversized submissions, all part ids persisted
                                   # in *_batch_submission_debug.json
    request_timeout: 900          # Per-call timeout in seconds (900 = 15 min for flex)
    retry:
      attempts: 8                 # Max network retries (exponential backoff)
      validation_attempts: 1      # Max retries for unparseable structured output / min_input_tokens
      min_input_tokens: 0         # Responses below this are retried (0 = disabled)
      content_quality:            # Quality validators; failed pages retried within
                                   # validation_attempts; disabled by default
        enabled: false
        max_repeated_substring_length: 30   # hallucination-loop substring detection
        max_repeated_substring_count: 15
        min_alphanum_in_substring: 15
        max_single_char_repeat: 75          # e.g. "MMMM..." x75
        min_transcription_length: 0         # truncation detection (0 = disabled)
        bleed_check_chars: 200              # system-prompt-bleed check window
        system_prompt_bleed_patterns: ['"type": "object"', '"additionalProperties"', ...]
        max_line_repeat_count: 18           # excessive-line-repetition (map-label loops)
        min_line_length_for_repeat: 10
        invalid_markers:                    # icon-description literals / placeholder flooding / "?" clusters
          enabled: true
          # icon_description_literals, generic_placeholder_patterns, ... — see config for full lists

prompt_caching:
  enabled: false                  # Master toggle for all providers
  anthropic:
    ttl: "5m"                     # Cache TTL: "5m" (free writes) | "1h" (2x write cost)
  openai:
    prompt_cache_retention: 24h   # null (default 5-10 min) | "24h" (gpt-5.x, gpt-4.1)
  openrouter:
    anthropic_cache_control: true # Pass cache_control for Claude models via OpenRouter

# Shape below with the shipped example defaults; the live values may differ
# in your config/concurrency_config.yaml, so read that file at run time.
daily_token_limit:
  enabled: false                  # shipped default
  daily_tokens: 10_000_000        # Combined cap (secondary guard); resets at 00:01 UTC
  scope: pooled                   # pooled = cap only calls in a defined pool; all = legacy
  per_key_pool_caps:              # per-(API key, pool) daily caps (primary gate)
    enabled: true
    openai:
      small: 9_750_000            # bare int: cap; models from built-in defaults
      large:
        cap: 975_000              # mapping form: custom cap and/or models list
        # models: ["gpt-5", "o3"]
```

Usage is stamped per (provider, key env var, pool) into the shared ledger;
pools are definable per provider (built-in OpenAI defaults otherwise).
Pool-less buckets (e.g. the local custom endpoint) are never blocked by
OpenAI usage under `scope: pooled`. A manual `api_keys_config.yaml` remap
is picked up at the next item without a restart.

## audio_config.yaml

Sixth config file (since v3.0.0); optional — the loader falls back to the
`.example` and then to `{}`. Governs `--type audio` only.

```yaml
audio_transcription:
  provider: openai            # audio-api venue: openai | google
  concurrency_limit: 4        # concurrent chunk requests
  openai:
    model: gpt-transcribe     # | gpt-4o-transcribe | gpt-4o-mini-transcribe | whisper-1
    languages: []             # ISO-639-1 hints, gpt-transcribe only (e.g. ['de', 'en'])
    language: ''              # single code for the other models
    keywords: []              # literal expected terms, gpt-transcribe only
  google:
    model: gemini-3.6-flash
    language_hint: ''         # appended to the transcription prompt
chunking:
  target_seconds: 600         # chunk length; changing it invalidates in-progress resume
  chunk_format: mp3           # mp3 | wav16 | copy
  apply_to_local: false       # whisper handles long files natively
local_whisper:
  model_size: large-v3        # tiny | base | small | medium | large-v2 | large-v3
  device: auto                # auto | cpu | cuda
ffmpeg:
  ffmpeg_cmd: ''              # '' = PATH; install e.g. via winget (Windows) or brew (macOS)
postprocessing:               # speech profile: no hyphenation merge, no line wrap
  wrap_lines: false
```
