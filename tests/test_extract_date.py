"""Test parsing dates from PDF text."""

from datetime import datetime
from pathlib import Path

import pytest
from fpdf import FPDF

from pdfdateextract.extract_date import ExtractDate


def create_pdf_with_text(tmp_path: Path, text: str) -> Path:
    """
    Helper to create a single-page PDF containing the given text.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=text)
    output_path = tmp_path / "temp.pdf"
    pdf.output(str(output_path))
    return output_path


@pytest.mark.parametrize(
    "date_text, langs, expected",
    [
        ("Date: 12/05/2025", None, datetime(2025, 5, 12)),
        ("Date: May 12, 2025", ["en"], datetime(2025, 5, 12)),
        ("Date: December 1 2025", ["en"], datetime(2025, 12, 1)),
        ("Date : 19/04/2025", ["fr"], datetime(2025, 4, 19)),
        ("Date : 5 mai 2025", ["fr"], datetime(2025, 5, 5)),
        ("Date : 1 décembre 2025", ["fr"], datetime(2025, 12, 1)),
        ("Datum: 31.07.2025", ["de"], datetime(2025, 7, 31)),
        ("Datum: 15 Aug 2025", ["de"], datetime(2025, 8, 15)),
        ("Datum: 2 November 2025", ["de"], datetime(2025, 11, 2)),
        ("Fecha: 23/09/2025", ["es"], datetime(2025, 9, 23)),
        ("Fecha: 7 oct 2025", ["es"], datetime(2025, 10, 7)),
        ("Fecha: 14 octubre 2025", ["es"], datetime(2025, 10, 14)),
    ],
)
def test_extract_date_parsing(tmp_path, date_text, langs, expected):
    """Test that ExtractDate finds and parses the expected date."""
    pdf_path = create_pdf_with_text(tmp_path, date_text)

    extractor = ExtractDate(str(pdf_path), langs=langs, nth=0, chunk_size=1)
    extractor.extract()

    assert extractor.dates, f"No dates found in PDF for text: '{date_text}'"

    snippet, dt = extractor.dates[0]
    assert (dt.year, dt.month, dt.day) == (expected.year, expected.month, expected.day), (
        f"Parsed {dt.date()} but expected {expected.date()} " f"for snippet '{snippet}'"
    )


if __name__ == "__main__":
    pytest.main()
