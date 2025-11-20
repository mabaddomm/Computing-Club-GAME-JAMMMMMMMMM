from game_objects.wall import Wall

class CollisionWall(Wall):
    """Wall used only for collisions, invisible in-game"""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.visible = False  # invisible by default
        # You could override color if needed for debugging
        self.color = (255, 0, 0)