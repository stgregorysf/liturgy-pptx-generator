import argparse
from datetime import datetime
import logging

import bs4
import requests

from modules import daily_readings_helpers
from modules import dzaghig
from modules import bible_com_helpers
from modules import pptx_helpers


logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)

WHATSAPP_MESSAGE_TEMPLATE = """
Ասիկա այսօրուան Daily Worship-ի էջն է։
{dailyreadings_url}

{apostolic_letter}

{before_reading}

{bible_verse}

{bowing_reason}
"""


def generate_slides(soup, target_date, nor_dzaghig):
    extracted_gospel_reading = daily_readings_helpers.get_gospel_metadata(soup)
    if not extracted_gospel_reading:
        logging.info("Could not parse metadata."); return
    
    extracted_letter_reading = daily_readings_helpers.get_letter_metadata(soup)
    logging.warning(f"parsed metadata is {'\n'.join([str(extracted_gospel_reading), str(extracted_letter_reading)])}")
    input('continue? [enter or ^C]')

    if nor_dzaghig:
        sharagan_tapor_pairs = dzaghig.NOR_DZAGHIG
    else:
        sharagan_before_tapor = daily_readings_helpers.get_sharagan_before_tapor(soup)
        sharagan_tapor_pairs = pptx_helpers.create_sharagan_verse_pairs(sharagan_before_tapor)

    sharagan_tapor_pptx = pptx_helpers.generate_reading_pptx(
        target_date,
        sharagan_tapor_pairs,
        suffix="_tapor.pptx",
        header_text="ՇԱՐԱԿԱՆ / Sharagan",
        is_sharagan=True,
        title_reference='Շարական խնկարկութեան սրբոյ պատարագին'
    )

    sharagan_before_reading = daily_readings_helpers.get_sharagan_before_reading(soup)
    sharagan_reading_pairs = pptx_helpers.create_sharagan_verse_pairs(sharagan_before_reading)
    sharagan_reading_pptx = pptx_helpers.generate_reading_pptx(
        target_date,
        sharagan_reading_pairs,
        suffix="_reading.pptx",
        header_text="ՇԱՐԱԿԱՆ / Sharagan",
        is_sharagan=True,
        title_reference='ՃԱՇՈՒ ՇԱՐԱԿԱՆ'
    )

    alleluia_before_reading = daily_readings_helpers.get_line_containing_phrase(soup, 'Ալէլուիա, ալէլուիա:')
    alleluia_reading_pairs = pptx_helpers.create_sharagan_verse_pairs(alleluia_before_reading)
    alleluia_reading_pptx = pptx_helpers.generate_reading_pptx(
        target_date,
        alleluia_reading_pairs,
        suffix="_generated_alleluia.pptx",
        header_text="ՍՐԿ/Deacon",
        is_sharagan=False
    )

    letter_verse_pairs = bible_com_helpers.get_letter_verse_pairs(extracted_letter_reading)
    letter_pptx = pptx_helpers.generate_reading_pptx(
        target_date,
        letter_verse_pairs,
        suffix="_generated_letter.pptx",
        header_text="ՍՐԿ/Deacon",
        is_sharagan=False
    )

    gospel_verse_pairs = bible_com_helpers.get_gospel_verse_pairs(extracted_gospel_reading)
    gospel_pptx = pptx_helpers.generate_reading_pptx(
        target_date,
        gospel_verse_pairs,
        suffix="_generated_reading.pptx",
        header_text="ՍՐԿ/Deacon",
        is_sharagan=False
    )
    
    final_presentation = pptx_helpers.insert_slides_into_template(
        target_date,
        sharagan_tapor_pptx, 
        sharagan_reading_pptx, 
        alleluia_reading_pptx,
        letter_pptx,
        gospel_pptx,
    )
    
    logging.info("See final combined presentation at:\n%s", final_presentation)

def main():
    parser = argparse.ArgumentParser(description='Fetch Liturgy verse by verse.')
    parser.add_argument('date', help='Date in YYYY-MM-DD format')
    parser.add_argument('--nor_dzaghig', help='if set, song before tapor is this, else get song from dailyreadings.am', action='store_true')
    parser.add_argument('--whatsapp', help='if set, generate copypasta for whatsapp groupchat', action='store_true')
    args = parser.parse_args()

    try:
        target_date = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        logging.info("Error: Use YYYY-MM-DD"); return

    daily_url = daily_readings_helpers.get_dailyreadings_url(target_date)
    if not daily_url:
        logging.info("Liturgy not found for " + args.date); return

    logging.warning(f"daily readings url is {daily_url}")

    response = requests.get(daily_url)
    if response.status_code != 200:
        logging.error(f'url responded with {response.status_code}')
        return None
    soup = bs4.BeautifulSoup(response.content, 'html.parser')

    if args.whatsapp:
        meta = daily_readings_helpers.get_gospel_metadata(soup)
        if not meta:
            logging.info("Could not parse metadata."); return
        bible_verse = f'{meta.book_code} {meta.start_chapter}:{meta.start_verse} - {meta.end_chapter}:{meta.end_verse}'

        meta = daily_readings_helpers.get_letter_metadata(soup)
        apostolic_letter = f'{meta.book_code} {meta.start_chapter}:{meta.start_verse} - {meta.end_chapter}:{meta.end_verse}'
        logging.info(WHATSAPP_MESSAGE_TEMPLATE.format(
            dailyreadings_url=daily_url,
            apostolic_letter=apostolic_letter,
            before_reading=daily_readings_helpers.get_line_containing_phrase(soup, 'Ալէլուիա, ալէլուիա:'),
            bible_verse=bible_verse,
            bowing_reason=daily_readings_helpers.get_line_containing_phrase(soup, 'Օրհնեալ, գովեալ եւ փառաւորեալ, հրաշալի եւ աստուածազարդ'),
        ))
        return

    generate_slides(soup, target_date, args.nor_dzaghig)


if __name__ == "__main__":
    main()
