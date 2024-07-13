import streamlit as st
import prettytable as prettytable
import random as rnd
import pandas as pd

POPULATION_SIZE = 4
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 3
MUTATION_RATE = 0.1

class Data:
    ROOMS = [["D22", 45], ["C17", 50], ["R109", 40]]
    MEETING_TIMES = [["MT1", "MWF 09:00 - 10:00"],
                     ["MT2", "MWF 10:00 - 11:00"],
                     ["MT3", "TTH 09:00 - 10:30"],
                     ["MT4", "TTH 10:30 - 12:00"],
                     ["MT5", "TTH 11:30 - 12:30"]]
    INSTRUCTORS = [["I1", "Dr Farrukh"],
                   ["I2", "Mr. Karez"],
                   ["I3", "Dr Rafi"],
                   ["I4", "Mr Ali"]]

    def __init__(self):
        self._rooms = [Room(number, capacity) for number, capacity in self.ROOMS]
        self._meetingTimes = [MeetingTime(id, time) for id, time in self.MEETING_TIMES]
        self._instructors = [Instructor(id, name) for id, name in self.INSTRUCTORS]
        
        # Initialize courses
        self._courses = [
            Course("C1", "AI2002", [self._instructors[0], self._instructors[1]], 25),
            Course("C2", "CL3001", [self._instructors[0], self._instructors[1], self._instructors[2]], 35),
            Course("C3", "CS3009", [self._instructors[0], self._instructors[1]], 25),
            Course("C4", "SS2007", [self._instructors[2], self._instructors[3]], 30),
            Course("C5", "CS4053", [self._instructors[3]], 35),
            Course("C6", "CS2009", [self._instructors[0], self._instructors[2]], 45),
            Course("C7", "CS2005", [self._instructors[1], self._instructors[3]], 45),
        ]
        
        # Initialize departments
        self._depts = [
            Department("CS", [self._courses[0], self._courses[2]]),
            Department("EE", [self._courses[1], self._courses[3], self._courses[4]]),
            Department("AI", [self._courses[5], self._courses[6]])
        ]
        self._numberOfClasses = sum(len(dept.get_courses()) for dept in self._depts)

    def get_rooms(self): return self._rooms
    def get_instructors(self): return self._instructors
    def get_courses(self): return self._courses
    def get_depts(self): return self._depts
    def get_meetingTimes(self): return self._meetingTimes
    def get_numberOfClasses(self): return self._numberOfClasses


class Schedule:
    def __init__(self, data):
        self._data = data
        self._classes = []
        self._numbOfConflicts = 0
        self._fitness = -1
        self._classNumb = 0
        self._isFitnessChanged = True

    def get_classes(self):
        self._isFitnessChanged = True
        return self._classes
    
    def get_numbOfConflicts(self): return self._numbOfConflicts
    
    def get_fitness(self):
        if self._isFitnessChanged:
            self._fitness = self.calculate_fitness()
            self._isFitnessChanged = False
        return self._fitness
    
    def initialize(self):
        depts = self._data.get_depts()
        for dept in depts:
            for course in dept.get_courses():
                newClass = Class(self._classNumb, dept, course)
                self._classNumb += 1
                newClass.set_meetingTime(self._data.get_meetingTimes()[rnd.randrange(len(self._data.get_meetingTimes()))])
                newClass.set_room(self._data.get_rooms()[rnd.randrange(len(self._data.get_rooms()))])
                newClass.set_instructor(course.get_instructors()[rnd.randrange(len(course.get_instructors()))])
                self._classes.append(newClass)
        return self
    
    def calculate_fitness(self):
        self._numbOfConflicts = 0
        classes = self.get_classes()
        for i in range(len(classes)):
            if classes[i].get_room().get_seatingCapacity() < classes[i].get_course().get_maxNumbOfStudents():
                self._numbOfConflicts += 1
            for j in range(len(classes)):
                if j >= i:
                    if (classes[i].get_meetingTime() == classes[j].get_meetingTime() and
                        classes[i].get_id() != classes[j].get_id()):
                        if classes[i].get_room() == classes[j].get_room(): 
                            self._numbOfConflicts += 1
                        if classes[i].get_instructor() == classes[j].get_instructor(): 
                            self._numbOfConflicts += 1
        return 1 / (1.0 * self._numbOfConflicts + 1)
    
    def __str__(self):
        return ", ".join(str(cls) for cls in self._classes)


class Population:
    def __init__(self, size, data):
        self._size = size
        self._data = data
        self._schedules = [Schedule(data).initialize() for _ in range(size)]

    def get_schedules(self): return self._schedules


class GeneticAlgorithm:
    def evolve(self, population): 
        return self._mutate_population(self._crossover_population(population))
    
    def _crossover_population(self, pop):
        crossover_pop = Population(0, pop._data)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        i = NUMB_OF_ELITE_SCHEDULES
        while i < POPULATION_SIZE:
            schedule1 = self._select_tournament_population(pop).get_schedules()[0]
            schedule2 = self._select_tournament_population(pop).get_schedules()[0]
            crossover_pop.get_schedules().append(self._crossover_schedule(schedule1, schedule2))
            i += 1
        return crossover_pop
    
    def _mutate_population(self, population):
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.get_schedules()[i])
        return population
    
    def _crossover_schedule(self, schedule1, schedule2):
        crossoverSchedule = Schedule(schedule1._data).initialize()
        for i in range(len(crossoverSchedule.get_classes())):
            if rnd.random() > 0.5:
                crossoverSchedule.get_classes()[i] = schedule1.get_classes()[i]
            else:
                crossoverSchedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossoverSchedule
    
    def _mutate_schedule(self, mutateSchedule):
        schedule = Schedule(mutateSchedule._data).initialize()
        for i in range(len(mutateSchedule.get_classes())):
            if MUTATION_RATE > rnd.random():
                mutateSchedule.get_classes()[i] = schedule.get_classes()[i]
        return mutateSchedule
    
    def _select_tournament_population(self, pop):
        tournament_pop = Population(0, pop._data)
        for _ in range(TOURNAMENT_SELECTION_SIZE):
            tournament_pop.get_schedules().append(pop.get_schedules()[rnd.randrange(POPULATION_SIZE)])
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop


