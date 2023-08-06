from enum import Enum
import numpy as np
import logging
from ..utils import IDGenerator
from ..bounding_box import BoundingBox
from ..segment import Segment, Segment2D
from ..point import Point


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1

    @staticmethod
    def get_orthogonal(orientation: "Orientation") -> "Orientation":
        if orientation == Orientation.HORIZONTAL:
            return Orientation.VERTICAL
        elif orientation == Orientation.VERTICAL:
            return Orientation.HORIZONTAL


class VisLine:
    def __init__(
        self,
        axis: float,
        orientation: Orientation,
        start: float,
        end: float,
        width: float,
    ):
        self.axis = axis
        self.orientation = orientation
        self.start = start
        self.end = end
        self.width = width
        self.id = IDGenerator().generate_id()
        self.valid_args()

    def valid_args(self) -> bool:
        if self.start >= self.end:
            logging.error("Invalid VisLine: start >= end")

    def __str__(self):
        return f"VisLine(axis_value={self.axis:.3f}, orientation={self.orientation}, start={self.start:.3f}, end={self.end:.3f}, width={self.width:.3f}))"

    def __repr__(self):
        return self.__str__()

    def get_width(self) -> float:
        return self.width

    def get_length(self) -> float:
        return self.end - self.start

    def get_center(self) -> float:
        return (self.start + self.end) / 2

    def convert_to_bb(self, height_scale=1, width_scale=1, length_threshold=0):
        new_length = self.get_length() * (height_scale) + length_threshold
        new_width = self.get_width() * (width_scale)

        if self.orientation == Orientation.HORIZONTAL:
            left = self.get_center() - new_length / 2
            right = self.get_center() + new_length / 2
            top = self.axis + new_width / 2
            bottom = self.axis - new_width / 2
        else:
            left = self.axis - new_width / 2
            right = self.axis + new_width / 2
            top = self.get_center() + new_length / 2
            bottom = self.get_center() - new_length / 2
        return BoundingBox(left, top, right, bottom)

    def intersect_bounding_box(self, bbox: BoundingBox) -> bool:
        if self.orientation == Orientation.HORIZONTAL:
            axis_condition = bbox.bottom <= self.axis <= bbox.top
            first_segment = Segment(left=bbox.left, right=bbox.right)
            second_segment = Segment(left=self.start, right=self.end)
            orthogonal_condition = first_segment.intersect(second_segment)
            return axis_condition and orthogonal_condition
        else:
            axis_condition = bbox.left <= self.axis <= bbox.right
            first_segment = Segment(left=bbox.bottom, right=bbox.top)
            second_segment = Segment(left=self.start, right=self.end)
            orthogonal_condition = first_segment.intersect(second_segment)
            return axis_condition and orthogonal_condition

    def convert_to_segment(self) -> Segment2D:
        if self.orientation == Orientation.HORIZONTAL:
            return Segment2D(
                Point(self.start, self.axis),
                Point(self.end, self.axis),
            )
        else:
            return Segment2D(
                Point(self.axis, self.start),
                Point(self.axis, self.end),
            )

    def is_hor(self) -> bool:
        return self.orientation == Orientation.HORIZONTAL

    def is_ver(self) -> bool:
        return self.orientation == Orientation.VERTICAL

    @staticmethod
    def get_weighted_average_axis(lines: list["VisLine"]) -> float:
        """Get the weighted average of the axis values of a list of visual lines."""
        return np.average(
            [line.axis for line in lines],
            weights=[(vis_line.get_length()) for vis_line in lines],
        )

    @staticmethod
    def merge_lines(lines: list["VisLine"]) -> "VisLine":
        if not lines:
            raise ValueError("Cannot merge empty list of lines")
        if len(lines) == 1:
            return lines[0]
        return VisLine(
            axis=VisLine.get_weighted_average_axis(lines),
            orientation=lines[0].orientation,
            start=np.min([line.start for line in lines]),
            end=np.max([line.end for line in lines]),
            width=np.mean([line.width for line in lines]),
        )
