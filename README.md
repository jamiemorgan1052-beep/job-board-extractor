# Offline Job Board Extractor

A small, dependency-free Python tool that converts authorized, saved job-board
HTML into normalized JSON or CSV. Extraction rules live in a compact JSON file,
so the parser can be adapted without editing Python.

![Abstract project illustration](docs/featured.png)

Need a small authorized extraction or automation task? Book the fixed-scope [Python Automation, Data Cleanup & QA service](https://contra.com/s/mXUk6X3o-python-automation-data-cleanup-and-qa) from USD 75.

Prefer a reusable download? Buy the [single-user commercial toolkit for USD 29](https://contra.com/products/4LenSM3O-offline-job-board-extractor-python-toolkit).

## What it demonstrates

- Configurable selectors for title, company, location, link, and description
- Relative-to-absolute URL resolution
- Duplicate removal and required-field validation
- JSON and CSV output
- Useful warnings for incomplete or repeated cards
- Fully offline tests with synthetic HTML

It deliberately performs no live crawling. You supply a local HTML file that
you are authorized to process.

## Requirements

- Python 3.10 or newer
- No third-party packages

## Quick start

From the repository root:

```powershell
python -m jobextractor.cli `
  --html tests/fixtures/jobs.html `
  --base-url https://jobs.example.test `
  --config examples/selectors.json `
  --output jobs.json
```

The bundled fixture prints:

```text
warning: card 3: duplicate skipped
warning: card 4: skipped; missing company, location, link, link href
extracted 2 jobs to jobs.json
```

An output record has a predictable shape:

```json
{
  "title": "Backend Engineer",
  "company": "Example Labs",
  "location": "Remote",
  "url": "https://jobs.example.test/jobs/42",
  "description": "Build small, reliable APIs."
}
```

Use `--format csv` for CSV output. Run `python -m jobextractor.cli --help`
for the complete command reference.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Responsible use

Only process content you own or have permission to access. This sample does not
bypass authentication, CAPTCHAs, rate limits, robots controls, or anti-bot
systems.

## Project notes

See [PROVENANCE.md](PROVENANCE.md) for authorship and AI-assistance disclosure.
Licensed under the [MIT License](LICENSE).
