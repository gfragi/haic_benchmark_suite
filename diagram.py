from graphviz import Digraph

# Use Case Diagram
use_case = Digraph('UseCase', filename='use_case_diagram', format='png')
use_case.attr(rankdir='LR', size='8,5')

# Actors
use_case.node('User', shape='actor')
use_case.node('HAICPlatform', shape='component')

# Use Cases
use_case.node('DefineTask', label='Define Task')
use_case.node('DefineProfile', label='Define Human Profile')
use_case.node('RunSimulation', label='Run Simulation')
use_case.node('ComputeMetrics', label='Compute HAIC Metrics')
use_case.node('VisualizeResults', label='Visualize Results')

# Relationships
use_case.edges([
    ('User', 'DefineTask'),
    ('User', 'DefineProfile'),
    ('User', 'RunSimulation'),
    ('RunSimulation', 'ComputeMetrics'),
    ('RunSimulation', 'VisualizeResults')
])

# Component Diagram
component = Digraph('Component', filename='component_diagram', format='png')
component.attr(rankdir='TB', size='8,6')

# Components
component.node('API', label='FastAPI Backend', shape='component')
component.node('Task', label='Task Module', shape='component')
component.node('Profile', label='Profile Module', shape='component')
component.node('Simulation', label='Simulation Engine', shape='component')
component.node('Metrics', label='Metrics Calculator', shape='component')
component.node('Frontend', label='Vue.js Frontend', shape='component')

# Relationships
component.edges([
    ('API', 'Task'),
    ('API', 'Profile'),
    ('API', 'Simulation'),
    ('API', 'Metrics'),
    ('API', 'Frontend'),
    ('Simulation', 'Metrics')
])

use_case.render(directory='./assets/', cleanup=True)
component.render(directory='./assets/', cleanup=True)

('use_case_diagram.png', 'component_diagram.png')


