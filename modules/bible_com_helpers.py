import logging
import os
from pathlib import Path
import typing

from modules import transliteration
from modules.util import VersePair

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)

# Define your root directory
ROOT_DIR = Path(os.path.join(os.getcwd(), "unicode"))


def get_text_using_file(txt_file_path, line_number: int):
    """
    Attempts to read a specific verse from a local text file.
    Assuming: ./book_code/chapter.txt
    """
    if not txt_file_path.exists():
        return "[Text not found]"

    # Read all lines; lines are 1-indexed in your files
    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # Check if verse exists in this file (verse 1 = index 0)
    if 0 < line_number <= len(lines):
        return lines[line_number - 1]
    
    return "[Text not found]"


def get_gospel_verse_pairs(meta) -> typing.Iterable[VersePair]:
    verse_pairs = []
    
    current_chapter = meta.start_chapter
    current_verse = meta.start_verse
    
    mapping = {
        "Մատթէոսի":"matthew", 
        "Մարկոսի":"mark", 
        "Ղուկասու":"luke", 
        "Յովհաննու":"john",
        "Պօղոսի առաքելոյն ի Հռովմայեցւոց թղթոյն է ընթերցուածս": "romans",
        "Պօղոսի առաքելոյն ի Կորնթացւոց առաջին թղթոյն է ընթերցուածս": "corinthians_1",
        "Պօղոսի առաքելոյն ի Կորնթացւոց երկրորդ թղթոյն է ընթերցուածս": "corinthians_2",
        "Պօղոսի առաքելոյն ի Գաղատացւոց թղթոյն է ընթերցուածս": "galatians",
        "Պօղոսի առաքելոյն ի Եփեսացւոց թղթոյն է ընթերցուածս": "Ephesians",
        "Պօղոսի առաքելոյն ի Փիլիպպեցւոց թղթոյն է ընթերցուածս": "philippians",
        "Պօղոսի առաքելոյն ի Կողոսացւոց թղթոյն է ընթերցուածս": "colossians",
        "Պօղոսի առաքելոյն ի Թեսաղոնիկեցւոց առաջին թղթոյն է ընթերցուածս": "thessalonians_1",
        "Պօղոսի առաքելոյն ի Թեսաղոնիկեցւոց երկրորդ թղթոյն է ընթերցուածս": "thessalonians_2",
        "Պօղոսի առաքելոյն առ Տիմոթէոս առաջին թղթոյն է ընթերցուածս": "timothy_1",
        "Պօղոսի առաքելոյն առ Տիմոթէոս երկրորդ թղթոյն է ընթերցուածս": "timothy_2",
        "Պօղոսի առաքելոյն առ Տիտոս թղթոյն է ընթերցուածս": "titus",
        "Պօղոսի առաքելոյն առ Փիլիմոն թղթոյն է ընթերցուածս": "philemon",
        "Պօղոսի առաքելոյն ի Եբրայեցւոց թղթոյն է ընթերցուածս": "hebrews",
        "Յակոբու առաքելոյն ի Կաթողիկեայ թղթոյն է ընթերցուածս": "james",
        "Պետրոսի առաքելոյն առաջին ի Կաթողիկեայ թղթոյն է ընթերցուածս": "peter_1",
        "Պետրոսի առաքելոյն երկրորդ ի Կաթողիկեայ թղթոյն է ընթերցուածս": "peter_2",
        "Յուդայի առաքելոյն ի Կաթողիկեայ թղթոյն է ընթերցուածս": "jude",
    }
    while True:
        # 1. Get Armenian text from your local folder
        armenian_code = meta.book_code
        real_code = mapping[armenian_code]

        txt_file_path = ROOT_DIR / "armenian" / real_code / f"{current_chapter}.txt"
        arm_text = get_text_using_file(txt_file_path, current_verse)

        txt_file_path = ROOT_DIR / "nkjv" / real_code / f"{current_chapter}.txt"
        niv_text = get_text_using_file(txt_file_path, current_verse)

        nkjv_code_nice = real_code[:1].upper() + real_code[1:].lower()

        if "_" in nkjv_code_nice:
            # handle case like Peter_1, make it 1 Peter
            name, number = nkjv_code_nice.split("_")
            nkjv_code_nice = f'{number} {name}'

        if ' է ընթերցուածս' in armenian_code:
            # remove this suffix from the armenian code
            armenian_code = armenian_code.replace(' է ընթերցուածս', '')
        reading_code = f"{armenian_code}/{nkjv_code_nice} {current_chapter}:{current_verse}"

        
        if arm_text == "[Text not found]":
            # Check if we should try the next chapter
            if current_chapter < meta.end_chapter:
                current_chapter += 1
                current_verse = 1
                continue
            else:
                # Reached the end of the requested range
                break

        try:
            stg_transliteration = transliteration.transliterate(
                arm_text
            )
        except Exception:
            stg_transliteration = ''
        
        verse_pairs.append(VersePair(
            reading_code=reading_code,
            armenian_text=arm_text,
            transliterated_text=stg_transliteration,
            niv_text=niv_text,
        ))

        if current_chapter == meta.end_chapter and current_verse == meta.end_verse:
            break

        current_verse += 1

    return verse_pairs


def get_letter_verse_pairs(meta):
    result = [
        VersePair(
            reading_code="Psalms 65:1",
            armenian_text="Ալէլուիա, ալէլուիա: Քեզ վայելէ օրհնութիւն, Աստուած, ի Սիոն, եւ քեզ տացին աղօթք յԵրուսաղէմ։",
            transliterated_text=transliteration.transliterate("Ալէլուիա, ալէլուիա: Քեզ վայելէ օրհնութիւն, Աստուած, ի Սիոն, եւ քեզ տացին աղօթք յԵրուսաղէմ։"),
            niv_text="Praise awaits you, our God, in Zion;to you our vows will be fulfilled.",
        )
        # todo add "the reading is from..."/առաքելոյն թղթոյն է ընթերցուածս
    ]
    reading = get_gospel_verse_pairs(meta)
    if reading:
        # put the actual reading on its own slide
        reading[0].first_on_slide = True
    result.extend(reading)
    return result
