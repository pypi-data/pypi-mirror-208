from .text_block import Page, Word
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
import shutil
import io


def get_font_size(
    canvas: object, text: str, font_name: str, width: float
) -> float:
    width_1 = canvas.stringWidth(text, font_name, 1)
    ratio = width / width_1
    return ratio


def get_canvas_mode(invisible: bool) -> int:
    return 3 if invisible else 1


def draw_word_on_canvas(
    word: Word,
    can: Canvas,
    page_width: float,
    page_height: float,
    mode: int,
):
    bb = word.bounding_box
    text = word.text
    center = bb.get_center()
    x_center, y_center = center.get_x(), center.get_y()

    font_size = get_font_size(
        canvas=can,
        text=text,
        font_name="Courier",
        width=page_width * bb.get_width(),
    )
    can.setFont("Courier", font_size)
    can.drawCentredString(
        x_center * page_width,
        y_center * page_height,
        text,
        mode=mode,
    )


def save_searchable_pdf(
    document_page: Page,
    in_pdf_path: str,
    out_pdf_path: str,
    invisible: bool = True,
):
    words = list(document_page.get_all(Word))
    if not words:
        shutil.copyfile(in_pdf_path, out_pdf_path)
        return
    with open(in_pdf_path, "rb") as f:
        existing_pdf = PdfReader(f)
        page = existing_pdf.pages[0]

        output = PdfWriter()

        page_width = float(page["/MediaBox"][2]) - float(page["/MediaBox"][0])
        page_height = float(page["/MediaBox"][3]) - float(page["/MediaBox"][1])

        packet = io.BytesIO()
        can = Canvas(packet, pagesize=letter)
        mode = get_canvas_mode(invisible)

        for word in words:
            draw_word_on_canvas(word, can, page_width, page_height, mode)
        can.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        with open(out_pdf_path, "wb") as f:
            output.write(f)
