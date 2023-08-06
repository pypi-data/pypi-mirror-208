from random import choices, random
from .dna import DNA



class Population:
	
	def __init__(self, size, dna :DNA):
		# Size of the population
		self.size = size
		# Type of individuals in the population
		self.dna = dna
		# List of individuals in the population
		self.population = None
  
	
	def train(self, n_generations: int, mutation_rate: float) -> float:
		# Initialize the population if it has not been initialized already
		if self.population is None:
			self.population = self.dna.setup(self.size)

		it = 0
		# Perform genetic algorithm for the specified number of generations
		while it < n_generations:
      		# Calculate the fitness scores of all individuals in the population
			scores = [self.dna.score(x) for x in self.population]

			# Normalize the fitness scores to probabilities
			sumscores = sum(scores)
			prob = [ x / sumscores for x in scores ]

			# Select parents for the next generation using weighted random sampling
			couples = (choices(self.population, weights=prob, k=self.dna.n_parents) for x in self.population)

			# Create the next generation by performing crossover and mutation on the parents
			next_population = [ self.dna.crossover(*parents) for parents in couples ]
			for dna in next_population:
				if random() < mutation_rate:
					self.dna.mutate(dna)

			# Replace the old population with the new population
			self.population = next_population

			it += 1

		# Return the fitness score of the best individual in the final population
		return max(scores)

			

