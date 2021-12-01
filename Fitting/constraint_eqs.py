"""
This script generates equations for CalculiX.
The intention is to create MPC (Multiple Point constraints) as in the 
example on page 337 of Practical Finite Element Analysis for Mechanical Engineers.

I'm using the following setup for creating this problem:

- Mesh a model using Cubit (freeware up to 50K elements)
- Setup the FEM with PreProMax (open source)
- Define the MPC using *EQUATION from Calculix (see point 6.7.2 in http://www.dhondt.de/ccx_2.18.pdf)
  -> A Python script generates .txt files with the equations for each node, 
  having extracted the node numbers out of the .inp CalculiX file exported with PreProMax.
"""

from collections import namedtuple

Point = namedtuple('Point', ['x', 'y', 'z'])


def MPC(nodes, base_nodes, movable_nodes):
    """
    These must be defined before the first *STEP in the Calculix .inp file
    
    *EQUATION
    - Number of terms in the equation
    - Node number of the first variable.
    - Degree of freedom at above node for the first variable.
    - Value of the coefficient of the first variable.
    """
    
    equations = []
    for node_id, base_node_id, mv_node_id in zip(nodes, base_nodes, movable_nodes):
        
        eq = (
            f"** MY EQUATIONS\n*EQUATION\n"
            f"3\n"
            f"{node_id}, {3}, -1, {base_node_id}, {3}, 1, {mv_node_id}, {3}, 1\n")
        
        equations.append(eq)
    
    return "".join(equations)


def get_nodes_map(calculix_filename):
    """
    Load CalculiX .inp file to parse its nodes and return
    something like: {'5462': Point(), ...}
    """

    nodes_map = {}
    found = False
    with open(calculix_filename, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if found:
                if "**" in line:
                    break
                else:
                    node_id, x, y, z = line.split(', ')
                    nodes_map[node_id] = Point(x=float(x), y=float(y), z=float(z))
            else:
                if "*Node" in line:
                    found = True
                    print("Found where the nodes are")
                else:
                    continue

    return nodes_map


def gen_nodes(first_node_id, query_nodes, calculix_filename="Fitting_fea.inp"):
    """
    Create new nodes (with id starting at `first_node_id`) positioned in
    the same place of the query nodes.
    """

    nodes_map = get_nodes_map(calculix_filename)
    
    s = "** MY NODES\n*Node\n"
    dummy_nodes = []                
    
    for i,node_id in enumerate(query_nodes):
        x,y,z = nodes_map[str(node_id)]
        dummy_nodes.append(first_node_id+i)
        s += f"{first_node_id+i}, {x}, {y}, {z}\n"

    return s, dummy_nodes


def constrain_dofs(nodes):
    """
    These must be defined inside a *STEP
    """

    s = "** MY BOUNDARIES\n*BOUNDARY\n"
    for node_id in nodes:
        s += f"{node_id}, 1, 2\n"
    return s


def fix_base(nodes):
    s = "** Name: MY BOUNDARIES\n*BOUNDARY\n"
    for node_id in nodes:
        s += f"{node_id}, 1, 3, 0\n" # constrain x, y, z
    return s


# The follwing list of nodes was extracted from an exported CalculiX file based on a Node Set
nodes = [
70, 71, 74, 75, 80, 81, 84, 85, 448, 452, 453, 454, 455, 456, 457, 458, 
459, 460, 461, 474, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 615, 616, 
617, 618, 619, 620, 621, 622, 623, 624, 637, 638, 639, 640, 641, 642, 643, 644, 
645, 646, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 
662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 2586, 2587, 2588, 2589, 
2590, 2591, 2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599, 2600, 2601, 2602, 2603, 2604, 2605, 
2606, 2607, 2608, 2609, 2610, 2611, 2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2621, 
2622, 2623, 2624, 2625, 2626, 2627, 2628, 2629, 2630, 2631, 2632, 2633, 2634, 2635, 2636, 2637, 
2638, 2639, 2640, 2641, 2642, 2643, 2644, 2645, 2646, 2647, 2648, 2649, 2650, 2651, 2652, 2653, 
2654, 2655, 2656, 2657, 2658, 2659, 2660, 2661, 2662, 2663, 2664, 2665, 2666, 2667, 2668, 2669, 
2670, 2671, 2672, 2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681, 2682, 2683, 2684, 2685, 
2686, 2687, 2688, 2689, 2690, 2691, 2692, 2693, 2694, 2695, 2696, 2697, 2698, 2699, 2700, 2701, 
2702, 2703, 2704, 2705, 2706, 2707, 2708, 2709, 2710, 2711, 2712, 2713, 2714
]

with open("nodes.txt", "w") as f:
    s, dummy_base_nodes = gen_nodes(first_node_id=5487, query_nodes=nodes)
    f.write(s)

    s, dummy_movable_nodes = gen_nodes(first_node_id=5487+len(dummy_base_nodes), query_nodes=nodes)
    f.write(s)

with open("boundaries.txt", "w") as f:
    s = fix_base(dummy_base_nodes)
    f.write(s)

    s = constrain_dofs(dummy_movable_nodes)
    f.write(s)

with open("equations.txt", "w") as f:
    s = MPC(nodes, dummy_base_nodes, dummy_movable_nodes)
    f.write(s)

    