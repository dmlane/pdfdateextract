# pdfdateextract

> **⚠️ WARNING:** This code is experimental and *not* production-ready. Use at your own risk.

**Extract multilingual dates from PDF files**

This utility scans PDF documents, extracts date snippets in various formats and languages, and prints them in ISO 8601 format. It handles large files by processing pages in configurable chunks, skips pages with parse errors, and falls back to a secondary PDF parser for robustness.

## Features

- **Multilingual support**: Detects dates in English, French, German, Spanish, etc.
- **Flexible formats**: Numeric (DD/MM/YYYY, YYYY-MM-DD), short and long month names.
- **Chunked processing**: Handles large PDFs efficiently with configurable page blocks.
- **Error resilience**: Skips or falls back on pages with encoding issues.
- **Logging**: Detailed logs are written to a rotating log file in the user’s log directory.

## Installation

```bash
pip install pdfdateextract
```

## Usage

```bash
pdfdateextract /path/to/document.pdf
```

By default, all dates are printed in order. To retrieve only the *n*th date, use:

```bash
pdfdateextract /path/to/doc.pdf --nth 2
```

To restrict to specific languages:

```bash
pdfdateextract /path/to/doc.pdf --langs en fr de
```

## API

```python
from extract_date import ExtractDate

extractor = ExtractDate(
    pdf_path="/path/to/doc.pdf", langs=["en", "fr"], nth=0, chunk_size=10
)
extractor.extract()
# or retrieve parsed dates programmatically
dates = extractor.get_dates()
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

### MIT License

```text
MIT License

Copyright (c) 2025 Dave Lane

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## Legal Disclaimer

The software is provided "as is", without warranty of any kind, express or implied. In no event shall the authors be liable for any claim, damages, or other liability...

---

*Powered in part by ChatGPT*
