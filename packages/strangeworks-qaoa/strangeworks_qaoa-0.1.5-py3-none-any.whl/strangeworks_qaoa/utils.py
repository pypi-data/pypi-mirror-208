import copy
import random
from itertools import combinations, groupby

import dimod
import networkx as nx
import numpy as np
import qiskit
import scipy.sparse.linalg as sla
from qiskit.opflow import I, Z


def get_graph(nodes, seedin):
    """
    Generate networkX graph where each node is connected to all other nodes.
    The weights of the connections are random and uniformly distributed between -1 to 1
    """
    random.seed(seedin)

    G = nx.Graph()
    for nn in range(0, nodes):
        G.add_nodes_from([(nn, {"weight": 0})])
        # G.add_nodes_from([(nn)])

    edges = combinations(range(nodes), 2)
    for _, node_edges in groupby(edges, key=lambda x: x[0]):
        for e in node_edges:
            G.add_edges_from([(e[0], e[1], {"weight": random.uniform(-1, 1)})])

    return G


def get_nReg_MaxCut_graph(n, nodes, seedin):
    """
    Generate networkX graph where each node has n connections to a random slection of
    the other nodes.
    The weights of the connections are random and uniformly distributed between -1 to 1
    """
    random.seed(seedin)

    G = nx.Graph()
    for nn in range(0, nodes):
        G.add_nodes_from([(nn)])

    F = nx.random_regular_graph(n, nodes)
    for e in F.edges:
        G.add_edges_from([(e[0], e[1], {"weight": random.uniform(-1, 1)})])

    return G


def get_rand_QUBO(nodes, seedin):
    """
    Generate random QUBO matrix
    The weights of the connections are random and uniformly distributed between -1 to 1
    """
    random.seed(seedin)

    QUBO = np.zeros((nodes, nodes), dtype=float)
    for n in range(nodes):
        QUBO[n][n] = random.uniform(-1, 1)
        for m in range(n + 1, nodes):
            QUBO[n][m] = random.uniform(-1, 1)

    return QUBO


def get_nReg_MaxCut_QUBO(n, nodes, seedin):
    """
    Generate QUBO matrix where each node has n connections to a random slection of
    the other nodes.
    The weights of the connections are random and uniformly distributed between -1 to 1
    """

    G = get_nReg_MaxCut_graph(n, nodes, seedin)

    return get_QUBO(G)


def get_rand_PauliSumOp(nodes, seedin):
    """
    Generate random PauliSumOp
    The weights of the connections are random and uniformly distributed between -1 to 1
    """

    G = get_graph(nodes, seedin)

    return get_PauliSumOp(G)


def get_nReg_MaxCut_PauliSumOp(n, nodes, seedin):
    """
    Generate PauliSumOp where each node has n connections to a random slection of
    the other nodes.
    The weights of the connections are random and uniformly distributed between -1 to 1
    """

    G = get_nReg_MaxCut_graph(n, nodes, seedin)

    return get_PauliSumOp(G)


def get_PauliSumOp(G):

    Ham = None

    for nn in list(G.nodes()):
        try:
            G.nodes[nn]["weight"]
        except Exception:
            # if not specified, node weights will be considered zero
            G.nodes[nn]["weight"] = 0

        if G.nodes[nn]["weight"] != 0:

            if nn == 0:
                temp = Z
            else:
                temp = I

            for pp in range(0, nn - 1):
                temp = temp ^ I

            if nn != 0:
                temp = temp ^ Z

            for pp in range(nn, len(G.nodes()) - 1):
                temp = temp ^ I

            if Ham is None:
                Ham = G.nodes[nn]["weight"] * temp
            else:
                Ham = Ham + G.nodes[nn]["weight"] * temp

    for pair in list(G.edges()):
        try:
            G.edges[pair]["weight"]
        except Exception:
            # if not specified, edge weight will be set equal to 1.0
            G.edges[pair]["weight"] = 1.0

        if pair[0] == 0:
            temp = Z
        else:
            temp = I

        for pp in range(0, pair[0] - 1):
            temp = temp ^ I

        if pair[0] != 0:
            temp = temp ^ Z

        for pp in range(pair[0], pair[1] - 1):
            temp = temp ^ I

        temp = temp ^ Z

        for pp in range(pair[1], len(G.nodes()) - 1):
            temp = temp ^ I

        if Ham is None:
            Ham = G.edges[pair]["weight"] * temp
        else:
            Ham = Ham + G.edges[pair]["weight"] * temp

    return Ham


