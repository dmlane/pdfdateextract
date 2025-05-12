#!/usr/bin/env python3
"""
Module: extract_date

Provides ExtractDate for multilingual PDF date extraction.
"""
import logging
import re
import warnings
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Optional, Tuple

import pdfplumber
from dateparser import parse as date_parse
from dateparser.conf import Settings
from pdfplumber.utils.exceptions import PdfminerException

# Determine log directory using platformdirs
from platformdirs import user_log_dir  # type: ignore
from pypdf import PdfReader
from pypdf.errors import PdfReadError

# Configure logger to output to user-specific log file with rotation
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


log_dir = Path(user_log_dir("pdfdateextract", appauthor=False))
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "extract_date.log"

# Set up rotating file handler
rotating_handler = RotatingFileHandler(
    filename=log_file,
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
rotating_handler.setLevel(logging.DEBUG)
rotating_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s"))
logger.addHandler(rotating_handler)

# Silence pdfplumber/pdfminer cropbox messages via logging
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Suppress CropBox missing messages
warnings.filterwarnings("ignore", message="CropBox missing from /Page.*")

# Patterns for date extraction
MONTH_WORD_PATTERN = r"[A-Za-zÀ-ÖØ-öø-ÿ]+"
COMBINED_PATTERN = re.compile(
    rf"\b(?:"
    rf"\d{{1,2}}[./-]\d{{1,2}}[./-]\d{{2,4}}|"  # 31/07/2025
    rf"\d{{4}}[./-]\d{{1,2}}[./-]\d{{1,2}}|"  # 2025-07-31
    rf"\d{{1,2}}\s+{MONTH_WORD_PATTERN},?\s+\d{{4}}|"  # 5 mai 2025
    rf"{MONTH_WORD_PATTERN}\s+\d{{1,2}},?\s+\d{{4}}"  # May 5, 2025
    rf")\b",
    re.UNICODE,
)

# DateParser settings
DATE_SETTINGS = Settings()
DATE_SETTINGS.strict_parsing = True
DATE_SETTINGS.date_order = "DMY"
DATE_SETTINGS.prefs_day_of_month = "first"


class ExtractDate:
    """
    ExtractDate class for PDF date extraction.

    Public methods:
        extract(): run extraction.
        get_dates(): return parsed dates.

    Properties:
        dates: list of (snippet, datetime) tuples.
    """

    def __init__(
        self,
        pdf_path: str,
        langs: Optional[List[str]] = None,
        nth: int = 0,
        chunk_size: int = 10,
    ) -> None:
        self.pdf_path = pdf_path
        self.langs = langs
        self.nth = nth
        self.chunk_size = chunk_size
        self._dates: List[Tuple[str, datetime]] = []

    @property
    def dates(self) -> List[Tuple[str, datetime]]:
        """Return list of parsed dates (snippet, datetime)."""
        return self._dates.copy()

    def extract(self) -> None:
        """
        Run extraction process on PDF, populating dates.

        Falls back to pypdf on parse errors.
        """
        fallback = PdfReader(self.pdf_path)
        with pdfplumber.open(self.pdf_path) as pdf:
            total = len(pdf.pages)
            logger.debug("Processing %d pages in chunks of %d", total, self.chunk_size)
            for start in range(0, total, self.chunk_size):
                pages = list(range(start, min(start + self.chunk_size, total)))
                text_block = self._read_pages(pdf, fallback, pages)
                if not text_block:
                    continue
                candidates = self._find_candidates(text_block)
                self._parse_candidates(candidates)
                if self.nth and len(self._dates) >= self.nth:
                    break
        self._print_results()
        logger.info("Extraction complete. %d dates found.", len(self._dates))

    def get_dates(self) -> List[Tuple[str, datetime]]:
        """Return list of (snippet, datetime) tuples."""
        return self._dates.copy()

    def _read_pages(
        self,
        pdf: pdfplumber.PDF,
        fallback: PdfReader,
        pages: List[int],
    ) -> str:
        """Read text from specified pages, handling parse errors."""
        texts: List[str] = []
        for idx in pages:
            try:
                txt = pdf.pages[idx].extract_text() or ""
            except PdfminerException as exc:
                logger.debug("Page %d parse error, skipping pdfplumber: %s", idx + 1, exc)
                try:
                    txt = fallback.pages[idx].extract_text() or ""
                except PdfReadError as exc2:
                    logger.debug("Fallback parse error on page %d: %s", idx + 1, exc2)
                    continue
            texts.append(txt)
        return "\n".join(texts)

    def _find_candidates(self, text: str) -> List[str]:
        """Identify unique date-like snippets in the given text."""
        seen = set()
        result: List[str] = []
        for match in COMBINED_PATTERN.finditer(text):
            snippet = match.group()
            if snippet not in seen:
                seen.add(snippet)
                result.append(snippet)
        return result

    def _parse_candidates(self, candidates: List[str]) -> None:
        """
        Parse candidate strings into datetimes, respecting `nth` limit.
        Numeric dates (DD/MM/YYYY or YYYY-MM-DD) are parsed manually
        to enforce DMY or YMD ordering.
        """
        for snippet in candidates:
            dt = None
            # Manual parse for strictly numeric dates (DD/MM/YYYY)
            m_dmy = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})", snippet)
            # Manual parse for ISO‐style (YYYY-MM-DD)
            m_ymd = re.fullmatch(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", snippet)
            if m_dmy:
                d_str, m_str, y_str = m_dmy.groups()
                dt = datetime(int(y_str), int(m_str), int(d_str))
            elif m_ymd:
                y_str, m_str, d_str = m_ymd.groups()
                dt = datetime(int(y_str), int(m_str), int(d_str))
            else:
                # Fallback to dateparser for anything else
                if self.langs is not None:
                    dt = date_parse(
                        snippet,
                        settings=DATE_SETTINGS,
                        languages=self.langs,
                    )
                else:
                    dt = date_parse(
                        snippet,
                        settings=DATE_SETTINGS,
                    )
            if dt:
                self._dates.append((snippet, dt))
                if self.nth and len(self._dates) >= self.nth:
                    break

    def _print_results(self) -> None:
        """Print extracted dates to stdout."""
        if not self._dates:
            print("No dates found.")
            return
        if not self.nth:
            for idx, (snippet, dt) in enumerate(self._dates, start=1):
                print(f"{idx}. '{snippet}' -> {dt.isoformat()}")
        else:
            index = self.nth - 1
            if 0 <= index < len(self._dates):
                _, dt = self._dates[index]
                print(dt.isoformat())
            else:
                print(f"Error: requested #{self.nth} but only {len(self._dates)} found")
