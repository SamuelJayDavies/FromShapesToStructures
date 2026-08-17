from .BrickType import BrickType

class Brick:
    """ Class that represents a brick that can be placed, orientated and has its own coordinates in a Result Grid if it is placed correctly
     
    Args:
        brickType: the type of the brick being placed
        y: the y-coordinate of the brick being placed
        z: the z_coordinate of the brick being placed
        x: the x_coordinate of the brick being placed
        orientation: the orientation in the form [int, int] of the brick
    """
    def __init__(self, 
                  brickType: BrickType, y: int, z: int, x: int, orientation: tuple[int, int]) -> None:
        if not isinstance(brickType, BrickType):
            raise TypeError("brickType must be an instance of BrickType.")
        
        integer_parameters = [y, z, x]

        for param in integer_parameters:
            if not isinstance(param, int):
                raise TypeError(param + " must be an integer.")
        
        for param in integer_parameters:
            if param < 0:
                raise ValueError(str(param) + " must be a non-negative integer.")

        if len(orientation) != 2:
            raise ValueError("Orientation must contain 2 dimensions exactly")
        
        if not all(isinstance(dimension, int) for dimension in orientation):
            raise ValueError("Orientaton dimensions must be integers")

        if orientation not in brickType.orientations():
            raise ValueError("The provided orientation " + str(orientation) + " cannot be used with this brick type + " + str(brickType) + ".")
        
        self.brickType = brickType

        self.y = y
        self.z = z
        self.x = x

        self.orientation = orientation
        # Brick ID is only changed to non-None when the brick has been successfully placed, and the method is_placed() will return True
        self.brick_id = None
    
    def size_x(self) -> int:
        """ Returns the width of the brick
        
        Args:
            Returns the width of the brick"""
        return self.orientation[0]
    
    def size_z(self) -> int:
        """ Returns the depth of the brick
        
        Args:
            The depth of the brick"""
        return self.orientation[1]

    def area(self) -> int:
        """ Returns the area of the brick
        
        Args:
            The area of the brick"""
        return self.brickType.area()
    
    def position(self) -> tuple[int, int, int]:
        return (self.y, self.z, self.x)
    
    def is_placed(self) -> bool:
        return self.brick_id is not None
    
    def place_brick(self, brick_id: int) -> None:
        self.brick_id = brick_id

    def __repr__(self) -> str:
        return "Brick Placement - Type: " + self.brickType.name + " is placed: " + str(self.is_placed()) + ", Position: (" + str(self.y) + ", " + str(self.z) + ", " + str(self.x) + "), Orientation: (" + str(self.orientation[0]) + ", " + str(self.orientation[1]) + "), Brick  ID: " + str(self.brick_id)