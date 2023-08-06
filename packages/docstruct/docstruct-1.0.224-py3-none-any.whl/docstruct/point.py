class Point:
    """
    A point in 2D space."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def get_x(self) -> float:
        """Get the x coordinate of the point."""
        return self.x

    def get_y(self) -> float:
        """Get the y coordinate of the point."""
        return self.y

    def __str__(self):
        return f"Point(x={self.x:.3f}, y={self.y:.3f})"

    def __repr__(self):
        return self.__str__()

    def __add__(self, other: "Point") -> "Point":
        """Create a new point by adding two points."""
        if not isinstance(other, Point):
            raise TypeError(
                "unsupported operand type(s) for +: "
                + f"'{type(self).__name__}' and '{type(other).__name__}'"
            )

        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        """Create a new point by subtracting two points."""
        if not isinstance(other, Point):
            raise TypeError(
                "unsupported operand type(s) for -: "
                + f"'{type(self).__name__}' and '{type(other).__name__}'"
            )

        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> "Point":
        """Create a new point by multiplying a point by a scalar."""
        if not isinstance(other, (int, float)):
            raise TypeError(
                "unsupported operand type(s) for *: "
                + f"'{type(self).__name__}' and '{type(other).__name__}'"
            )
        return Point(self.x * other, self.y * other)

    def __rmul__(self, scalar: float) -> "Point":
        return self.__mul__(scalar)

    def __truediv__(self, other: float) -> "Point":
        """Create a new point by dividing a point by a scalar."""
        if not isinstance(other, (int, float)):
            raise TypeError(
                "unsupported operand type(s) for /: "
                + f"'{type(self).__name__}' and '{type(other).__name__}'"
            )
        if other == 0:
            raise ZeroDivisionError("Division by zero is not allowed")

        return Point(self.x / other, self.y / other)

    def __abs__(self) -> float:
        """Get the distance of the point from the origin."""
        return (self.x**2 + self.y**2) ** 0.5

    def abs_squared(self) -> float:
        """Get the squared distance of the point from the origin."""
        return self.x**2 + self.y**2

    def dot_product(self, other: "Point") -> float:
        """Get the dot product of two points."""
        if not isinstance(other, Point):
            raise TypeError(
                "unsupported operand type(s) for *: "
                + f"'{type(self).__name__}' and '{type(other).__name__}'"
            )

        return self.x * other.x + self.y * other.y

    def distance(self, other: "Point") -> float:
        """Get the distance between two points."""
        if not isinstance(other, Point):
            raise TypeError(
                "unsupported operand type(s) for -: "
                + f"'{type(self).__name__}' and '{type(other).__name__}'"
            )
        return abs(self - other)

    def normalize(self) -> "Point":
        """Get a new point that is normalized."""
        if abs(self) == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return self / abs(self)
