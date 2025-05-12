"""Main entry point for pdfdateextract"""

import argparse
import sys
from importlib.metadata import version

from pdfdateextract._util import MyException
from pdfdateextract.extract_date import ExtractDate


class Pdfdateextract:
    """Main class"""

    parser = None
    version = None
    verbose = False

    def __init__(self):
        pass

    def make_cmd_line_parser(self):
        """Set up the command line parser"""
        self.parser = argparse.ArgumentParser(
            description="Extract dates (in any language) from a PDF file."
        )
        self.parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=version("pdfdateextract"),
            help="Print the version number",
        )
        self.parser.add_argument(
            "-v", "--verbose", action="store_true", default=False, help="Verbose output"
        )
        # Positional argument for PDF path
        self.parser.add_argument("pdf", help="Path to the PDF file to process.")

        self.parser.add_argument(
            "-l",
            "--langs",
            nargs="+",
            default=None,
            help=(
                "Space-separated list of ISO 639-1 language codes to restrict parsing "
                "(e.g. en fr de). Omit to auto-detect all supported languages."
            ),
        )
        self.parser.add_argument(
            "-n",
            "--nth",
            type=int,
            default=0,
            help="0 to print all dates (default), or n to print only the nth date (1-based index).",
        )
        self.parser.add_argument(
            "-c",
            "--chunk-size",
            type=int,
            default=10,
            help="Number of pages to process per chunk (default: 10).",
        )
        args = self.parser.parse_args()

        extractor = ExtractDate(args.pdf, args.langs, args.nth, args.chunk_size)
        extractor.extract()

    def parse_args(self):
        """Parse the command line arguments"""
        args = self.parser.parse_args()

        self.verbose = args.verbose

    def run(self):
        """Main entry point"""
        self.make_cmd_line_parser()
        self.parse_args()


def main():
    """Main entry point"""
    try:
        Pdfdateextract().run()
    except MyException as e:
        print(e.msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
