import random
from collections import defaultdict
import os # Import for file operations


# CONFIGURATION


DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

SLOTS = [
    '8:30-9:30',
    '9:30-10:30',
    '10:30-11:30',
    '11:30-12:30',
    '12:30-1:30'
]

ROOMS = ['C1', 'C2', 'C3', 'C4', 'C5']

POPULATION_SIZE = 80
GENERATIONS = 300
MUTATION_RATE = 0.1
OUTPUT_FILENAME = 'timetable_output.html' 

 
# SUBJECTS & TEACHERS
 

SUBJECT_TEACHER = {
    'Web Technology': 'Prof. Ahmed Shaff',
    'Artificial Intelligence': 'Dr. Manzar Abbas',
    'App Development': 'Prof. Arslan Sarwar',
    'Data Science': 'Prof. Fakhar Mustafa',
    'Graph Theory': 'Prof. M. Naeem',
    'Data Structure and Algorithm': 'Prof. Imran Shehzad',
    'Data Analysis and Algorithm': 'Prof. Kamran Malik',
    'Statistics and Probability': 'Prof. Aqsa Tahseen',
    'Assembly Language': 'Prof. Usman Nasim',
    'Operating System': 'Prof. Zafar Iqbal',
    'Database Systems': 'Prof. Saqib Mehmood',
    'Computer Networks': 'Prof. Faisal Karim',
    'Software Engineering': 'Prof. Hina Yousaf',
    'Discrete Mathematics': 'Dr. Njama ',
    'Information Security': 'Prof. Danish Ali'
}

SUBJECTS = list(SUBJECT_TEACHER.keys())


# SECTIONS


SECTIONS = [
    'SP23-BCS-A', 'SP23-BCS-B',
    'FA23-BCS-A', 'FA23-BCS-B',
    'SP24-BCS-A', 'SP24-BCS-B',
    'FA24-BCS-A', 'FA24-BCS-B'
]


# STUDENTS 


def generate_students():
    students = []
    roll = 1
    for _ in range(8):
        sec = []
        for _ in range(25):
            sec.append(f"STD-{roll:03d}")
            roll += 1
        students.append(sec)
    return students


# CLASSES 


def generate_classes(students):
    classes = []
    for i, sec_students in enumerate(students):
        chosen_subjects = random.sample(SUBJECTS, 5)
        for subject in chosen_subjects:
            for _ in range(2):
                classes.append({
                    'section': SECTIONS[i],
                    'subject': subject,
                    'teacher': SUBJECT_TEACHER[subject],
                    'students': sec_students
                })
    return classes


# GENETIC REPRESENTATION 


def random_gene(cls):
    return {
        'section': cls['section'],
        'subject': cls['subject'],
        'teacher': cls['teacher'],
        'students': cls['students'],
        'day': random.choice(DAYS),
        'slot': random.choice(SLOTS),
        'room': random.choice(ROOMS)
    }

def create_chromosome(classes):
    return [random_gene(c) for c in classes]


# FITNESS FUNCTION 


def fitness(chromosome):
    penalty = 0
    teacher_busy = set()
    room_busy = set()
    section_busy = set()
    subject_day = set()
    section_days = defaultdict(set)

    for g in chromosome:
        t = (g['teacher'], g['day'], g['slot'])
        r = (g['room'], g['day'], g['slot'])
        s = (g['section'], g['day'], g['slot'])
        sd = (g['section'], g['subject'], g['day'])

        if t in teacher_busy: penalty += 100 # Teacher conflict
        if r in room_busy: penalty += 100    # Room conflict
        if s in section_busy: penalty += 100  # Section conflict
        if sd in subject_day: penalty += 300 # Subject taught more than once a day
        
        teacher_busy.add(t)
        room_busy.add(r)
        section_busy.add(s)
        subject_day.add(sd)
        section_days[g['section']].add(g['day'])

    for sec in SECTIONS:
        # Check if a section has classes on all 5 days
        if len(section_days[sec]) < 5:
            penalty += 500

    return 10000 - penalty


# GA OPERATORS  


def selection(pop):
    a, b = random.sample(pop, 2)
    return a if fitness(a) > fitness(b) else b

def crossover(p1, p2):
    cut = random.randint(1, len(p1) - 1)
    # Ensure genes from p2 are deep copied to avoid mutation side effects
    return p1[:cut] + [dict(g) for g in p2[cut:]]

