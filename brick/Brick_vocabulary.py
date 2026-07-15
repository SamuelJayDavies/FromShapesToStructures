from typing import List

from .BrickType import BrickType

# Rules for a valid vocabulary should be that:
# 1. All bricks must be valid BrickType instances
# 2. A brick vocabulary must contain at least one brick
# 3. All bricks must have unique names, and dimensions
# 4. All vocabularies require a 1x1 brick to be present, to ensure any valid voxel can be filled


class Brick_vocabulary:

    def __init__(self, bricks: List[BrickType]) -> None:
        """
        Initialise a brick vocabulary
        
        Args:
            bricks: A list of BrickType instances to be included in the vocabulary.
            
        Raises:
            TypeError: If bricks is not a list or tuple, or if any item in bricks is not a BrickType.
            ValueError: If bricks is empty, contains duplicate names or dimensions, or does not contain a 1x1 brick.
        
        Returns:
            None
        """
        # Validation Checks #

        # Check 1
        if len(bricks) == 0:
            raise ValueError("Brick vocabulary cannot be empty.")
        
        # Check 2
        if not all(isinstance(brick, BrickType) for brick in bricks):
            raise TypeError("All items within vocabulary must be BrickType instances.")
        
        seen_names = set()
        seen_dimensions = set()

        for brick in bricks:

            # Check 3a
            if brick.name in seen_names:
                raise ValueError("Duplicate brick name found in vocabulary: " + brick.name)
            
            # Check 3b
            if tuple(sorted((brick.x_length, brick.z_length))) in seen_dimensions:
                raise ValueError("Duplicate brick dimensions found in vocabulary: " + str(brick.x_length) + "x" + str(brick.z_length))
            
            seen_names.add(brick.name)
            seen_dimensions.add(tuple(sorted((brick.x_length, brick.z_length))))
        
        # Check 4
        if not any(brick.x_length == 1 and brick.z_length == 1 for brick in bricks):
            raise ValueError("Vocabulary must contain a 1x1 brick.")
        
        # End of Validation Checks #
        print("Brick vocab succesfully saved")
        self._bricks = bricks

    def bricks(self) -> list[BrickType]:

        return list(self._bricks)
    
    def __len__(self) -> int:
        """
        Get the number of bricks in the vocabulary.
        
        Returns:
            The number of bricks in the vocabulary.
        """
        return len(self._bricks)
    
    def __getitem__(self, index: int) -> BrickType:
        """
        Get a brick from the vocabulary by index.
        
        Args:
            index: The index of the brick to retrieve.
        
        Returns:
            The brick instance at the specified index.
        """
        return self._bricks[index]
    
    def __iter__(self):
        """
        Iterate over the bricks in the vocabulary.
        
        Returns:
            An iterator over the bricks in the vocabulary.
        """
        return iter(self._bricks)
    
    def __repr__(self) -> str:
        """
        Get a string representation of the brick vocabulary.
        
        Returns:
            A string representation of the brick vocabulary.
        """
        return "Brick Vocabulary: " + ", ".join([brick.name for brick in self._bricks])

    def group_by_area_size(self) -> list[tuple[int, list[BrickType]]]:
        groups: dict[int, list[BrickType]] = {}

        for brick in self._bricks:
            brick_area = brick.area()

            if brick_area not in groups:
                groups[brick_area] = []

            groups[brick_area].append(brick)
        
        sorted_areas = sorted(groups.keys(), reverse=True)

        grouped_bricks: list[tuple[int, list[BrickType]]] = []

        for area in sorted_areas:
            grouped_bricks.append((area, list(groups[area])))

        return grouped_bricks

BASIC_BRICK_VOCABULARY = Brick_vocabulary(
    bricks=[
        BrickType(name="1x1", x_length=1, z_length=1),
        BrickType(name="1x2", x_length=1, z_length=2),
        BrickType(name="2x2", x_length=2, z_length=2),
        BrickType(name="2x4", x_length=2, z_length=4),
        BrickType(name="4x4", x_length=4, z_length=4),
    ]
)

ADVANCED_BRICK_VOCABULARY = Brick_vocabulary(
    bricks=[
        BrickType(name="1x1", x_length=1, z_length=1),
        BrickType(name="1x2", x_length=1, z_length=2),
        BrickType(name="1x3", x_length=1, z_length=3),
        BrickType(name="1x4", x_length=1, z_length=4),
        BrickType(name="1x6", x_length=1, z_length=6),
        BrickType(name="1x8", x_length=1, z_length=8),
        BrickType(name="2x2", x_length=2, z_length=2),
        BrickType(name="2x3", x_length=2, z_length=3),
        BrickType(name="2x4", x_length=2, z_length=4),
        BrickType(name="2x6", x_length=2, z_length=6),
        BrickType(name="2x8", x_length=2, z_length=8),
        BrickType(name="3x3", x_length=3, z_length=3),
        BrickType(name="3x4", x_length=3, z_length=4),
        BrickType(name="3x6", x_length=3, z_length=6),
        BrickType(name="3x8", x_length=3, z_length=8),
        BrickType(name="4x4", x_length=4, z_length=4),
        BrickType(name="4x6", x_length=4, z_length=6),
        BrickType(name="4x8", x_length=4, z_length=8),
        BrickType(name="6x6", x_length=6, z_length=6),
        BrickType(name="6x8", x_length=6, z_length=8),
        BrickType(name="8x8", x_length=8, z_length=8)
    ]
)