def get_QUBO(G):

    nodes = len(G.nodes)
    Ising_Mat = np.zeros((nodes, nodes), dtype=float)

    for nn in list(G.nodes()):
        try:
            G.nodes[nn]["weight"]
        except Exception:
            # if not specified, node weights will be considered zero
            G.nodes[nn]["weight"] = 0

        Ising_Mat[nn][nn] = G.nodes[nn]["weight"]

    for pair in list(G.edges()):
        try:
            G.edges[pair]["weight"]
        except Exception:
            # if not specified, edge weight will be set equal to 1.0
            G.edges[pair]["weight"] = 1.0

        Ising_Mat[pair[0]][pair[1]] = G.edges[pair]["weight"]

    return Ising_Mat


def get_Ising(G):

    Q = get_QUBO(G)
    Ising_mat = convert_QUBO_to_Ising(Q)

    return Ising_mat


def get_Ham_from_graph(G):

    Ham = []
    for nn in list(G.nodes()):
        try:
            G.nodes[nn]["weight"]
        except Exception:
            # if not specified, node weights will be considered zero
            G.nodes[nn]["weight"] = 0

        if G.nodes[nn]["weight"] != 0:
            Ham.append((G.nodes[nn]["weight"], nn))

    for pair in list(G.edges()):
        try:
            G.edges[pair]["weight"]
        except Exception:
            # if not specified, edge weight will be set equal to 1.0
            G.edges[pair]["weight"] = 1.0
        Ham.append((G.edges[pair]["weight"], pair))

    return Ham


def get_Ham_from_PauliSumOp(H_pauliSum):

    Ham = []
    for nn in range(len(H_pauliSum._primitive)):

        op_str = str(H_pauliSum._primitive[nn]._pauli_list[0])

        pair = []
        for ll in range(len(op_str)):
            if op_str[ll] == "Z":
                pair.append(ll)

        if len(pair) > 1:
            pair = tuple(pair)
        else:
            pair = pair[0]

        Ham.append((np.real(H_pauliSum._primitive[nn]._coeffs[0]), pair))

    return Ham


def get_Ham_from_QUBO(QUBO_mat):

    nodes = np.size(QUBO_mat[0])

    Ham = []
    for nn in range(nodes):
        if QUBO_mat[nn][nn] != 0:
            Ham.append((QUBO_mat[nn][nn], nn))

    for p1 in range(nodes):
        for p2 in range(p1 + 1, nodes):
            if np.abs(QUBO_mat[p1][p2]) > 1e-5:
                pair = tuple([p1, p2])
                Ham.append((QUBO_mat[p1][p2], pair))

    return Ham


def convert_QUBO_to_Ising(QUBO_mat):

    nodes = np.size(QUBO_mat[0])
    Ising_mat = QUBO_mat / 4

    for nn in range(nodes):
        Ising_mat[nn][nn] = QUBO_mat[nn][nn] / 2 + sum(
            QUBO_mat[nn][nn + 1 :] / 4
        )  # noqa E501

    for nn in range(nodes):
        Ising_mat[nn][nn] += sum(QUBO_mat[:nn, nn] / 4)

    return Ising_mat


def get_graph_from_Ham(H, nqubits):
    G = nx.Graph()
    list_nodes = []
    for nn in range(nqubits):
        list_nodes.append(nn)
    G.add_nodes_from(list_nodes)

    for nn in range(len(H)):
        try:
            len(H[nn][1])
            check = True
        except TypeError:
            check = False

        if check is True:
            Num_z = len(H[nn][1])
            if Num_z > 2:
                print(
                    """Error: cannot create networkX graph.
                    Hamiltonian has more than pairwise connections"""
                )
            elif Num_z == 2:
                G.add_edges_from([(H[nn][1][0], H[nn][1][1], {"weight": H[nn][0]})])
        else:
            ind = H[nn][1]
            G.add_nodes_from([(ind, {"weight": H[nn][0]})])

    return G


def get_QUBO_from_Ham(H, nodes):

    Q = np.zeros((nodes, nodes), dtype=float)

    for nn in range(len(H)):
        try:
            len(H[nn][1])
            check = True
        except TypeError:
            check = False

        if check is True:
            Num_z = len(H[nn][1])
            if Num_z > 2:
                print(
                    """Error: cannot create QUBO.
                    Hamiltonian has more than pairwise connections"""
                )
            elif Num_z == 2:
                Q[H[nn][1][0]][H[nn][1][1]] = H[nn][0]
        else:
            ind = H[nn][1]
            Q[ind][ind] = H[nn][0]

    return Q


