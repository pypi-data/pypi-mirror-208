from inspect import BoundArguments
from .text_block import Page, word, Character, TextBlock
from .bounding_box import BoundingBox
import numpy as np


class SpacePartition:
    def __init__(
        self, searchable_block: TextBlock, partition_factor: int, query_type: type
    ):
        search_area = searchable_block.bounding_box
        blocks = searchable_block.get_all(query_type)
        grid = np.ndarray((partition_factor, partition_factor), dtype=object)
        for block in blocks:
            grid = self.add_block_to_grid(block, grid, search_area, partition_factor)

    def add_block_to_grid(
        self,
        block: TextBlock,
        grid: np.ndarray,
        search_area: BoundingBox,
        partition_factor: int,
    ): 
        center = block.bounding_box.center
        center.x - 
        return grid
