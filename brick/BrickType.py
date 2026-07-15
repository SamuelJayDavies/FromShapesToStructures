class BrickType:

    def __init__(self, name, x_length, z_length) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        elif not name:
            raise ValueError("Name cannot be empty")
        else:
            dimensions = {"Width": x_length, "Depth": z_length}

            for brick_name, var in dimensions.items():
                if not isinstance(var, int):
                    raise TypeError(brick_name + " must be an integer value")
                elif var < 1:
                    raise ValueError(brick_name + " must be at least 1")
                else:
                    self.name = name
                    self.x_length = x_length
                    self.z_length = z_length

    def area(self) -> int:
        return self.x_length * self.z_length
    
    def dimensions(self) -> tuple[int, int]:
        return self.x_length, self.z_length
    
    def orientations(self) -> list[tuple[int, int]]:
        original_orientation = (self.x_length, self.z_length)
        rotated_orientation = (self.z_length, self.x_length)
        if original_orientation == rotated_orientation:
            return [original_orientation]
        else:
            return [original_orientation, rotated_orientation]

    # repr over __str__ because if __str__ isn't defined, __repr__ is used instead. 
    def __repr__(self) -> str:
        return "BrickType: " + self.name + ", x_length: " + str(self.x_length) + ", z_length: " + str(self.z_length)