# def get_PauliSumOp_from_Ham(H):

#     Ham = None

#     for nn in range(len(H)):

#         if H[nn][1][0] == "Z":
#             temp = 2 * Z + I
#         else:
#             temp = I
#         for mm in range(1, len(H[nn][1])):
#             if H[nn][1][mm] == "Z":
#                 temp = temp ^ 2 * Z + I
#             else:
#                 temp = temp ^ I

#         if Ham is None:
#             Ham = H[nn][0] * temp
#         else:
#             Ham = Ham + H[nn][0] * temp

#     return Ham


def get_cost_bitstring(bitstring, problem, ising=False):

    if type(problem) == nx.classes.graph.Graph:
        H = get_Ham_from_graph(problem)
    elif type(problem) == qiskit.opflow.primitive_ops.pauli_sum_op.PauliSumOp:
        H = get_Ham_from_PauliSumOp(problem)
    elif type(problem) == np.ndarray:
        H = get_Ham_from_QUBO(problem)
    elif (
        type(problem) == dict
        and problem.get("BQM") is not None
        and type(problem.get("BQM"))
        == dimod.binary.binary_quadratic_model.BinaryQuadraticModel
    ):
        QUBO = problem["BQM"].to_numpy_matrix(
            variable_order=problem.get("variable_order")
        )
        H = get_Ham_from_QUBO(QUBO)

    cost = get_energy(bitstring, H, ising)

    return cost


def get_energy(x, H, ising=False):
    """Get the energy of the quantum state

    Parameters:
        x (str): bitstring of ones and zeros
        H (List): Hamiltonian which we are to find the minimum value

    Return:
        En (float): energy of the state x.
    """
    coeffs = []
    pair_list = []
    for item in H:
        coeffs.append(item[0])
        pair_list.append(item[1])

    En = 0.0
    for pair in range(len(coeffs)):
        try:
            len(pair_list[pair])
            check = True
        except TypeError:
            check = False
        if check:

            xval = []
            for nn in pair_list[pair]:
                xval.append(int(x[nn]))

            if ising is True:
                diff = np.abs(sum(xval) - len(xval))
                En += np.power(-1, diff) * coeffs[pair] / np.power(2, len(xval))
            else:
                if sum(xval) == len(xval):
                    En += coeffs[pair]

        else:
            i = pair_list[pair]
            if x[i] == "1":
                En += coeffs[pair]
            elif ising is True:
                En -= coeffs[pair]

            if ising is True:
                En = En / 2.0

    return En


def get_exact_en(G, nodes, ising=False):

    if nodes > 24:
        Egs_exact = "!!problem too big for exact solution!!"
    else:

        edges = np.zeros((len(G.edges()), 2), dtype=int)
        we = np.zeros(len(G.edges()), dtype=float)
        iter = 0
        for x in G.edges():
            edges[iter, 0] = x[0]
            edges[iter, 1] = x[1]
            we[iter] = G.edges[x]["weight"]
            iter = iter + 1

        wn = np.zeros(len(G.nodes()), dtype=float)
        iter = 0
        for i in G.nodes():
            try:
                wn[iter] = G.nodes[i]["weight"]
            except Exception:
                wn[iter] = 0
            iter = iter + 1

        def TensorProd(A):

            out = np.kron(A[0], A[1])
            for oo in range(2, len(A)):
                out = np.kron(out, A[oo])

            return out

        if ising is True:
            sz = [[1.0 / 2.0, 0.0], [0.0, -1.0 / 2.0]]
        else:
            sz = [[1.0, 0.0], [0.0, 0.0]]

        A0 = []
        for n in range(0, nodes):
            A0.append(np.eye(2))

        Ham = np.zeros((np.power(2, nodes), np.power(2, nodes)), dtype=float)
        for p in range(0, nodes):
            A = copy.deepcopy(A0)
            A[p] = sz
            Ham += wn[p] * TensorProd(A)

        for p in range(0, len(G.edges())):
            A = copy.deepcopy(A0)
            A[edges[p][0]] = sz
            A[edges[p][1]] = sz
            Ham += we[p] * TensorProd(A)

        Egs_exact, V = sla.eigs(Ham, 1, which="SR")
        Egs_exact = np.real(Egs_exact[0])

        # Egs_exact = NumPyMinimumEigensolver().compute_minimum_eigenvalue(G).eigenvalue

    return Egs_exact