def mutate(chrom):
    if random.random() < MUTATION_RATE:
        g = random.choice(chrom)
        # Mutate the time/location of a randomly selected class
        g['day'] = random.choice(DAYS)
        g['slot'] = random.choice(SLOTS)
        g['room'] = random.choice(ROOMS)
    return chrom


# GENETIC ALGORITHM 


def genetic_algorithm(classes):
    population = [create_chromosome(classes) for _ in range(POPULATION_SIZE)]

    for gen in range(GENERATIONS):
        population.sort(key=fitness, reverse=True)
        best_fitness = fitness(population[0])

        if best_fitness >= 10000:
            print(f"Goal reached in Generation {gen+1}!")
            return population[0]

        # Keep the best 5 chromosomes
        new_pop = population[:5]
        
        # Breed the rest of the population
        while len(new_pop) < POPULATION_SIZE:
            parent1 = selection(population)
            parent2 = selection(population)
            child = mutate(crossover(parent1, parent2))
            new_pop.append(child)
        
        population = new_pop
         


    print(f"Algorithm finished after {GENERATIONS} generations. Best Fitness: {fitness(population[0])}")
    return population[0]


# DISPLAY (NEW HTML FORMAT)


def display_timetable_html(timetable, filename=OUTPUT_FILENAME):
    """Generates an HTML file displaying the timetable."""
    data = defaultdict(lambda: defaultdict(dict))
    for g in timetable:
        data[g['section']][g['day']][g['slot']] = g

    # --- 1. HTML Start and Styles ---
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Timetable - All Sections</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; padding: 20px; }}
        .section-container {{ margin-bottom: 40px; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        h2 {{ color: #0056b3; border-bottom: 3px solid #0056b3; padding-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; text-transform: uppercase; }}
        .day-header {{ background-color: #f0ad4e !important; color: white; font-weight: bold; text-align: center; }}
        .empty-slot {{ background-color: #f9f9f9; color: #aaa; font-style: italic; }}
        .subject-DSA {{ background-color: #e6f7ff; border-left: 5px solid #007bff; }}
        .subject-Math {{ background-color: #fff0e6; border-left: 5px solid #ff9900; }}
        .subject-IT {{ background-color: #e6ffe6; border-left: 5px solid #28a745; }}
    </style>
</head>
<body>
    <h1>Best Feasible Timetable Generated by Genetic Algorithm</h1>
"""
    # --- 2. Generate Content for Each Section ---
    for section in SECTIONS:
        html_content += f"""
    <div class="section-container">
        <h2>Section: {section}</h2>
        <table>
            <tr>
                <th>Day/Time</th>
"""
        # Add Time Slots as column headers
        for slot in SLOTS:
            html_content += f"<th>{slot}</th>"
        html_content += "</tr>"

        # Add rows for each Day
        for day in DAYS:
            html_content += f"<tr><td class='day-header'>{day}</td>"
            for slot in SLOTS:
                
                # Check if a class is scheduled
                if slot in data[section][day]:
                    g = data[section][day][slot]
                    
                    # Determine a class for coloring (Optional but helpful)
                    class_name = "subject-IT"
                    if "Data Structure" in g['subject'] or "Algorithm" in g['subject']:
                        class_name = "subject-DSA"
                    elif "Mathematics" in g['subject'] or "Statistics" in g['subject'] or "Graph Theory" in g['subject']:
                        class_name = "subject-Math"

                    # Add the class details cell
                    html_content += f"""
                        <td class='{class_name}'>
                            <strong>{g['subject']}</strong><br>
                            <small>{g['teacher']} ({g['room']})</small>
                        </td>
                    """
                else:
                    # Add an empty slot
                    html_content += "<td class='empty-slot'>- FREE -</td>"
            
            html_content += "</tr>" # End of the day row
        
        html_content += "</table></div>" # End of table and container

    #  Write to File 
    html_content += "\n</body>\n</html>"
    
    with open(filename, 'w') as f:
        f.write(html_content)
        
    print(f"\nTimetable successfully saved to: {os.path.abspath(filename)}")
    print("Open this file in your web browser to view the schedule.")


students = generate_students()
classes = generate_classes(students)

best = genetic_algorithm(classes)

display_timetable_html(best)