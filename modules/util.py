from dataclasses import dataclass


@dataclass
class VersePair:
    reading_code: str  # e.g., "JHN 1:5"
    armenian_text: str
    transliterated_text: str
    niv_text: str
    # if true, this pair starts on a new, blank slide
    # any stuff before it is written to a previous slide
    first_on_slide: bool = False
