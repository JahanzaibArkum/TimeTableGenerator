import streamlit as st
import prettytable as prettytable
import random as rnd
import pandas as pd

POPULATION_SIZE = 4
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 3
MUTATION_RATE = 0.1

class Data:
    ROOMS = [["D22",45], ["C17",50], ["R109",40]]
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
        self._rooms = []; self._meetingTimes = []; self._instructors = []
        for i in range(0, len(self.ROOMS)):
            self._rooms.append(Room(self.ROOMS[i][0], self.ROOMS[i][1]))
        for i in range(0, len(self.MEETING_TIMES)):
            self._meetingTimes.append(MeetingTime(self.MEETING_TIMES[i][0], self.MEETING_TIMES[i][1]))
        for i in range(0, len(self.INSTRUCTORS)):
            self._instructors.append(Instructor(self.INSTRUCTORS[i][0], self.INSTRUCTORS[i][1]))
        course1 = Course("C1", "AI2002", [self._instructors[0], self._instructors[1]], 25)
        course2 = Course("C2", "CL3001", [self._instructors[0], self._instructors[1], self._instructors[2]], 35)
        course3 = Course("C3", "CS3009", [self._instructors[0], self._instructors[1]], 25)
        course4 = Course("C4", "SS2007", [self._instructors[2], self._instructors[3]], 30)
        course5 = Course("C5", "CS4053", [self._instructors[3]], 35)
        course6 = Course("C6", "CS2009", [self._instructors[0], self._instructors[2]], 45)
        course7 = Course("C7", "CS2005", [self._instructors[1], self._instructors[3]], 45)
        self._courses = [course1, course2, course3, course4, course5, course6, course7]
        dept1 = Department("CS", [course1, course3])
        dept2 = Department("EE", [course2, course4, course5])
        dept3 = Department("AI", [course6, course7])
        self._depts = [dept1, dept2, dept3]
        self._numberOfClasses = 0
        for i in range(0, len(self._depts)):
            self._numberOfClasses += len(self._depts[i].get_courses())
            
    def get_rooms(self): return self._rooms
    def get_instructors(self): return self._instructors
    def get_courses(self): return self._courses
    def get_depts(self): return self._depts
    def get_meetingTimes(self): return self._meetingTimes
    def get_numberOfClasses(self): return self._numberOfClasses
    
class Schedule:
    
    def __init__(self):
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
        if (self._isFitnessChanged == True):
            self._fitness = self.calculate_fitness()
            self._isFitnessChanged = False
        return self._fitness
    
    def initialize(self):
        depts = self._data.get_depts()
        for i in range(0, len(depts)):
            courses = depts[i].get_courses()
            for j in range(0, len(courses)):
                newClass = Class(self._classNumb, depts[i], courses[j])
                self._classNumb += 1
                newClass.set_meetingTime(data.get_meetingTimes()[rnd.randrange(0, len(data.get_meetingTimes()))])
                newClass.set_room(data.get_rooms()[rnd.randrange(0, len(data.get_rooms()))])
                newClass.set_instructor(courses[j].get_instructors()[rnd.randrange(0, len(courses[j].get_instructors()))])
                self._classes.append(newClass)
        return self
    
    def calculate_fitness(self):
        self._numbOfConflicts = 0
        classes = self.get_classes()
        for i in range(0, len(classes)):
            if (classes[i].get_room().get_seatingCapacity() < classes[i].get_course().get_maxNumbOfStudents()):
                self._numbOfConflicts += 1
            for j in range(0, len(classes)):
                if (j >= i):
                    if (classes[i].get_meetingTime() == classes[j].get_meetingTime() and
                    classes[i].get_id() != classes[j].get_id()):
                        if (classes[i].get_room() == classes[j].get_room()): self._numbOfConflicts += 1
                        if (classes[i].get_instructor() == classes[j].get_instructor()): self._numbOfConflicts += 1
        return 1 / ((1.0*self._numbOfConflicts + 1))
    
    def __str__(self):
        returnValue = ""
        for i in range(0, len(self._classes)-1):
            returnValue += str(self._classes[i]) + ", "
        returnValue += str(self._classes[len(self._classes)-1])
        return returnValue
    
class Population:
    def __init__(self, size):
        self._size = size
        self._data = data
        self._schedules = []
        for i in range(0, size): self._schedules.append(Schedule().initialize())
    def get_schedules(self): return self._schedules
    
class GeneticAlgorithm:
    
    def evolve(self, population): return self._mutate_population(self._crossover_population(population))
    
    def _crossover_population(self, pop):
        crossover_pop = Population(0)
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
        crossoverSchedule = Schedule().initialize()
        for i in range(0, len(crossoverSchedule.get_classes())):
            if (rnd.random() > 0.5): crossoverSchedule.get_classes()[i] = schedule1.get_classes()[i]
            else: crossoverSchedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossoverSchedule
    
    def _mutate_schedule(self, mutateSchedule):
        schedule = Schedule().initialize()
        for i in range(0, len(mutateSchedule.get_classes())):
            if(MUTATION_RATE > rnd.random()): mutateSchedule.get_classes()[i] = schedule.get_classes()[i]
        return mutateSchedule
    
    def _select_tournament_population(self, pop):
        tournament_pop = Population(0)
        i = 0
        while i < TOURNAMENT_SELECTION_SIZE:
            tournament_pop.get_schedules().append(pop.get_schedules()[rnd.randrange(0, POPULATION_SIZE)])
            i += 1
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
        return str(self._dept.get_name()) + "," + str(self._course.get_number()) + "," +                str(self._room.get_number()) + "," + str(self._instructor.get_id()) + "," + str(self._meetingTime.get_id())
    
