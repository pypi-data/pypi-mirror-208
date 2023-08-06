import attr
import numpy as np
import cv2
import math
import itertools
import os
from .vis_line import VisLine, Orientation
from ..text_block import Word
from ..graph import Node, Graph
from ..spatial_grid_indexing import SpatialGrid
from ..drawer import Drawer
from .constants import (
    ANGLE_DEGREE_THRESHOLD,
    NUM_SAMPLED_POINTS_ON_LINE,
    NUM_SAMPLED_POINTS_ON_ORTHOGONAL_LINE,
    SPATIAL_GRID_SIZE,
)


@attr.s(auto_attribs=True)
class HorVerVisLines:
    hor_lines: list[VisLine]
    ver_lines: list[VisLine]

    def __iter__(self):
        return iter([self.hor_lines, self.ver_lines])


class VisLineOpenCV:
    def __init__(self, image: np.ndarray[(int, int)], length_threshold: float):
        self.image = image
        self.length_threshold = length_threshold
        self.image_height, self.image_width = image.shape

    @staticmethod
    def is_hor_line(line: np.array) -> bool:
        line_angle = VisLineOpenCV.get_line_angle(line)
        return VisLineOpenCV.is_hor_angle(line_angle)

    @staticmethod
    def is_ver_line(line: np.array) -> bool:
        line_angle = VisLineOpenCV.get_line_angle(line)
        return VisLineOpenCV.is_ver_angle(line_angle)

    @staticmethod
    def is_hor_angle(angle: float) -> bool:
        return -ANGLE_DEGREE_THRESHOLD < angle < ANGLE_DEGREE_THRESHOLD

    @staticmethod
    def is_ver_angle(angle: float) -> bool:
        return 90 - ANGLE_DEGREE_THRESHOLD < angle < 90 + ANGLE_DEGREE_THRESHOLD

    @staticmethod
    def get_line_angle(line: np.array) -> float:
        x0, y0, x1, y1 = line
        delta_x = abs(x0 - x1)
        delta_y = abs(y0 - y1)
        line_angle = math.degrees(math.atan2(delta_y, delta_x))
        return line_angle

    @staticmethod
    def fix_orientation(line: np.ndarray):
        x0, y0, x1, y1 = line
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        return x0, y0, x1, y1

    def get_openCV_lines(self):
        line_detector = cv2.ximgproc.createFastLineDetector(
            canny_th1=50,
            canny_th2=50,
            length_threshold=self.length_threshold,
            do_merge=False,
        )
        lines = line_detector.detect(self.image)
        if lines is None:
            return None
        return lines.squeeze(1)

    def normalize_line_coordinates(self, line: np.array):
        x0, y0, x1, y1 = line
        x0 = x0 / self.image_width
        x1 = x1 / self.image_width
        y0 = 1 - y0 / self.image_height
        y1 = 1 - y1 / self.image_height
        return x0, y0, x1, y1

    def get_line_width(self, line: dict, orientation: Orientation):
        x0, y0, x1, y1 = line
        points = sample_points_on_line(x0, y0, x1, y1, NUM_SAMPLED_POINTS_ON_LINE)
        widths = []
        for point in points:
            # TODO think of a max_length
            max_length = 15
            orthogonal_line = get_line(
                *point,
                length=max_length,
                orientation=Orientation.get_orthogonal(orientation),
            )

            orthogonal_points = sample_points_on_line(
                *orthogonal_line, NUM_SAMPLED_POINTS_ON_ORTHOGONAL_LINE
            )
            orthogonal_pixels_value = [
                get_pixel_value_with_interpolation(self.image, *point)
                for point in orthogonal_points
            ]
            width = estimate_width_from_pixels(orthogonal_pixels_value)
            widths.append(width)
        return np.mean(widths)

    def convert_to_vis_line(
        self, openCV_line: np.array, orientation: Orientation
    ) -> VisLine:
        line_width = self.get_line_width(openCV_line, orientation)
        normalized_line = self.normalize_line_coordinates(line=openCV_line)
        normalized_oriented_line = VisLineOpenCV.fix_orientation(normalized_line)
        normalized_line_width = line_width / self.image_height
        if orientation == Orientation.HORIZONTAL:
            axis = (normalized_oriented_line[1] + normalized_oriented_line[3]) / 2
            start = normalized_oriented_line[0]
            end = normalized_oriented_line[2]
        else:
            axis = (normalized_oriented_line[0] + normalized_oriented_line[2]) / 2
            start = normalized_oriented_line[1]
            end = normalized_oriented_line[3]
        return VisLine(
            axis=axis,
            orientation=orientation,
            start=start,
            end=end,
            width=normalized_line_width,
        )

    def get_lines(self):
        openCV_lines = self.get_openCV_lines()
        if openCV_lines is None:
            return [], []
        openCV_hor_lines = [
            line for line in openCV_lines if VisLineOpenCV.is_hor_line(line)
        ]
        openCV_ver_lines = [
            line for line in openCV_lines if VisLineOpenCV.is_ver_line(line)
        ]
        vis_hor_lines = [
            self.convert_to_vis_line(line, orientation=Orientation.HORIZONTAL)
            for line in openCV_hor_lines
        ]
        vis_ver_lines = [
            self.convert_to_vis_line(line, orientation=Orientation.VERTICAL)
            for line in openCV_ver_lines
        ]
        return vis_hor_lines, vis_ver_lines


