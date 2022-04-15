import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import multiprocessing
import pickle
from sklearn.datasets import load_iris
from matplotlib import pyplot

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import rpy2.robjects as robjects
from meta_features.ecol import Ecol

import setup.setup_framework as setup
from instances_generator.generator import InstancesGenerator
import extractor
import preprocess

# TODO: Implement Setup in a minimal main()
options = setup.get_options()

cont = 0
bobj = 0.4
P = [12]
SCALES = [1]
tread = ""
select_new_dataset = "N"
NGEN = 1000
# NGEN = options['NGEN']
CXPB = 0.7
MUTPB = 0.2
INDPB = 0.05
POP = 100

# TODO: Implement Generator of Instances in a minimal main()
gen_instances = InstancesGenerator(options)
df = gen_instances.generate(options['maker'][0])

filename = options['filename'] if options['filename'] != "" else "NGEN=" + \
    str(NGEN)

metrics = options['measures']

# TODO: Implement fitness global measures in a minimal main()
global_measures = []
if (options['filepath'] != ""):
    base_df = pd.read_csv(options['filepath'])
    target = options['label_name']

    # Copying Columns names
    # df.columns = preprocess.copyFeatureNamesFrom(base_df, label_name=target)

    # Extraction of Data Complexity Values
    global_measures = tuple(extractor.complexity(base_df, target, metrics))
else:
    for metric in metrics:
        global_measures.append(options[metric])
    global_measures = tuple(global_measures)

filename += '-' + '-'.join(metrics)
N_ATTRIBUTES = int(options['samples']) # mispelled variable name
print(metrics, len(metrics))
print(global_measures)
NOBJ = len(metrics)

dic = {}

# reference points
ref_points = [tools.uniform_reference_points(
    NOBJ, p, s) for p, s in zip(P, SCALES)]
ref_points = np.concatenate(ref_points)
_, uniques = np.unique(ref_points, axis=0, return_index=True)
ref_points = ref_points[uniques]

def my_evaluate(individual):
    vetor = []
    dataFrame['label'] = individual
    ecolTest.update_label(individual)
    robjects.globalenv['dataFrame'] = dataFrame

    for global_value, metrica in zip(global_measures, metrics):
        complexity_value = extractor.complexity_optimized(ecolTest, metrica)
        vetor.append(abs(global_value - complexity_value))

    return tuple(vetor)

def print_evaluate(individual):
    vetor = []
    dataFrame['label'] = individual
    ecolTest.update_label(individual)
    robjects.globalenv['dataFrame'] = dataFrame

    for metrica in metrics:
        complexity_value = extractor.complexity_optimized(ecolTest, metrica)
        vetor.append(abs(complexity_value))

    return tuple(vetor)


creator.create("FitnessMin", base.Fitness, weights=(-1.0,)*NOBJ)
creator.create("Individual", list, fitness=creator.FitnessMin)

RANDINT_LOW = 0
RANDINT_UP = options['classes'] - 1

toolbox = base.Toolbox()
toolbox.register("attr_int", random.randint, RANDINT_LOW, RANDINT_UP)
toolbox.register("individual", tools.initRepeat,
                 creator.Individual, toolbox.attr_int, N_ATTRIBUTES)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", my_evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=INDPB)
toolbox.register("select", tools.selNSGA3, ref_points=ref_points)


def main(seed=None):
    random.seed(64)
    pool = multiprocessing.Pool(processes=12)
    toolbox.register("map", pool.map)
    # Initialize statistics object
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)

    logbook = tools.Logbook()
    logbook.header = "gen", "evals", "std", "min", "avg", "max"

    pop = toolbox.population(POP)

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    # Compile statistics about the population
    record = stats.compile(pop)

    logbook.record(gen=0, evals=len(invalid_ind), **record)
    print(logbook.stream)
    # Begin the generational process
    for gen in range(1, NGEN):
        offspring = algorithms.varAnd(pop, toolbox, CXPB, MUTPB)
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        # Select the next generation population from parents and offspring
        pop = toolbox.select(pop + offspring, POP)

        # Compile statistics about the new population
        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)
        print(logbook.stream)
    return pop, logbook


if __name__ == '__main__':
    cont1 = 0
    cont0 = 0
    #dataFrame = pd.read_csv(str(N_ATTRIBUTES) + '.csv')
    #dataFrame = dataFrame.drop('c0', axis=1)
    dataFrame = df
    ecolTest = Ecol(dataframe=dataFrame, label='label')
    results = main()
    print("logbook")
    print(results[0][0])
    for x in range(len(results[0])):
        dic[print_evaluate(results[0][x])] = results[0][x]
        outfile = open(filename, 'wb')
        pickle.dump(dic, outfile)
        outfile.close()

    df['label'] = results[0][0]
    # Scale to original Dataset (Optional) #TODO: Improve preprocessing
    # df = preprocess.scaleColumnsFrom(base_df, df, label_column='label')
    df.to_csv(str(filename)+".csv")
    ax1 = df.plot.scatter(x=0, y=1, c='label', colormap='Paired')
    pyplot.show()
