# Python modules
import sys
import random

# Simpy modules
from SimPy.Simulation import *
from SimPy.SimPlot import *

# CloudSim modules
from GlobalVars import *
from Scenario import *
from Scheduler import *
from SchedulingAlgos import *
from TaskGenerator import *
from Task import *
from AbstractResource import *
from CloudMachine import *

currentMachine=0

arguments = [
             ('--grid-size', 'number of machines in the grid', 'integer', ),
             ('--scheduling-algorithm', 'scheduling algorithm', 'one of random, least_full, round_robin, fill_queue', ),
             ('--scheduler-qs', 'scheduler queue size', 'integer', ),
             ('--machine-qs', 'machine queue size', 'integer',  ),
             ('--scheduler-ht', 'scheduler hold time', 'float', ),
             ('--task-class-seed', 'seed used to do task class selection', 'integer'),
             ('--task-duration-seed', 'seed used to generate task duration', 'integer'),
             ('--task-arrival-seed', 'seed used to generate task arrivals', 'integer'),
             ('--task-arrival-mean', 'Mean task arrival rate', 'float'),
             ('--task-class', 'defines a task class, 4 values are needed: name probability time', 'string float int')
             ]

algorithms_map = {'random':random_schedule,
                  'least_full':least_full,
                  'round_robin':round_robin,
                  'fill_queue':fill_queue}

def usage():
    string = 'USAGE:\n'
    global arguments
    for arg in arguments:
        string = string + ('Argument: %s (%s) - type: %s\n' % arg)
        
    string += '\nArguments are passed as follow: simgrid.py --argument-name value'
    return string

def parse_args(scenario):
    import sys
    if len(sys.argv) == 1:
        #we have only one argument, return (we use default values)
        return
    
    args = sys.argv[1:]
    if len(args) == 1 and 'help' in args[0]:
        print usage()
        sys.exit()
    
    task_classes = []
    index = 0
    while index < len(args):
        if args[index] == '--grid-size':
            value = int(args[index+1])
            if value <= 0:
                raise Exception, '--grid-size must be positive'
            scenario.grid_description = [(value,1)]
            index += 2
        
        elif args[index] == '--scheduling-algorithm':
            scenario.schedule_algorithm = algorithms_map[args[index+1]]
            index += 2
            
        elif args[index] == '--scheduler-qs':
            value = int(args[index+1])
            if value <= 0:
                raise Exception, '--scheduler-qs must be positive'
            scenario.scheduler_queue_size = value
            index += 2
            
        elif args[index] == '--machine-qs':
            value = int(args[index+1])
            if value <= 0:
                raise Exception, '--machine-qs must be positive'
            scenario.machine_queue_size = value
            index += 2
        
        elif args[index] == '--scheduler-ht':
            value = float(args[index+1])
            if value <= 0:
                raise Exception, '--scheduler-ht must be positive'
            scenario.scheduler_hold_time = value
            index += 2

        elif args[index] == '--task-class-seed':
            value = int(args[index+1])
            if value <= 0:
                raise Exception, '--task-class-seed must be positive'
            scenario.task_class_selector_seed = value
            index += 2
            
        elif args[index] == '--task-duration-seed':
            value = int(args[index+1])
            if value <= 0:
                raise Exception, '--task-duration-seed must be positive'
            scenario.task_duration_seed = value
            index += 2
            
        elif args[index] == '--task-arrival-seed':
            value = int(args[index+1])
            if value <= 0:
                raise Exception, '--task-arrival-seed must be positive'
            scenario.task_arrival_seed = value
            index += 2
            
        elif args[index] == '--task-arrival-mean':
            value = float(args[index+1])
            if value <= 0:
                raise Exception, '--task-arrival-mean must be positive'
            scenario.task_arrival_mean = value
            index += 2
            
        elif args[index] == '--task-class':
            name = args[index+1]
            prob = float(args[index+2])
            mintime = int(args[index+3])
            maxtime = int(args[index+4])
            task_classes.append((name, prob, mintime, maxtime))
            index+=5

        else:
            raise Exception, 'Unknown option:' + str(args[index])
        
        if len(task_classes) > 0:
            scenario.task_distribution = task_classes

def run(scenario, verbose=True):
    scenario.init_objects()
    initialize()
    
    taskGenerator = TaskGenerator(scenario)
    activate(taskGenerator, taskGenerator.run(scenario.sim_time))
       
    simulate(until=scenario.sim_time)
    
    if verbose:
        print "Total tasks:", scenario.total_arriving_tasks
        print "task arrival seed: ", scenario.task_arrival_seed
        print "task class seed: ", scenario.task_class_selector_seed
        print "task duration seed: ", scenario.task_duration_seed
    
    return scenario, now()

def main():
    scenario = CloudSimScenario()
    parse_args(scenario)
    return run(scenario)
    
if __name__ == '__main__':
    main()

