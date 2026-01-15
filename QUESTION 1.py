import numpy as np
import pandas as pd
import streamlit as st
from typing import List

# -------------------- FIXED GA PARAMETERS --------------------
POPULATION_SIZE = 300
CHROMOSOME_LENGTH = 80
GENERATIONS = 50
TARGET_ONES = 40
MAX_FITNESS = 80

CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.01
TOURNAMENT_K = 3
ELITISM = 2
SEED = 42


# -------------------- FITNESS FUNCTION --------------------
def fitness_function(bitstring: np.ndarray) -> float:
    ones = np.sum(bitstring)
    return MAX_FITNESS - abs(ones - TARGET_ONES)


# -------------------- GA OPERATORS --------------------
def init_population(rng: np.random.Generator) -> np.ndarray:
    return rng.integers(0, 2, size=(POPULATION_SIZE, CHROMOSOME_LENGTH), dtype=np.int8)


def tournament_selection(fitness: np.ndarray, rng: np.random.Generator) -> int:
    idx = rng.integers(0, len(fitness), size=TOURNAMENT_K)
    return idx[np.argmax(fitness[idx])]


def one_point_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator):
    point = rng.integers(1, CHROMOSOME_LENGTH)
    return (
        np.concatenate([a[:point], b[point:]]),
        np.concatenate([b[:point], a[point:]])
    )


def bit_mutation(x: np.ndarray, rng: np.random.Generator):
    mask = rng.random(x.shape) < MUTATION_RATE
    x[mask] = 1 - x[mask]
    return x


# -------------------- GA MAIN LOOP --------------------
def run_ga():
    rng = np.random.default_rng(SEED)
    population = init_population(rng)

    history_best: List[float] = []
    history_avg: List[float] = []

    for gen in range(GENERATIONS):
        fitness = np.array([fitness_function(ind) for ind in population])

        history_best.append(np.max(fitness))
        history_avg.append(np.mean(fitness))

        elite_idx = np.argsort(fitness)[-ELITISM:]
        elites = population[elite_idx]

        next_population = []

        while len(next_population) < POPULATION_SIZE - ELITISM:
            p1 = population[tournament_selection(fitness, rng)]
            p2 = population[tournament_selection(fitness, rng)]

            if rng.random() < CROSSOVER_RATE:
                c1, c2 = one_point_crossover(p1, p2, rng)
            else:
                c1, c2 = p1.copy(), p2.copy()

            next_population.append(bit_mutation(c1, rng))
            if len(next_population) < POPULATION_SIZE - ELITISM:
                next_population.append(bit_mutation(c2, rng))

        population = np.vstack([next_population, elites])

    final_fitness = np.array([fitness_function(ind) for ind in population])
    best_idx = np.argmax(final_fitness)

    return {
        "best": population[best_idx],
        "best_fitness": final_fitness[best_idx],
        "history": pd.DataFrame({
            "Best Fitness": history_best,
            "Average Fitness": history_avg
        })
    }


# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Bit Pattern Generator using GA", layout="wide")
st.title("🧬 Genetic Algorithm Bit Pattern Generator")
st.caption("Fixed-parameter GA with fitness peak at 40 ones")

st.markdown("""
**Fixed Parameters**
- Population Size: 300  
- Chromosome Length: 80 bits  
- Generations: 50  
- Fitness Peak: 40 ones  
- Maximum Fitness: 80  
""")

if st.button("Run Genetic Algorithm", type="primary"):
    result = run_ga()

    st.subheader("Fitness Evolution")
    st.line_chart(result["history"])

    st.subheader("Best Bit Pattern")
    bitstring = ''.join(map(str, result["best"].tolist()))
    st.code(bitstring)

    st.write(f"**Best Fitness:** {result['best_fitness']:.2f}")
    st.write(f"**Number of Ones:** {int(np.sum(result['best']))} / {CHROMOSOME_LENGTH}")
