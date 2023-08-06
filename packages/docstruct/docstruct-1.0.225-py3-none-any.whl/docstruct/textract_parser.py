from .bounding_box import BoundingBox
from .constants import LINE, WORD
from .text_block import TextBlock, Word, Line


class TextractParser:
    def __init__(self, textract_response: dict):
        self.textract_response = textract_response
        self.validate_args()
        self.words: list[dict] = []
        self.lines: list[dict] = []
        self.map_id_to_block_dict: dict[str, dict] = {}
        self.map_id_to_block_object: dict[str, TextBlock] = {}

    def validate_args(self):
        """
        Validate the arguments
        """
        if not type(self.textract_response) == dict:
            raise ValueError("textract_response must be a dict")

    def get_children_id(self, block_dict: dict) -> list[str]:
        """
        Get the children ids of a block dict
        """
        relationships = block_dict.get("Relationships", [])
        for relationship in relationships:
            if relationship["Type"] == "CHILD":
                return relationship["Ids"]
        return []

    def get_bounding_box(self, block_dict: dict) -> BoundingBox:
        """
        Get a bounding box object from a block dict
        """
        bb_dict = block_dict["Geometry"]["BoundingBox"]

        # normalized image coordinates
        left = bb_dict["Left"]
        top = bb_dict["Top"]
        right = left + bb_dict["Width"]
        bottom = top + bb_dict["Height"]

        # normalized pdf coordinates
        top, bottom = 1 - top, 1 - bottom
        return BoundingBox(left, top, right, bottom)

    def get_line(self, block_dict: dict) -> Line:
        """
        Get a line object from a block dict
        """
        bb = self.get_bounding_box(block_dict)
        line = Line(bounding_box=bb)
        children_id = self.get_children_id(block_dict)
        children = [self.map_id_to_block_object[child_id] for child_id in children_id]
        line.set_children(children)
        return line

    def word_is_printed(self, word_dict: dict) -> bool:
        """
        Check if a block dict is printed
        """
        return word_dict["TextType"] == "PRINTED"

    def get_word(self, block_dict: dict) -> Word:
        """
        Get a word object from a block dict
        """
        bbox = self.get_bounding_box(block_dict)
        text = block_dict["Text"]
        word = Word(
            bounding_box=bbox, text=text, printed=self.word_is_printed(block_dict)
        )
        return word

    def split_blocks_by_type(self, response: dict) -> tuple[list[dict], list[dict]]:
        """
        Split the blocks by type
        """
        words = []
        lines = []
        blocks_dict = response["Blocks"]
        for block_dict in blocks_dict:
            block_type = block_dict["BlockType"]
            if block_type == WORD:
                words.append(block_dict)
            elif block_type == LINE:
                lines.append(block_dict)
        return words, lines

    def get_map_id_to_block_dict(self, response: dict) -> dict:
        """
        Get a map from block id to block dict
        """
        map_id_to_block_dict = {}
        blocks_dict = response["Blocks"]
        for block_dict in blocks_dict:
            map_id_to_block_dict[block_dict["Id"]] = block_dict
        return map_id_to_block_dict

    def parse_words(self, words_dict: list[dict]) -> dict:
        """
        Parse the words
        """
        map_id_to_block_object = {}
        for word_dict in words_dict:
            word = self.get_word(word_dict)
            map_id_to_block_object[word_dict["Id"]] = word
        return map_id_to_block_object

    def parse_lines(self, lines_dict: list[dict]) -> list[Line]:
        """
        Parse the lines
        """
        lines = []
        for line_dict in lines_dict:
            line = self.get_line(line_dict)
            lines.append(line)
        return lines

    def parse_response(self) -> list[Line]:
        """
        Parse the textract response and return the page object
        """
        self.words, self.lines = self.split_blocks_by_type(self.textract_response)
        self.map_id_to_block_dict = self.get_map_id_to_block_dict(
            self.textract_response
        )
        self.map_id_to_block_object = self.parse_words(self.words)
        lines = self.parse_lines(self.lines)
        return lines
