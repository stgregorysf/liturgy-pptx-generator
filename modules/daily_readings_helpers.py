from dataclasses import dataclass
from datetime import datetime
import logging
import re
import requests
from typing import List, Optional

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


@dataclass
class GospelMetadata:
    start_chapter: int
    start_verse: int
    end_chapter: int
    end_verse: int
    book_code: str

def get_dailyreadings_url(target_date: datetime.datetime) -> Optional[str]:
    """
        Fetches the hdid for the Liturgy and returns the dailyreadings.am URL.

        For example 2026-11-22 returns
        https://dailyreadings.am/v3/getHourlyText.php?hdate=1515342&hour=3558
    """
    index_url = "https://dailyreadings.am/v3/index.php"
    params = {'year': target_date.year, 'month': target_date.month, 'day': target_date.day, 'lang': 1}
    
    try:
        response = requests.get(index_url, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for item in root.findall('cp_item'):
            if item.get('id') == "3558":
                hdid = item.get('hdid')
                return f"https://dailyreadings.am/v3/getHourlyText.php?hdate={hdid}&hour=3558"
    except Exception as e:
        logging.info(f"Error fetching index: {e}")
    return None

def get_sharagan_before_tapor(soup: BeautifulSoup) -> Optional[str]:
    # find the specific <b> tag containing the title
    title_tag = soup.find(lambda tag: tag.name == 'b' and 'Շարական խնկարկութեան սրբոյ պատարագին' in tag.get_text())
    if not title_tag:
        return None
        
    # traverse subsequent siblings directly from the title tag
    content_parts = []
    current = title_tag.next_sibling
    
    while current:
        current_str = str(current.get_text())
        
        # Stop precisely when reaching the deacon prompt <i>Սրկ.</i>
        if 'Սրկ.' in current_str:
            break
            
        content_parts.append(current_str)
        current = current.next_sibling
        
    # join and clean up the extracted HTML content
    result_html = "".join(content_parts).strip()
    
    return result_html


def get_sharagan_before_reading(soup: BeautifulSoup) -> Optional[str]:
    # 1. Find the subtitle font tag
    font_tag = soup.find('font', color='#808080')
    if not font_tag:
        return None
        
    # Get the parent <p> tag to start from its position
    start_element = font_tag.parent
    
    # Traverse subsequent siblings until the "Սրկ." / "Օրհնեա՛" line
    content_parts = []
    current = start_element.next_sibling
    
    while current:
        # Convert current element to string to check for the stop condition
        # current_str = str(current.get_text())
        current_str = str(current.get_text())
        
        # Stop before reaching the deacon's prompt
        if 'Օրհնեա՛' in current_str or 'Սրկ.' in current_str:
            break
            
        content_parts.append(current_str)
        current = current.next_sibling
        
    result_html = "".join(content_parts).strip()
    
    return result_html


def get_bible_reading_metadata(full_text, book_code) -> Optional[GospelMetadata]:
    # bible verses look like (գլ. 2.23-3.12), or (գլ. 5.19-30)
    ref_match = re.search(r"\(գլ\.\s*(\d+)\.(\d+)(?:-(?:(\d+)\.)?(\d+))?\)", full_text)
    if not ref_match: return None

    start_chapter = int(ref_match.group(1))
    start_verse = int(ref_match.group(2))
    
    # Logic to handle if the end reference has a dot (cross-chapter) or just a number
    if ref_match.group(3) and ref_match.group(4):
        # Case: 2.23-3.12 -> End Chapter 3, End Verse 12
        end_chapter = int(ref_match.group(3))
        end_verse = int(ref_match.group(4))
    elif ref_match.group(4):
        # Case: 1.1-17 -> End Chapter 1 (same as start), End Verse 17
        end_chapter = start_chapter
        end_verse = int(ref_match.group(4))
    else:
        # Case: single verse
        end_chapter = start_chapter
        end_verse = start_verse

    return GospelMetadata(
        book_code=book_code,
        start_chapter=start_chapter,
        start_verse=start_verse,
        end_chapter=end_chapter,
        end_verse=end_verse
    )


def get_letter_metadata(soup: BeautifulSoup) -> Optional[GospelMetadata]:
    target_p = None
    for p in soup.find_all("p"):
        if "թղթոյն է ընթերցուածս" in p.get_text():
            target_p = p

    if not target_p: return None

    full_text = target_p.get_text(strip=True)

    # remove the parenthesis from
    # Պօղոսի առաքելոյն ի Թեսաղոնիկեցւոց առաջին թղթոյն է ընթերցուածս(գլ. 1.1-10)
    book_code = full_text.split("(")[0]

    return get_bible_reading_metadata(full_text, book_code)


def get_gospel_metadata(soup: BeautifulSoup) -> Optional[GospelMetadata]:
    gospel_map = set(["Մատթէոսի", "Մարկոսի", "Ղուկասու", "Յովհաննու"])
    target_p = None
    for p in soup.find_all("p"):
        if "ըստ" in p.get_text() and "Սրբոյ Աւետարանիս" in p.get_text():
            target_p = p

    if not target_p: return None
    full_text = target_p.get_text(strip=True)
    
    book_code = next((name for name in gospel_map if name in full_text), "Յովհաննու")

    return get_bible_reading_metadata(full_text, book_code)


def get_line_containing_phrase(soup: BeautifulSoup, phrase: str) -> Optional[GospelMetadata]:
    target_p = None
    for p in soup.find_all("p"):
        if phrase in p.get_text():
            target_p = p
            break
    
    if not target_p: return None
    # Replace <br> tags with newlines and split into clean lines
    lines = [line.strip() for line in target_p.get_text(separator="\n").splitlines() if line.strip()]
    
    for line in lines:
        if phrase in line:
            return line
    return None