class DisplayMgr:
    
    def print_available_data(self, data):
        st.write("> All Available Data")
        self.print_dept(data)
        available_courses = data.get_courses()  # Ensure this retrieves the list of courses
        self.print_course(available_courses)  # Pass them to the method
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
        st.table(df)  # Display the DataFrame in Streamlit

    def print_dept(self, data):
        depts = data.get_depts()
        table_data = []

        for dept in depts:
            courses = dept.get_courses()
            course_names = ", ".join(course.get_name() for course in courses)
            table_data.append([dept.get_name(), course_names])

        df = pd.DataFrame(table_data, columns=['Department', 'Courses'])
        st.table(df)  # Display the DataFrame in Streamlit

    def print_room(self, data):
        rooms = data.get_rooms()
        table_data = []

        for room in rooms:
            table_data.append([room.get_number(), room.get_seatingCapacity()])

        df = pd.DataFrame(table_data, columns=['Room #', 'Max Seating Capacity'])
        st.table(df)  # Display the DataFrame in Streamlit

    def print_instructor(self, data):
        instructors = data.get_instructors()
        table_data = []

        for instructor in instructors:
            table_data.append([instructor.get_id(), instructor.get_name()])

        df = pd.DataFrame(table_data, columns=['Instructor ID', 'Instructor Name'])
        st.table(df)  # Display the DataFrame in Streamlit

    def print_meeting_times(self, data):
        meeting_times = data.get_meetingTimes()
        table_data = []

        for meeting_time in meeting_times:
            table_data.append([meeting_time.get_id(), meeting_time.get_time()])

        df = pd.DataFrame(table_data, columns=['Meeting Time ID', 'Meeting Time'])
        st.table(df)  # Display the DataFrame in Streamlit

    def print_generation(self, population):
        st.write("Generation Results:")
        # Assuming population has a method to get schedules
        for gen in range(len(population)):
            st.write(f"Generation #{gen}")
            # You can implement further details based on your structure

    def print_schedule_as_table(self, schedule):
        table_data = []  # Adjust this based on your schedule structure

        for item in schedule:
            table_data.append([
                item.get_some_property(),  # Adjust based on actual properties
                item.get_another_property()
            ])

        df = pd.DataFrame(table_data, columns=['Property 1', 'Property 2'])
        st.table(df)  # Display the schedule in a table
            
            
            
        




data = Data()
st.title("Class Scheduling Application")
displayMgr = DisplayMgr()
displayMgr.print_available_data(available_courses)

generationNumber = 0
print("\n> Generation # "+str(generationNumber))
population = Population(POPULATION_SIZE)
population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
displayMgr.print_generation(population)
displayMgr.print_schedule_as_table(population.get_schedules()[0])
geneticAlgorithm = GeneticAlgorithm()
while (population.get_schedules()[0].get_fitness() != 1.0):
    generationNumber += 1
    print("\n> Generation # " + str(generationNumber))
    population = geneticAlgorithm.evolve(population)
    population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
    displayMgr.print_generation(population)
    displayMgr.print_schedule_as_table(population.get_schedules()[0])
print("\n\n")
# Inside your main script
if st.button("Show Available Data"):
    displayMgr.print_available_data()  # Should work without issues now
    for dept in data.get_depts():
        st.write(f"{dept.get_name()}: {', '.join(course.get_name() for course in dept.get_courses())}")

    st.write("### Instructors")
    for instructor in data.get_instructors():
        st.write(f"{instructor.get_id()}: {instructor.get_name()}")

    st.write("### Rooms")
    for room in data.get_rooms():
        st.write(f"{room.get_number()} - Capacity: {room.get_seatingCapacity()}")

    st.write("### Meeting Times")
    for meeting_time in data.get_meetingTimes():
        st.write(f"{meeting_time.get_id()}: {meeting_time.get_time()}")

# Initialize population and run genetic algorithm
if st.button("Run Scheduling Algorithm"):
    generationNumber = 0
    population = Population(POPULATION_SIZE)
    population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)

    st.write(f"### Generation # {generationNumber}")
    displayMgr.print_generation(population)  # Adjust this to use Streamlit if needed

    while population.get_schedules()[0].get_fitness() != 1.0:
        generationNumber += 1
        population = geneticAlgorithm.evolve(population)
        population.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)

        st.write(f"### Generation # {generationNumber}")
        displayMgr.print_generation(population)  # Adjust this to use Streamlit if needed

    st.write("### Optimal Schedule Found")
    displayMgr.print_schedule_as_table(population.get_schedules()[0])  # Adjust this to use Streamlit


# In[ ]:




