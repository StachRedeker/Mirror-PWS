import os
import neat

def main(genomes, config):
    networks = []
    ge = []
    choices = []

    for _, genome in genomes:
        network = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(network)

        genome.fitness = 0
        ge.append(genome)

        choices.append([])

    for x in range(25):
        for i, genome in enumerate(ge):
            output = networks[i].activate([x, x%2])

            # print(str(x) + " - " + str(i) + " chose " + str(output[0]))
            if output[0] > 0.5:
                if x % 2 == 0:
                    ge[i].fitness += 1
                    choices[i].append(1)
                else:
                    ge[i].fitness -= 5
                    choices[i].append(0)
            else:
                if not x % 2 == 0:
                    ge[i].fitness += 1
                    choices[i].append(1)
                else:
                    ge[i].fitness -= 5
                    choices[i].append(0)
                    pass
            
            # Optional death function, if I use this there are no winners at any point.
            # if ge[i].fitness <= 20:
            #     ge[i].fitness -= 100
            #     ge.pop(i)
            #     choices.pop(i)
            #    networks.pop(i)
    if len(ge) > 0:
        fittest = -1
        fitness = -999999
        for i, genome in enumerate(ge):
            if ge[i].fitness > fitness:
                fittest = i
                fitness = ge[i].fitness

        print("Best: " + str(fittest) + " with fitness " + str(fitness))
        print(str(choices[fittest]))
    else:
        print("Done with no best.")

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    pop = neat.Population(config)

    #pop.add_reporter(neat.StdOutReporter(True))
    #stats = neat.StatisticsReporter()
    #pop.add_reporter(stats)

    winner = pop.run(main, 100)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