class VisLineRemover:
    def __init__(self, lines: list[VisLine], words: list[Word]):
        self.lines = lines
        self.words = words
        self.spatial_grid = self.get_spatial_grid(lines, words)

    def get_spatial_grid(self, lines: list[VisLine], words: list[Word]) -> SpatialGrid:
        spatial_grid = SpatialGrid(
            num_rows=SPATIAL_GRID_SIZE, num_cols=SPATIAL_GRID_SIZE
        )
        for word in words:
            spatial_grid.add_bounding_box_interior(
                bbox=word.bounding_box.scale(width_scale=1, height_scale=1), data=word
            )
        for line in lines:
            spatial_grid.add_vis_line(vis_line=line)
        return spatial_grid

    def remove_lines(self) -> list[VisLine]:
        non_empty_cells = self.spatial_grid.get_non_empty_cells()
        line_word_pairs: set(VisLine, Word) = set()
        for cell in non_empty_cells:
            words_and_lines = self.spatial_grid.get_by_grid_coordinates(*cell)
            words = [word for word in words_and_lines if isinstance(word, Word)]
            lines = [line for line in words_and_lines if isinstance(line, VisLine)]
            for line in lines:
                for word in words:
                    line_word_pairs.add((line, word))
        intersecting_lines = set()

        for line, word in line_word_pairs:
            # if self.old_intersect(line, word):
            if line.intersect_bounding_box(
                word.bounding_box.scale(width_scale=1, height_scale=0.9)
                # word.bounding_box.scale(scale_x=1, scale_y=1)
            ):
                intersecting_lines.add(line)
        non_intersecting_lines = []
        for line in self.lines:
            if line not in intersecting_lines:
                non_intersecting_lines.append(line)
        horizontal_lines = [line for line in non_intersecting_lines if line.is_hor()]
        vertical_lines = [line for line in non_intersecting_lines if line.is_ver()]
        return horizontal_lines, vertical_lines


