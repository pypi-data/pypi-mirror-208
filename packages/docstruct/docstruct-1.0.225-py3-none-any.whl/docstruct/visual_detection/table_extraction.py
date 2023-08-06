import cv2
from .vis_line_detection import VisLineDetector, VisLineMerger
from .bordered_table_extraction import BorderedTableExtractor
from ..text_block import word, Page, Cell, Table


class TableExtractor:
    def __init__(self, image_path: str, page: Page):

        self.image = cv2.imread(image_path)
        self.image_height, self.image_width = self.image.shape[:2]
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.page = page

    def group_words_to_cells(self, words: list[word], cells: list[Cell]) -> list[Cell]:
        """Group words to cells."""
        for cell in cells:
            cell.set_words(words)
        return cells

    def extract_tables(self) -> list[Table]:

        words = list(self.page.get_all(word))
        if not words:
            return []
        hor_threshold = self.get_average_word_height(self.page)
        ver_threshold = hor_threshold * self.image_height / self.image_width
        length_threshold = int(hor_threshold * self.image_height)

        line_detector = VisLineDetector(self.gray_image, length_threshold)
        hor_lines, ver_lines = line_detector.main()
        hor_line_merger = VisLineMerger(hor_lines, hor_threshold)
        merged_hor_lines = hor_line_merger.main()

        ver_line_merger = VisLineMerger(ver_lines, ver_threshold)
        merged_ver_lines = ver_line_merger.main()

        table_detector = BorderedTableExtractor(
            merged_hor_lines, merged_ver_lines, hor_threshold, ver_threshold
        )
        tables = table_detector.main()
        return tables
