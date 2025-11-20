from game import Level
from scenes.houseUno import houseUno


class Level1(Level):
	"""Level 1 setup"""

	def __init__(self):
		super().__init__("Level1")
		scene = houseUno("assets/images/marcus_level/letsgo.tmx")
		self.add_scene(scene)
