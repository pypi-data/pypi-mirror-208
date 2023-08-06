import random
from enum import Enum

from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from .vis_line import VisLineOrientation, VisLine
from .text_block import (
    TextBlock,
    Character,
    Line,
    Page,
    Paragraph,
    Word,
    Table,
    TableCell,
)
from .spatial_grid_indexing import SpatialGrid
from enum import Enum
import random

from .text_block import (
    TableCell,
    Character,
    Line,
    Page,
    Paragraph,
    Table,
    TextBlock,
    Word,
)


class Color(Enum):
    LIGHT_PINK = (255, 182, 193)
    PEACH = (255, 218, 185)
    SKY_BLUE = (135, 206, 235)
    LAVENDER = (230, 230, 250)
    MINT_GREEN = (152, 255, 152)
    LIGHT_YELLOW = (255, 255, 224)
    PALE_GREEN = (152, 251, 152)
    POWDER_BLUE = (176, 224, 230)
    BEIGE = (245, 245, 220)
    CREAM = (255, 253, 208)
    LIGHT_CORAL = (240, 128, 128)
    PALE_TRRQUOISE = (175, 238, 238)
    LIGHT_BLUE_SKY = (135, 206, 250)
    LIGHT_STEEL_BLUE = (176, 196, 222)
    THISTLE = (216, 191, 216)
    GOLD = (255, 215, 0)


COLORS_MAP = {
    Character: "purple",
    Word: "blue",
    Line: "green",
    Paragraph: "yellow",
    Page: "red",
}
WIDTHS_MAP = {
    Character: 1,
    Word: 2,
    Line: 3,
    TableCell: 3,
    Paragraph: 4,
    Table: 4,
    Page: 5,
}


def get_random_rgb_color():
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


