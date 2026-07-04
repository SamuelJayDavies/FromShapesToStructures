import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brick import Brick
from brick import BrickType

brick = BrickType("2x4", 2, 4)

candidate_brick = Brick(brick, y=0, z=1, x=2, orientation=(4,2))

print(candidate_brick)

print(candidate_brick.is_placed())

candidate_brick.place_brick(brick_id=1)

print(candidate_brick)