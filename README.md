# Langton
Langton's Ant, a simple cellular automaton in Python

The preamble to the script (before the main loops) can be edited to affect the cellular automaton's rules and display properties. Adding command line options is planned.

The Langton’s ant program can use any arbitrary rule set in the form of a string like ‘rllr’ which determines the ant’s turning directive as a function of the present board state. In addition to performing the rules on a flat 2D grid with edges where the CA will stop if the ant falls of an edge, the program can also use a torus or Klein bottle topology. Making gifs is also supported, but rendering them takes a very long time. 

The ant on a Klein bottle is an interesting case. A Klein bottle has a torus boundary condition joining two opposing edges and Möbius boundary conditions joining the remaining two, in which there is a ‘twist’ in the boundary that maps the top of the world to the bottom. I’d love to investigate the effect of topological closure on ant patterns further; it seems that that area is not well-studied. For example, the ant’s behavior at the boundary in the ‘rl’ rule populates the entire Klein bottle boundary region when it is discovered.

I used this program for my Recurse center interview; the pair programming exercise consisted of adding animation to the program from a less-finished state.