class Drawer:
    """
    This class is used to draw bounding boxes of text blocks on an image.
    Example:

    from docstruct import TextBlockDrawer
    image_path = 'foo.png'
    page = Page() ...
    drawer = TextBlockDrawer(image_path)
    drawer.draw(page)
    drawer.show()
    """

    def __init__(self, image_path: Optional[str] = None):
        self.blank_image = image_path is None
        if self.blank_image:
            # create a blank A4 image:
            self.rgb_image = Image.new("RGB", (2480, 3508), (255, 255, 255))
            self.alpha_image = Image.new(
                "RGBA", self.rgb_image.size, (255, 255, 255, 0)
            )
        else:
            self.rgb_image = Image.open(image_path)
            self.alpha_image = Image.new(
                "RGBA", self.rgb_image.size, (255, 255, 255, 0)
            )
        self.width, self.height = self.rgb_image.size
        self.image_drawer = ImageDraw.Draw(self.alpha_image)

    def draw_block_index(self, block: TextBlock, draw_right: bool, draw_top: bool):
        """
        Draws the index of the block on the right top corner of the block.
        """
        bb = block.bounding_box
        top_left = bb.get_top_left()
        left, top = top_left.x * self.width, top_left.y * self.height
        bottom_right = bb.get_bottom_right()
        right, bottom = (
            bottom_right.x * self.width,
            bottom_right.y * self.height,
        )
        top, bottom = self.height - top, self.height - bottom
        hor = right if draw_right else left
        ver = top if draw_top else bottom

        # draw white background:
        self.image_drawer.rectangle(
            [hor - 10, ver - 10, hor + 10, ver + 10], fill="white"
        )

        self.image_drawer.text(
            [hor, ver],
            str(block.get_relative_order()),
            fill="black",
        )

    def get_font_size(self, block: TextBlock) -> int:
        min_font_size = 1
        max_font_size = 1000
        text = str(block)
        width = block.bounding_box.get_width() * self.width
        while max_font_size - min_font_size > 1:
            font_size = (min_font_size + max_font_size) // 2
            font = ImageFont.truetype("Arial.ttf", font_size)
            text_width, _ = self.image_drawer.textsize(text, font=font)
            if text_width <= width:
                min_font_size = font_size
            else:
                max_font_size = font_size
        return min_font_size

    def draw_text_block_text(self, word: Word):
        """
        Draw the character on the image
        """
        top_left = word.bounding_box.get_top_left()
        x, y = (
            top_left.x * self.width,
            self.height - top_left.y * self.height,
        )
        font_size = self.get_font_size(word)
        self.image_drawer.text(
            [x, y],
            str(word),
            fill="black",
            font=ImageFont.truetype("Arial.ttf", font_size),
        )

    def draw_text_block_bounding_box(
        self,
        block: TextBlock,
        color: str = "black",
        fill: bool = False,
        width: int = 1,
    ):
        """
        Draws the bounding box of the text block on the image, not including it's children.
        """
        bbox = block.bounding_box
        bbox.draw_on_image(
            self.image_drawer,
            color,
            self.width,
            self.height,
            fill=fill,
            width=width,
        )
        if self.blank_image:
            self.draw_text_block_text(block)

    def draw(self, block: TextBlock, *to_draw: list[str]):
        """
        Draws the bounding boxes of the text block on the image, including it's children.
        """
        blocks = list(block.post_order_traversal(block))

        if not to_draw:
            to_draw = list((key.__name__.lower() for key in COLORS_MAP))
        for block in blocks:
            name = type(block).__name__.lower()
            if name not in to_draw:
                continue

            if name == "table":
                self.draw_table(block)
            else:
                self.draw_text_block_bounding_box(
                    block,
                    color=COLORS_MAP[type(block)],
                    fill=False,
                    width=WIDTHS_MAP[type(block)],
                )

        for block in blocks:
            name = type(block).__name__.lower()
            if name not in to_draw:
                continue
            if name in [
                "paragraph",
                "table",
            ]:
                self.draw_block_index(block, draw_right=True, draw_top=True)
            elif name == "line":
                self.draw_block_index(block, draw_right=False, draw_top=False)

    def draw_cell(self, cell: TableCell, random_color: bool = False):
        if random_color:
            color = get_random_rgb_color()
        else:
            color = (255, 0, 0)
        color = (*color, 100)
        cell.bounding_box.draw_on_image(
            self.image_drawer, color, self.width, self.height, fill=True
        )
        self.draw_cell_index(cell)
        if self.blank_image:
            words = cell.get_all(Word)
            for word in words:
                self.draw_text_block_text(word)

    def draw_cell_index(self, cell: TableCell):
        """
        Draws the index of the block on the right top corner of the block.
        """
        bb = cell.bounding_box
        top_left = bb.get_top_left()
        left, top = top_left.x * self.width, top_left.y * self.height
        bottom_right = bb.get_bottom_right()
        right, bottom = (
            bottom_right.x * self.width,
            bottom_right.y * self.height,
        )
        top, bottom = self.height - top, self.height - bottom

        self.image_drawer.text(
            [left + 3, top + 3],
            f"({cell.row_index}, {cell.col_index})",
            fill="black",
        )

    def draw_table(self, table: Table, cell_random_color: bool = True):
        for cell in table.cells:
            self.draw_cell(cell, cell_random_color)
        table.bounding_box.draw_on_image(
            self.image_drawer,
            Color.GOLD.value,
            self.width,
            self.height,
            fill=False,
            width=3,
        )

    def draw_vis_line(self, vis_line: VisLine, color: tuple[int, int, int]):
        if vis_line.orientation == VisLineOrientation.HORIZONTAL:
            x0 = vis_line.start * self.width
            x1 = vis_line.end * self.width
            y = self.height - vis_line.axis * self.height
            self.image_drawer.line(
                [x0, y, x1, y],
                fill=color,
                width=3,
            )

        elif vis_line.orientation == VisLineOrientation.VERTICAL:
            y0 = self.height - vis_line.start * self.height
            y1 = self.height - vis_line.end * self.height
            x = vis_line.axis * self.width
            self.image_drawer.line(
                [x, y0, x, y1],
                fill=color,
                width=3,
            )

    def draw_vis_lines(
        self,
        vis_lines: list[VisLine],
        random_color: bool = False,
        draw_index: bool = False,
    ):
        for i, vis_line in enumerate(vis_lines):
            if random_color:
                # color = next(self.rgb_generator)
                color = get_random_rgb_color()
            else:
                color = (255, 0, 0)
            self.draw_vis_line(vis_line=vis_line, color=color)

            left = vis_line.start * self.width
            top = self.height - vis_line.axis * self.height
            if draw_index:
                self.image_drawer.text(
                    [left, top],
                    str(i),
                    fill="black",
                )

    def draw_spatial_grid(self, grid: SpatialGrid, obj_type: type):
        non_empty_cells = grid.get_non_empty_cells()
        for cell in non_empty_cells:
            objects = grid.get_by_grid_coordinates(*cell)
            for obj in objects:
                if isinstance(obj, obj_type):
                    bbox = grid.convert_grid_coordinates_to_bbox(*cell)
                    bbox.draw_on_image(
                        image_drawer=self.image_drawer,
                        color=(255, 255, 0, 100),
                        image_width=self.width,
                        image_height=self.height,
                        fill=True,
                    )

    def save(self, out_path: str):
        """
        Saves the image to the given path.
        """
        result_image = Image.alpha_composite(
            self.rgb_image.convert("RGBA"), self.alpha_image
        )

        result_image = result_image.convert("RGB")
        result_image.save(out_path)

    def show(self):
        result_image = Image.alpha_composite(
            self.rgb_image.convert("RGBA"), self.alpha_image
        )

        result_image.show()
