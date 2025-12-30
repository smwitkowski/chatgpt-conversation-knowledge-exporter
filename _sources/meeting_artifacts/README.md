# Meeting Artifacts

This directory contains meeting notes and transcripts from various platforms.

## Supported Formats

- **Markdown files (`.md`)**:
  - Google Meet notes (with notes sections and transcript)
  - Zoom meeting notes
  - Other markdown-formatted meeting notes

- **Plain text files (`.txt`)**:
  - Microsoft Teams transcripts (`TIME : NAME : TEXT` format)
  - Zoom transcripts
  - Other plain text transcripts

## File Naming

Recommended naming convention:
- `YYYY-MM-DD_meeting-title.md` or `.txt`
- Example: `2025-12-30_david-stephen_google-meet.md`

## Usage

```bash
# Process all meeting artifacts in this directory
ckx run-all --input _sources/meeting_artifacts/

# Process a specific meeting file
ckx linearize --input _sources/meeting_artifacts/2025-12-30_meeting.md
ckx extract --input _sources/meeting_artifacts/teams_transcript.txt
```

## Notes

- Meeting artifacts are converted into synthetic "conversation" structures
- Each file becomes one conversation with a stable ID (`meeting__<slug>__<hash8>`)
- Transcript timestamps are normalized to `HH:MM:SS` format
- Action items in markdown files are automatically detected and tagged

