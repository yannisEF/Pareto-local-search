# Pareto local search

## Introduction

Given a set of objects with different weights, we seek the best way to fill our backpack. However, the given objects hold multi-dimensional score values, hence some solutions are not mutually dominated.

Therefore, given a user (a decision maker), we aim to propose him with the best solution according to his own preferences and score aggregator (unknown to us). In other words, we search for the optimal solution of a given user.

In this project, we implement two main methods :
* A two step resolution process: finding an approximation of the set of non dominated solutions; querying the user to get an idea of his preferences
* A one step resolution process: mixing incremental elicitation and the resolution process

## Files

Each file contains a main bloc which presents a usage example of the defined class.

### Folders

The *Data* folder holds a set of problems, all of which are defined in a .dat file containing the weights and values of the objects. It is also possible to provide a .eff file which contains the problem's true set of non dominated solutions.

The *Results* folder holds our experimental results. *Images* contains saves of obtained graphs, *Pareto* holds saved sets of non dominated solutions.

The *Utils* folder contains utilitarian functions used throughout the project.

### Elicitation and Decision maker

The *elicitor.py* file holds the definition of a decision maker and of the elicititation process. Useable agregation functions are defined in *agregation_functions.py*.

### Pareto-local-search

Files with the *pls* prefix hold various degrees of sophistication for our solving methods. The class hierarchy is the following:

```bash
├── pls1
│   ├── pls2
│   ├── pls3
│   │   ├── pls_quadtree
│   │   ├── pls_ndtree
│   │   ├── pls_elicitation
│   │   └── pls_elicitation_quadtree
└── └── pls4 (not working)
```

Files with the *struct* prefix contain data structures for Quad Trees and NDTrees.

### Main files

The *main* prefixed files allow you to reproduce our results, editable parameters are defined at the beginning of each file.