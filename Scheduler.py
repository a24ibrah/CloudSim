from SimPy.Simulation import *
from AbstractResource import *
from CloudMachine import *

class Scheduler(Process):
    def __init__(self, scenario, name="Scheduler"):
        Process.__init__ (self, name=name)
        self.scenario = scenario

        self.started = False

        self.genId = 0
        self.activeMachines = []
        self.destroyedMachines = []

        # [0] startTime
        # [1] remainingJobs
        self.taskInfos = {}
        self.taskJobs = {}

        self.tasksRT = []
        self.jobsRT = []

        temp = scenario.addMonitor ("activeNodesMon")
        scenario.addMonitorPlot ("Running nodes", temp)

        temp = scenario.addMonitor ("activeJobsMon")
        scenario.addMonitorPlot ("Running Jobs", temp)

        temp = scenario.addMonitor("jobRTAvgMon")
        scenario.addMonitorPlot ("Average job response time", temp)

        temp = scenario.addMonitor("taskRTAvgMon")
        scenario.addMonitorPlot ("Average task response time", temp)

        temp = scenario.addMonitor("executionCostMon")
        scenario.addMonitorPlot ("Cost of execution", temp)

    def addJob(self, job):
        job.startTime = now()
        
        jobList = self.taskJobs.get(job.taskId)
        if(jobList == None):
            jobList = []
            taskInfo = [job.startTime, job.numjobs]
            self.taskInfos[job.taskId] = taskInfo
        
        jobList.append(job)
        self.taskJobs[job.taskId] = jobList

    def jobFinished(self, job):
        finishTime = now()

        # Remove job from job list
        self.taskJobs[job.taskId].remove(job)

        # Calculate job service time
        jobRT = finishTime - job.startTime
        self.jobsRT.append(jobRT)


        # Complete job in task info and check if
        # task is completed
        taskInfo = self.taskInfos[job.taskId]
        taskInfo[1] -= 1
        
        # No tasks remaining - Task finished!
        if(taskInfo[1] == 0):
            # Calculate task service time
            taskRT = finishTime - taskInfo[0] #initialTime
            self.tasksRT.append(taskRT)

    def run(self):

        # Create initial machines
        for m_id in range(self.scenario.initial_machines):
           self.createMachine(1)

        self.started = True

        while (self.started):
            allocations = self.scenario.schedule_algorithm (self.activeMachines, self.taskJobs)

            # iterate over allocations generated by scheduling algorithm
            for machine_job in allocations:
                machine = machine_job[0]
                job = machine_job[1]

                if(machine == None and job == None):
                  # Invalid allocation
                  continue

                # if job is undefined, shutdown machine
                if(job == None):
                    self.destroyMachine(machine)
                else:
                    # if machine is undefined, start job
                    if(machine == None):
                        machine = self.createMachine()

                    # start job on machine
                    machine.addJob(job)
            
            self.scenario.monitors ["activeJobsMon"].observe (sum(map(lambda x: len(x), self.taskJobs.values())))
            self.scenario.monitors ["activeNodesMon"].observe (len(self.activeMachines))

            if(len(self.jobsRT) > 0):
                self.scenario.monitors ["jobRTAvgMon"].observe (sum(self.jobsRT)/len(self.jobsRT))
            if(len(self.tasksRT) > 0):
                self.scenario.monitors ["taskRTAvgMon"].observe (sum(self.tasksRT)/len(self.tasksRT))

            currentCost = 0.0
            for machine in self.activeMachines+self.destroyedMachines:
                currentCost += machine.getExecutionTime() * self.scenario.wn_cost
            self.scenario.monitors ["executionCostMon"].observe (currentCost)

            yield hold, self, self.scenario.sch_interval
        
    def destroyMachine(self, machine):
        machine.stop()
        cancel(machine)
        self.activeMachines.remove(machine)
        self.destroyedMachines.append(machine)

    def createMachine(self, started=0):
        machine = CloudMachine(self.genId, self.scenario, started)
        self.activeMachines.append(machine)
        self.genId += 1
        activate(machine, machine.start())
        return machine


    def stop(self):
        self.started = False

