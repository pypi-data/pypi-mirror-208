"""Constants for the docstruct package.

The delimiter between pages / paragraphs / lines / words  
is represented by the `PAGE_DELIMITER` / `PARAGRAPH_DELIMITER` /  `LINE_DELIMITER`  / `WORD_DELIMITER` constant.
"""

AREA_DELIMITER = "\v"
PAGE_DELIMITER = "\f"
PARAGRAPH_DELIMITER = "\v"
LINE_DELIMITER = "\n"
WORD_DELIMITER = " "
TABLE_DELIMITER = "\t"
CELL_DELIMITER = "\n"
COLUMN_DELIMITER = "\n"

DELIMITERS = {
    "PAGE": PAGE_DELIMITER,
    "PARAGRAPH": PARAGRAPH_DELIMITER,
    "LINE": LINE_DELIMITER,
    "WORD": WORD_DELIMITER,
    "TABLE": TABLE_DELIMITER,
    "CELL": CELL_DELIMITER,
    "COLUMN": COLUMN_DELIMITER,
}

THIN_CHARS = {".", ",", ":", ";", "!"}
CHARACTER_WIDTH_MAP = {"lower": 1, "upper": 1.2, "thin": 0.5, "default": 1}