class VisLineMerger:
    def __init__(self, lines: list[VisLine], length_threshold: float):
        self.lines = lines
        self.length_threshold = length_threshold
        self.spatial_grid = self.get_spatial_grid(lines)

    def get_spatial_grid(self, lines: list[VisLine]) -> SpatialGrid:
        spatial_grid = SpatialGrid(
            num_rows=SPATIAL_GRID_SIZE, num_cols=SPATIAL_GRID_SIZE
        )
        for line in lines:
            bbox = line.convert_to_bb(
                length_threshold=self.length_threshold,
            )
            spatial_grid.add_bounding_box_interior(bbox=bbox, data=line)
        return spatial_grid

    def get_graph(self):
        nodes = [Node(line) for line in self.lines]

        map_line_id_to_node = {
            line.id: nodes[index] for index, line in enumerate(self.lines)
        }
        non_empty_cells = self.spatial_grid.get_non_empty_cells()
        line_pairs = set()
        for cell in non_empty_cells:
            lines = self.spatial_grid.get_by_grid_coordinates(*cell)
            for pair in itertools.combinations(lines, 2):
                line_pairs.add(pair)

        for first_line, second_line in line_pairs:
            if self.are_adjacent_lines(first_line, second_line):
                first_node = map_line_id_to_node[first_line.id]
                second_node = map_line_id_to_node[second_line.id]
                first_node.add_neighbor(second_node)
                second_node.add_neighbor(first_node)
        return Graph(nodes)

    def merge_lines(self):
        """
        Merge horizontal lines that are close to each other
        A line with axis_value = axis and a width = W, is represented by a bounding box surrounding that line
        with width = W(1+hor_epsilon) and hight = ver_epsilon
        two lines are adjacent of their bounding boxes intersect.
        First notice int(x+y) <= int(x)+int(y)+1
        """
        graph = self.get_graph()
        ccs_of_nodes = graph.get_connected_components()

        ccs_of_lines = []
        for cc in ccs_of_nodes:
            ccs_of_lines.append([node.data for node in cc])

        merged_lines = []
        for cc in ccs_of_lines:
            line = VisLine.merge_lines(cc)
            merged_lines.append(line)
        return merged_lines

    def are_adjacent_lines(
        self,
        first_line: VisLine,
        second_line: VisLine,
    ):
        first_bb = first_line.convert_to_bb(
            length_threshold=self.length_threshold,
        )
        second_bb = second_line.convert_to_bb(
            length_threshold=self.length_threshold,
        )
        return first_bb.intersect(second_bb)


def sample_points_on_line(x0, y0, x1, y1, num_points: int) -> np.ndarray:
    """
    Sample equidistant points on a line segment avoiding the endpoints
    """
    x = np.linspace(x0, x1, num_points + 2)[1:-1]
    y = np.linspace(y0, y1, num_points + 2)[1:-1]
    return np.stack([x, y], axis=1)


def get_pixel_value(image: np.ndarray, x: int, y: int):
    if x < 0 or y < 0:
        return 255
    if x >= image.shape[1] or y >= image.shape[0]:
        return 255
    return image[y, x]


def get_pixel_value_with_interpolation(image: np.ndarray, x: float, y: float):
    """
    Notice the sum of the weights is equal to 1:
    """
    x0 = int(x)
    x1 = x0 + 1
    y0 = int(y)
    y1 = y0 + 1
    x0_weight = x1 - x
    x1_weight = x - x0
    y0_weight = y1 - y
    y1_weight = y - y0
    return (
        get_pixel_value(image, x0, y0) * x0_weight * y0_weight
        + get_pixel_value(image, x1, y0) * x1_weight * y0_weight
        + get_pixel_value(image, x0, y1) * x0_weight * y1_weight
        + get_pixel_value(image, x1, y1) * x1_weight * y1_weight
    )


def estimate_width_from_pixels(pixels: list[int]):
    # TODO - for the "001" case in the dataset with boundaries width of 5 doesn't work good.
    return 10


def get_line(center_x: float, center_y: float, length: float, orientation: Orientation):
    if orientation == Orientation.HORIZONTAL:
        x0 = center_x - length / 2
        x1 = center_x + length / 2
        y0 = center_y
        y1 = center_y
    else:
        x0 = center_x
        x1 = center_x
        y0 = center_y - length / 2
        y1 = center_y + length / 2
    return x0, y0, x1, y1


def filter_lines_by_length(
    lines: list[VisLine], length_threshold: float
) -> list[VisLine]:
    return [line for line in lines if line.get_length() > length_threshold]


