"""Constants for the docbuild package.
"""
LINE = "LINE"
WORD = "WORD"

BBOX_PATTERN = "\s*bbox\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9]+)"

# The factor of which we'll multiply the paragraph bounding box when looking for intersections with other paragraphs.
PARAGRAPH_VERTICAL_SCALE = 1.1
PARAGRAPH_HORIZONTAL_SCALE = 1
PARAGRAPH_HORIZONTAL_SCALE_FOR_LINES = 100
PARAGRAPH_VERTICAL_SCALE_FOR_LINES = 0.5

SORT_LINE_VERTICAL_SCALE = 0.5

