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

import setup.setup_framework as setup
from instances_generator.generator import InstancesGenerator
import complexity as complx
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

metricasList = options['measures']

if (options['filepath'] != ""):
    base_df = pd.read_csv(options['filepath'])
    target = options['label_name']

    # Copying Columns names
    df.columns = preprocess.copyFeatureNamesFrom(base_df, label_name=target)

    if ('C2' in metricasList):
        globalBalance = complx.balance(base_df, target, "C2")
        filename += "-C2"
    if ('L2' in metricasList):
        globalLinear = complx.linearity(base_df, target, "L2")
        print(globalLinear)
        filename += "-L2"
    if ('N1' in metricasList):
        globalN1 = complx.neighborhood(base_df, target, "N1")
        filename += "-N1"
    if ('N2' in metricasList):
        globalN2 = complx.neighborhood(base_df, target, "N2")
        filename += "-N2"
        print("WARNING: N2 is a experimental measure, you may not be able to get efficient results")
    if ('N1' in metricasList):
        globalT1 = complx.neighborhood(base_df, target, "T1")
        filename += "-T1"
        print("WARNING: T1 is a experimental measure, you may not be able to get efficient results")
    if ('F2' in metricasList):
        globalF2 = complx.feature(base_df, target, "F2")
        filename += "-F2"
else:
    if ('C2' in metricasList):
        objetivo = options['C2']
        globalBalance = float(objetivo)
        filename += "-C2"
    if ('L2' in metricasList):
        objetivo = options['L2']
        globalLinear = float(objetivo)
        filename += "-L2"
    if ('N1' in metricasList):
        objetivo = options['N1']
        globalN1 = float(objetivo)
        filename += "-N1"
    if ('N2' in metricasList):
        print("WARNING: N2 is a experimental measure, you may not be able to get efficient results")
        objetivo = options['N2']
        globalN2 = float(objetivo)
        filename += "-N2"
    if ('T1' in metricasList):
        print("WARNING: T1 is a experimental measure, you may not be able to get efficient results")
        objetivo = options['T1']
        globalT1 = float(objetivo)
        filename += "-T1"
    if ('F2' in metricasList):
        objetivo = options['F2']
        globalF2 = float(objetivo)
        filename += "-F2"

N_ATTRIBUTES = int(options['samples']) # mispelled variable name
print(metricasList, len(metricasList))
print(globalN1, globalLinear, globalBalance, globalF2)
NOBJ = len(metricasList)

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
    robjects.globalenv['dataFrame'] = dataFrame
    target = "label"

    if('C2' in metricasList):
        imbalance = complx.balance(dataFrame, target, "C2")
        vetor.append(abs(globalBalance - imbalance))
    if ('L2' in metricasList):
        linearity = complx.linearity(dataFrame, target, "L2")
        vetor.append(abs(globalLinear - linearity))
    if ('N1' in metricasList):
        n1 = complx.neighborhood(dataFrame, target, "N1")
        vetor.append(abs(globalN1 - n1))
    if ('N2' in metricasList):
        n2 = complx.neighborhood(dataFrame, target, "N2")
        vetor.append(abs(globalN2 - n2))
    if ('T1' in metricasList):
        t1 = complx.neighborhood(dataFrame, target, "T1")
        vetor.append(abs(globalT1 - t1))
    if ('F2' in metricasList):
        f2 = complx.feature(dataFrame, target, "F2")
        vetor.append(abs(globalF2 - f2))
    ## --
    if(len(vetor) == 1):
        return vetor[0],
    if(len(vetor) == 2):
        return vetor[0], vetor[1],
    elif(len(vetor) == 3):
        return vetor[0], vetor[1], vetor[2],
    elif(len(vetor) == 4):
        return vetor[0], vetor[1], vetor[2], vetor[3],


def print_evaluate(individual):
    vetor = []
    dataFrame['label'] = individual
    robjects.globalenv['dataFrame'] = dataFrame
    target = "label"
    if('C2' in metricasList):
        imbalance = complx.balance(dataFrame, target, "C2")
        vetor.append(abs(imbalance))
    if ('L2' in metricasList):
        linearity = complx.linearity(dataFrame, target, "L2")
        vetor.append(abs(linearity))
    if ('N1' in metricasList):
        n1 = complx.neighborhood(dataFrame, target, "N1")
        vetor.append(abs(n1))
    if ('N2' in metricasList):
        n2 = complx.neighborhood(dataFrame, target, "N2")
        vetor.append(abs(n2))
    if ('T1' in metricasList):
        t1 = complx.neighborhood(dataFrame, target, "T1")
        vetor.append(abs(t1))
    if ('F2' in metricasList):
        f2 = complx.feature(dataFrame, target, "F2")
        vetor.append(abs(f2))
    ## --
    if(len(vetor) == 1):
        return vetor[0],
    if(len(vetor) == 2):
        return vetor[0], vetor[1],
    elif(len(vetor) == 3):
        return vetor[0], vetor[1], vetor[2],
    elif(len(vetor) == 4):
        return vetor[0], vetor[1], vetor[2], vetor[3],


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