class VisLineExtension:
    """
    Assumes that the lines are either horizontal or vertical
    """

    def __init__(self, lines: list[VisLine], length_threshold: float):

        self.lines = lines
        self.length_threshold = length_threshold

    def similar_lines_up_to_axis(
        self, first_line: VisLine, second_line: VisLine
    ) -> bool:
        """
        Check if two lines are similar up to their axis value
        """
        if (
            abs(first_line.start - second_line.start) > self.length_threshold
            or abs(first_line.end - second_line.end) > self.length_threshold
        ):
            return False
        x = first_line.get_length()
        y = second_line.get_length()

        length_ratio = abs(x - y) / max(x, y)
        return length_ratio < 0.1

    def extend_lines(self):
        """
        Extend lines that are close to each other
        """
        for first_line in self.lines:
            similar_to_first_line = []
            for second_line in self.lines:
                if first_line.id == second_line.id:
                    continue
                if self.similar_lines_up_to_axis(first_line, second_line):
                    similar_to_first_line.append(second_line)
            if len(similar_to_first_line) == 0:
                continue
            first_line.start = np.min(
                [first_line.start] + [line.start for line in similar_to_first_line]
            )
            first_line.end = np.max(
                [first_line.end] + [line.end for line in similar_to_first_line]
            )


class VisLineDetector:
    def __init__(
        self,
        image_path: str,
        words: list[Word],
        debug: bool = False,
        debug_dir: str = None,
    ):
        self.image = cv2.imread(image_path)
        self.image_height, self.image_width = self.image.shape[:2]
        self.words = words
        self.debug = debug
        self.debug_dir = debug_dir
        if debug:
            self.opencv_drawer = Drawer(image_path)
            self.remover_drawer = Drawer(image_path)
            self.merge_drawer = Drawer(image_path)
            self.extension_drawer = Drawer(image_path)

    def detect_lines(
        self, hor_threshold: int, ver_threshold: int, image_length_threshold: int
    ) -> HorVerVisLines:
        hor_image = self.hor_preprocess(self.image)
        ver_image = self.ver_preprocess(self.image)

        gray_hor_image = cv2.cvtColor(hor_image, cv2.COLOR_BGR2GRAY)
        gray_ver_image = cv2.cvtColor(ver_image, cv2.COLOR_BGR2GRAY)

        hor_line_detector = VisLineOpenCV(gray_hor_image, image_length_threshold)

        hor_lines, _ = hor_line_detector.get_lines()
        ver_line_detector = VisLineOpenCV(gray_ver_image, image_length_threshold)
        _, ver_lines = ver_line_detector.get_lines()

        if self.debug:
            self.opencv_drawer.draw_vis_lines(hor_lines + ver_lines, random_color=True)
            self.opencv_drawer.save(os.path.join(self.debug_dir, "opencv_lines.jpg"))

        line_remover = VisLineRemover(lines=hor_lines + ver_lines, words=self.words)

        # self.remover_drawer.draw_spatial_grid(line_remover.spatial_grid, VisLine)
        # self.remover_drawer.show()
        hor_lines, ver_lines = line_remover.remove_lines()
        if self.debug:
            self.remover_drawer.draw_vis_lines(hor_lines + ver_lines, random_color=True)
            self.remover_drawer.save(os.path.join(self.folder, "remover_lines.jpg"))

        hor_line_merger = VisLineMerger(hor_lines, hor_threshold)
        merged_hor_lines = hor_line_merger.merge_lines()
        ver_line_merger = VisLineMerger(ver_lines, ver_threshold)
        merged_ver_lines = ver_line_merger.merge_lines()

        if self.debug:
            self.merge_drawer.draw_vis_lines(
                merged_hor_lines + merged_ver_lines, random_color=True
            )
            self.merge_drawer.save(os.path.join(self.folder, "merge_lines.jpg"))

        line_extension = VisLineExtension(merged_hor_lines, hor_threshold)
        line_extension.extend_lines()
        line_extension = VisLineExtension(merged_ver_lines, ver_threshold)

        hor_ver_vis_lines = HorVerVisLines(merged_hor_lines, merged_ver_lines)
        return hor_ver_vis_lines

    def hor_preprocess(self, image: np.ndarray) -> np.ndarray:
        """Horizontal blur"""
        kernel = np.ones((3, 7), np.float32) / 21
        image = cv2.filter2D(image, -1, kernel)
        return image

    def ver_preprocess(self, image: np.ndarray) -> np.ndarray:
        """Vertical blur"""
        kernel = np.ones((7, 3), np.float32) / 21
        image = cv2.filter2D(image, -1, kernel)
        return image
