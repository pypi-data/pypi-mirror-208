from .point import Point


class Segment:
    """
    A segment in 1D space.
    """

    def __init__(self, left: float, right: float):
        self.left = left
        self.right = right
        self.validate_args()

    def validate_args(self):
        """Check if the arguments are valid."""
        if self.left > self.right:
            raise ValueError(
                f"left={self.left} is greater than right={self.right}"
            )

    def get_left(self) -> float:
        """Get the left value of the segment."""
        return self.left

    def get_right(self) -> float:
        """Get the right value of the segment."""
        return self.right

    def get_length(self) -> float:
        """Get the length of the segment."""
        return abs(self.right - self.left)

    def get_center(self) -> float:
        """Get the center of the segment."""
        return (self.left + self.right) / 2

    def __lt__(self, other):
        return self.right < other.left

    def __gt__(self, other):
        return self.left > other.right

    def __str__(self):
        return f"Segment(left={self.left:.3f}, right={self.right:.3f})"

    def __repr__(self):
        return self.__str__()

    def intersect(self, other: "Segment"):
        """Check if two segments intersect"""
        if self.left > other.right:
            return False
        if self.right < other.left:
            return False
        return True

    def merge(self, other: "Segment") -> "Segment":
        """Merge two segments assuming that they intersect."""
        return Segment(min(self.left, other.left), max(self.right, other.right))

    def relation(self, other: "Segment") -> int:
        """Check the relation between two segments.
        Returns -1 if the other segment is before the self segment.
        Returns 0 if there is intersection between self and other.
        Returns 1 if the self segment is before the other segment.

        """
        if self < other:
            return 1
        if other < self:
            return -1
        return 0

    @staticmethod
    def merge_segments(segments: list["Segment"]) -> list["Segment"]:
        """
        Merge every segments that intersect with each other to a single segment.
        The output is a list of segments that are not intersecting.
        Moreover the output is increasingly sorted.
        """
        if len(segments) <= 1:
            return segments
        segments = sorted(segments, key=lambda segment: segment.get_left())

        clusters: list[Segment] = [segments.pop(0)]
        for segment in segments:
            last_cluster = clusters[-1]
            if segment.intersect(last_cluster):
                clusters[-1] = last_cluster.merge(segment)

            else:
                clusters.append(segment)
        return clusters

    def get_intersection(self, other: "Segment") -> "Segment":
        """Get the intersection between two segments."""
        if not self.intersect(other):
            return None
        return Segment(max(self.left, other.left), min(self.right, other.right))

    def proportion_covered_by_segments(
        self, segments: list["Segment"]
    ) -> float:
        """
        Get the proportion of the segment that is covered by the segments.
        """
        segments = Segment.merge_segments(segments)
        total_covered = 0
        for segment in segments:
            overlap = self.get_intersection(segment)
            if overlap is None:
                continue
            total_covered += overlap.get_length()

        return total_covered / self.get_length()


class Segment2D:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
        self.validate_args()

    def validate_args(self):
        if self.start.x == self.end.x and self.start.y == self.end.y:
            raise ValueError(
                f"start={self.start} and end={self.end} are the same point."
            )

    def get_start(self) -> Point:
        return self.start

    def get_end(self) -> Point:
        return self.end

    def get_length(self) -> float:
        return self.end.distance(self.start)

    def get_center(self) -> Point:
        return (self.start + self.end) / 2

    def __str__(self):
        return f"Segment2D(start={self.start}, end={self.end})"

    def __repr__(self):
        return self.__str__()

    def side(
        self,
        point: Point,
    ):
        return (self.end.y - point.y) * (self.start.x - point.x) > (
            self.start.y - point.y
        ) * (self.end.x - point.x)

    def intersect(self, other: "Segment2D") -> bool:
        return other.side(self.start) != other.side(self.end) and self.side(
            other.start
        ) != self.side(other.end)

    def get_projection_point(self, point: Point) -> Point:
        vector = self.end - self.start
        dot_product = (point - self.start).dot_product(
            vector
        ) / vector.abs_squared()
        truncate_dot_product = max(0, min(1, dot_product))
        return self.start + vector * truncate_dot_product

    def distance_from_point(self, point: Point) -> float:
        """Get the distance from a point to a segment."""
        projection = self.get_projection_point(point)
        return point.distance(projection)
