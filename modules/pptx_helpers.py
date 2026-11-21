import datetime
import os
from copy import deepcopy

import typing

import googletrans
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from modules import transliteration
from modules.util import VersePair


PPTX_TEMPLATE_PATH = os.path.join(os.getcwd(), 'static', 'template.pptx')


def get_template_dimensions():
    """Retrieves the exact width and height of the master template."""
    try:
        temp_prs = Presentation(PPTX_TEMPLATE_PATH)
        return temp_prs.slide_width, temp_prs.slide_height
    except Exception:
        return Inches(10), Inches(5.625)


def apply_slide_template(slide, width, height):
    """Applies the specific OneDrive dark blue and red left border scaled to full slide dimensions."""
    # background: #1F4E79 (31, 78, 121)
    background = slide.shapes.add_shape(1, 0, 0, width, height)
    background.fill.solid()
    background.fill.fore_color.rgb = RGBColor(31, 78, 121)
    background.line.fill.background()

    # red left border
    border = slide.shapes.add_shape(1, 0, 0, width * 0.01, height)
    border.fill.solid()
    border.fill.fore_color.rgb = RGBColor(255, 0, 0)
    border.line.fill.background()


def add_text_box(
    slide,
    top_ratio,
    text,
    font_size=32,
    is_italic=False,
    color=(255, 255, 255),
    slide_width=Inches(10),
    slide_height=Inches(5.625),
):
    """Helper to add styled text boxes dynamically scaled to the template's dimensions."""
    left = slide_width * 0.05
    width = slide_width * 0.90
    height = slide_height * 0.25
    top_pos = slide_height * top_ratio

    txBox = slide.shapes.add_textbox(left, top_pos, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True

    scale_factor = slide_height / Inches(5.625)
    scaled_font_size = max(10, int(font_size * scale_factor))

    p = tf.paragraphs[0]
    p.text = text
    p.font.name = "Arial"
    p.font.size = Pt(scaled_font_size)
    p.font.italic = is_italic
    p.font.color.rgb = RGBColor(*color)
    p.alignment = PP_ALIGN.LEFT
    return txBox


def get_gospel_reference(start_ref, current_ref):
    """Formats the reference as 'BOOK CH:VS' or 'BOOK CH:VS-VS'."""
    if start_ref == current_ref:
        return start_ref

    end_verse = current_ref.split(":")[-1]
    start_ref_open_bracket = start_ref.replace("]", "")
    return f"{start_ref_open_bracket}-{end_verse}"


def flush_to_slide(
    prs, w, h, top_right_ref, header_text, arm_list, phonetic_list, niv_list
):
    """Unified helper to flush text lines to a presentation slide."""
    if not arm_list:
        return

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_template(slide, w, h)

    # top right reference
    ref_box = add_text_box(
        slide,
        0.035,
        top_right_ref,
        font_size=12,
        color=(255, 255, 255),
        slide_width=w,
        slide_height=h,
    )
    ref_box.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT

    # section header (underlined)
    header_box = add_text_box(
        slide, 0.071, header_text, font_size=18, slide_width=w, slide_height=h
    )
    header_box.text_frame.paragraphs[0].font.underline = True

    # armenian text
    combined_arm = " ".join(arm_list)
    add_text_box(
        slide, 0.142, combined_arm, font_size=18, slide_width=w, slide_height=h
    )

    # transliteration, armenian as english
    combined_phonetic = " ".join(phonetic_list)
    add_text_box(
        slide,
        0.426,
        combined_phonetic,
        font_size=18,
        color=(255, 255, 0),
        slide_width=w,
        slide_height=h,
    )

    # english
    combined_niv = " ".join(niv_list)
    add_text_box(
        slide,
        0.711,
        combined_niv,
        font_size=18,
        is_italic=True,
        slide_width=w,
        slide_height=h,
    )


def create_sharagan_verse_pairs(sharagan_text: str):
    """Chunks sharagan text into ~50 character segments and generates phonetic and NIV translations."""
    words = [s.strip() for s in sharagan_text.split(" ") if s.strip()]
    pairs = []
    current_chunk = []
    current_len = 0

    for word in words:
        word_len = len(word)
        if current_len + word_len > 50 and current_chunk:
            arm_text = " ".join(current_chunk)
            try:
                phonetic = transliteration.transliterate(arm_text)
            except Exception:
                phonetic = ""
            try:
                niv = googletrans.Translator().translate(arm_text).text
            except Exception:
                niv = ""

            pairs.append(
                VersePair(
                    reading_code="",
                    armenian_text=arm_text,
                    transliterated_text=phonetic,
                    niv_text=niv,
                )
            )
            current_chunk = []
            current_len = 0

        current_chunk.append(word)
        current_len += word_len + 1

    if current_chunk:
        arm_text = " ".join(current_chunk)
        try:
            phonetic = transliteration.transliterate(arm_text)
        except Exception:
            phonetic = ""
        try:
            niv = googletrans.Translator().translate(arm_text).text
        except Exception:
            niv = ""

        pairs.append(
            VersePair(
                reading_code="",
                armenian_text=arm_text,
                transliterated_text=phonetic,
                niv_text=niv,
            )
        )

    return pairs


def generate_reading_pptx(
    target_date: datetime.datetime,
    verse_pairs: typing.List[typing.Any],
    suffix="_generated_reading.pptx",
    header_text="ՍՐԿ/Deacon",
    is_sharagan=False,
    title_reference="",
):
    prs = Presentation()
    w, h = get_template_dimensions()
    prs.slide_width = w
    prs.slide_height = h

    current_arm = []
    current_phonetic = []
    current_niv = []
    current_char_count = 0
    gospel_verse_start = None
    last_seen_verse = None
    slide_counter = 1

    def process_flush():
        nonlocal slide_counter
        if is_sharagan:
            slide_ref = f"{title_reference} ({slide_counter})"
            slide_counter += 1
        else:
            slide_ref = get_gospel_reference(gospel_verse_start, last_seen_verse)

        flush_to_slide(
            prs,
            w,
            h,
            slide_ref,
            header_text,
            current_arm,
            current_phonetic,
            current_niv,
        )

    for pair in verse_pairs:
        if not gospel_verse_start:
            gospel_verse_start = pair.reading_code

        arm_entry = pair.armenian_text

        # if current_char_count + len(arm_entry) > 150:
        if current_char_count + len(arm_entry) > 250 or pair.first_on_slide:
            process_flush()
            current_arm, current_phonetic, current_niv = [], [], []
            current_char_count = 0
            gospel_verse_start = pair.reading_code

        current_arm.append(arm_entry)
        current_phonetic.append(pair.transliterated_text)
        current_niv.append(pair.niv_text)
        current_char_count += len(arm_entry)
        last_seen_verse = pair.reading_code

    if current_arm:
        process_flush()

    ts = target_date.strftime("%Y%m%d")
    os.makedirs(os.path.join(os.getcwd(), ts), exist_ok=True)
    file_name = os.path.join(os.getcwd(), ts, ts + suffix)
    prs.save(file_name)
    return file_name


def insert_slides_into_template(
    target_date,
    sharagan_tapor_path,
    sharagan_reading_path,
    alleluia_reading_path,
    letter_path,
    gospel_path,
):
    """Inserts generated presentation slides into the master template at matching positions."""
    prs = Presentation(PPTX_TEMPLATE_PATH)
    xml_slides = prs.slides._sldIdLst

    blank_layout = next(
        (layout for layout in prs.slide_layouts if "blank" in layout.name.lower()),
        prs.slide_layouts[0],
    )

    insertions = [
        (gospel_path, 62),
        (alleluia_reading_path, 59),
        (letter_path, 58),
        (sharagan_reading_path, 49),
        (sharagan_tapor_path, 34),
    ]
    insertions.sort(key=lambda x: x[1], reverse=True)

    for src_path, after_slide_num in insertions:
        if not os.path.exists(src_path):
            continue
        src_prs = Presentation(src_path)

        for i, src_slide in enumerate(src_prs.slides):
            dest_slide = prs.slides.add_slide(blank_layout)

            for shape in src_slide.shapes:
                new_el = deepcopy(shape.element)
                dest_slide.shapes._spTree.insert_element_before(new_el, "p:extLst")

            slides_list = list(xml_slides)
            new_slide_item = slides_list[-1]
            xml_slides.remove(new_slide_item)
            xml_slides.insert(after_slide_num + i, new_slide_item)

    ts = target_date.strftime("%Y%m%d")
    os.makedirs(os.path.join(os.getcwd(), ts), exist_ok=True)
    final_output = os.path.join(os.getcwd(), ts, f"{ts}_final_service.pptx")
    prs.save(final_output)
    return final_output
