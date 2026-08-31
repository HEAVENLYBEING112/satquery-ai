from typing import Any, Iterator, Tuple
from dataclasses import dataclass

@dataclass
class TileConfig:
    tile_size: int = 512
    overlap: int = 64

class TileGenerator:
    def __init__(self, config: TileConfig):
        self.config = config
        
    def generate_tiles(self, width: int, height: int) -> Iterator[Tuple[int, int, int, int]]:
        """
        Yields (x_offset, y_offset, width, height)
        """
        step = self.config.tile_size - self.config.overlap
        if step <= 0:
            raise ValueError("Overlap must be less than tile size.")
            
        for y in range(0, height, step):
            for x in range(0, width, step):
                w = min(self.config.tile_size, width - x)
                h = min(self.config.tile_size, height - y)
                yield (x, y, w, h)
                
                # To avoid tiny edge tiles, we might adjust this in future
