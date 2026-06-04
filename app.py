from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)


def generate_random_chromosome(length):
    return [random.randint(0, 1) for _ in range(length)]


def fitness(chromosome, target):
    return sum(1 for g, t in zip(chromosome, target) if g == t)


def tournament_selection(population, target, k=3):
    contenders = random.sample(population, k)
    contenders.sort(key=lambda c: fitness(c, target), reverse=True)
    return contenders[0]


def crossover(parent1, parent2, crossover_rate):
    if random.random() > crossover_rate:
        return parent1[:], parent2[:]

    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def mutate(chromosome, mutation_rate):
    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            chromosome[i] = 1 - chromosome[i]
    return chromosome


def run_ga(target, population_size, generations, crossover_rate, mutation_rate):
    target = [int(x) for x in target]
    chromosome_length = len(target)

    population = [generate_random_chromosome(chromosome_length) for _ in range(population_size)]
    history = []

    best_solution = None
    best_fitness = -1

    for generation in range(generations):
        population.sort(key=lambda c: fitness(c, target), reverse=True)

        current_best = population[0]
        current_best_fitness = fitness(current_best, target)

        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_solution = current_best[:]

        history.append(best_fitness)

        if best_fitness == chromosome_length:
            break

        new_population = []

        # Elitism: keep the best chromosome
        new_population.append(current_best[:])

        while len(new_population) < population_size:
            parent1 = tournament_selection(population, target)
            parent2 = tournament_selection(population, target)

            child1, child2 = crossover(parent1, parent2, crossover_rate)
            child1 = mutate(child1, mutation_rate)
            child2 = mutate(child2, mutation_rate)

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        population = new_population

    return {
        "best_solution": "".join(map(str, best_solution)),
        "best_fitness": best_fitness,
        "max_fitness": chromosome_length,
        "generations_ran": len(history),
        "history": history
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json()

    target = data.get("target", "11110000")
    population_size = int(data.get("population_size", 30))
    generations = int(data.get("generations", 100))
    crossover_rate = float(data.get("crossover_rate", 0.8))
    mutation_rate = float(data.get("mutation_rate", 0.01))

    if not target or any(ch not in "01" for ch in target):
        return jsonify({"error": "Target must contain only 0 and 1."}), 400

    if population_size < 2:
        return jsonify({"error": "Population size must be at least 2."}), 400

    if len(target) < 2:
        return jsonify({"error": "Target length must be at least 2."}), 400

    result = run_ga(
        target=target,
        population_size=population_size,
        generations=generations,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate
    )

    result["target"] = target
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)