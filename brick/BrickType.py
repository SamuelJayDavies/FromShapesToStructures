class BrickType:

    def __init__(self, name, x_length, z_length) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        
        if not isinstance(x_length, int):
            raise TypeError("x_length must be an integer.")
        
        if not isinstance(z_length, int):
            raise TypeError("z_length must be an integer.")
        
        if x_length < 1:
            raise ValueError("x_length must be at least greater than 1")
        
        if z_length < 1:
            raise ValueError("z_length must be at least greater than 1")
        
        if not name:
            raise ValueError("Name cannot be empty.")
        
        if not x_length:
            raise ValueError("x_length cannot be zero.")
        
        if not z_length:
            raise ValueError("z_length cannot be zero.")
        
        self.name = name
        self.x_length = x_length
        self.z_length = z_length

    def area(self) -> int:
        return self.x_length * self.z_length
    
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