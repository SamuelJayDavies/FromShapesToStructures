from BrickType import BrickType

class Brick:
    def __init__(self, 
                  brickType: BrickType, brick_id: int, y: int, z: int, x: int, orientation: tuple[int, int]) -> None:
        if not isinstance(brickType, BrickType):
            raise TypeError("brickType must be an instance of BrickType.")
        
        integer_parameters = [y, z, x]

        for param in integer_parameters:
            if not isinstance(param, int):
                raise TypeError(param + " must be an integer.")
            
        if integer_parameters[:3] < 0:
            raise ValueError("y, z, and x must be non-negative integers.")

        if orientation not in brickType.orientations():
            raise ValueError("The provided orientation " + str(orientation) + " cannot be used with this brick type + " + str(brickType) + ".")
        
        self.brickType = brickType

        self.y = y
        self.z = z
        self.x = x

        self.orientation = orientation
        
        self.brick_id = brick_id

    def size_x(self) -> int:
        return self.orientation[0]
    
    def size_z(self) -> int:
        return self.orientation[1]

    def area(self) -> int:
        return self.brickType.area()
    
    def position(self) -> tuple[int, int, int]:
        return (self.y, self.z, self.x)
    
    def is_placed(self) -> bool:
        return self.brick_id is not None
    
    def place_brick(self, brick_id: int) -> None:
        self.brick_id = brick_id

    def __repr__(self) -> str:
        return "Brick Placement - Type: " + self.brickType.name + ", Position: (" + str(self.y) + ", " + str(self.z) + ", " + str(self.x) + "), Orientation: (" + str(self.orientation[0]) + ", " + str(self.orientation[1]) + "), Brick  ID: " + str(self.brick_id)