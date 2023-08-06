from typing import TypeVar


T = TypeVar('T')

class DNA:
	
	def __init__(self, n_parents=2):
		self.n_parents = n_parents

	def setup(self, popsize: int) -> list[T]:
		raise NotImplementedError("Should be implemented by subclass")

	def crossover(self, *args: T) -> T:
		raise NotImplementedError("Should be implemented by subclass")
	
	def score(self, subject: T) -> float:
		raise NotImplementedError("Should be implemented by subclass")

	def mutate(self, subject: T) -> T:
		raise NotImplementedError("Should be implemented by subclass")
