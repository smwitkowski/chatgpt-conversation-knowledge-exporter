# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial scaffold with packaging (pyproject.toml, Makefile, README)
- CLI structure with Typer
- Linearization step to extract conversations from ChatGPT export JSON
- OpenAI-backed knowledge atom extraction
- Documentation compilation from atoms
- Support for `uv` package manager
- `--conversation-id` option for single-conversation testing
- Per-chunk progress feedback during extraction
- Project knowledge compilation prompt for synthesizing docs with AI assistants
- Support for single-conversation JSON files (objects with `mapping`/`current_node`) in addition to list-based exports
- Automatic conversation ID injection from filename when `id`/`conversation_id` is missing in single conversation files
- Support for Claude AI export JSON inputs (converted to ChatGPT-style mapping internally)
- `consolidate` command to aggregate per-conversation outputs into project-wide knowledge packet with exact-match deduplication

### Changed
- Switched from traditional venv/pip to `uv` for faster dependency management

## [0.1.0] - 2024-12-XX

### Added
- Initial release