class Course:
    def __init__(self, number, name, instructors, maxNumbOfStudents):
        self._number = number
        self._name = name
        self._maxNumbOfStudents = maxNumbOfStudents
        self._instructors = instructors
        
    def get_number(self): return self._number
    def get_name(self): return self._name
    def get_instructors(self): return self._instructors
    def get_maxNumbOfStudents(self): return self._maxNumbOfStudents
    
    def __str__(self): return self._name


class Instructor:
    def __init__(self, id, name):
        self._id = id
        self._name = name
        
    def get_id(self): return self._id
    def get_name(self): return self._name
    
    def __str__(self): return self._name


class Room:
    def __init__(self, number, seatingCapacity):
        self._number = number
        self._seatingCapacity = seatingCapacity
        
    def get_number(self): return self._number
    def get_seatingCapacity(self): return self._seatingCapacity


class MeetingTime:
    def __init__(self, id, time):
        self._id = id
        self._time = time
        
    def get_id(self): return self._id
    def get_time(self): return self._time


class Department:
    def __init__(self, name, courses):
        self._name = name
        self._courses = courses
        
    def get_name(self): return self._name
    def get_courses(self): return self._courses


class Class:
    def __init__(self, id, dept, course):
        self._id = id
        self._dept = dept
        self._course = course
        self._instructor = None
        self._meetingTime = None
        self._room = None
        
    def get_id(self): return self._id
    def get_dept(self): return self._dept
    def get_course(self): return self._course
    def get_instructor(self): return self._instructor
    def get_meetingTime(self): return self._meetingTime
    def get_room(self): return self._room
    def set_instructor(self, instructor): self._instructor = instructor
    def set_meetingTime(self, meetingTime): self._meetingTime = meetingTime
    def set_room(self, room): self._room = room
    
    def __str__(self):
        return f"{self._dept.get_name()}, {self._course.get_number()}, {self._room.get_number()}, {self._instructor.get_id()}, {self._meetingTime.get_id()}"


class DisplayMgr:
    def print_available_data(self, data):
        st.write("> All Available Data")
        self.print_dept(data)
        available_courses = data.get_courses()
        self.print_course(available_courses)
        self.print_room(data)
        self.print_instructor(data)
        self.print_meeting_times(data)

    def print_course(self, available_courses):
        table_data = []
        for course in available_courses:
            table_data.append([
                course.get_number(),
                course.get_name(),
                course.get_maxNumbOfStudents(),
                ", ".join(instructor.get_name() for instructor in course.get_instructors())
            ])
        df = pd.DataFrame(table_data, columns=['Course #', 'Course Name', 'Max # of Students', 'Instructors'])
        st.table(df)

    def print_dept(self, data):
        depts = data.get_depts()
        table_data = []
        for dept in depts:
            course_names = ", ".join(course.get_name() for course in dept.get_courses())
            table_data.append([dept.get_name(), course_names])
        df = pd.DataFrame(table_data, columns=['Department', 'Courses'])
        st.table(df)

    def print_room(self, data):
        rooms = data.get_rooms()
        table_data = []
        for room in rooms:
            table_data.append([room.get_number(), room.get_seatingCapacity()])
        df = pd.DataFrame(table_data, columns=['Room #', 'Max Seating Capacity'])
        st.table(df)

    def print_instructor(self, data):
        instructors = data.get_instructors()
        table_data = []
        for instructor in instructors:
            table_data.append([instructor.get_id(), instructor.get_name()])
        df = pd.DataFrame(table_data, columns=['Instructor ID', 'Instructor Name'])
        st.table(df)

    def print_meeting_times(self, data):
        meeting_times = data.get_meetingTimes()
        table_data = []
        for meeting_time in meeting_times:
            table_data.append([meeting_time.get_id(), meeting_time.get_time()])
        df = pd.DataFrame(table_data, columns=['Meeting Time ID', 'Meeting Time'])
        st.table(df)

    def print_generation(self, population):
        st.write("Generation Results:")
        for gen in range(len(population.get_schedules())):
            st.write(f"Generation #{gen}")

    def print_schedule_as_table(self, schedule):
        table_data = []
        for item in schedule.get_classes():
            table_data.append([
                item.get_dept().get_name(),  # Adjust this based on your structure
                item.get_course().get_name()
            ])
        df = pd.DataFrame(table_data, columns=['Department', 'Course Name'])
        st.table(df)


# Initialize data and display
data = Data()
st.title("Class Scheduling Application")
displayMgr = DisplayMgr()

# Display available data
if st.button("Show Available Data"):
    displayMgr.print_available_data(data)

# Initialize population and run genetic algorithm
if st.button("Run Scheduling Algorithm"):
    generationNumber = 0
    population = Population(POPULATION_SIZE, data)
    population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)

    st.write(f"### Generation # {generationNumber}")
    displayMgr.print_generation(population)

    while population.get_schedules()[0].get_fitness() != 1.0:
        generationNumber += 1
        population = GeneticAlgorithm().evolve(population)
        population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)

        st.write(f"### Generation # {generationNumber}")
        displayMgr.print_generation(population)

    st.write("### Optimal Schedule Found")
    displayMgr.print_schedule_as_table(population.get_schedules()[0])





