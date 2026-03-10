# Changelog

## 0.5.1 (Unreleased)

- **NEW: Series & Seasons support** - Browse UP 主的合集与系列
  - `bili series list <mid>` - List all series and seasons for a UP
  - `bili series archives <series_id> --mid <uid>` - Get videos in a series
  - `bili series season <season_id> --mid <uid>` - Get videos in a season (合集)
  - Support `--format yaml|json` and `--page-size` options
  - Full test coverage with 8 automated tests

## 0.5.0

- Add subtitle timeline output via `bili video --subtitle-timeline` / `-st`
- Add `--subtitle-format timeline|srt`
- Keep subtitle timeline compatible with current `--yaml` / `--json` command surface
- Ensure subtitle timeline requests load optional credentials like plain subtitles
- Restore README badges and fix CI type-checking with `types-PyYAML`
