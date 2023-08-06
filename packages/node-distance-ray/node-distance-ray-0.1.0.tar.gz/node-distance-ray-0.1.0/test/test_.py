import node_distance_ray as ndr

batch_num_nodes = [[31], [24], [25], [25]]

batch_all_edges = [
    [[
        (11, 1), (3, 2), (11, 3), (11, 4), (6, 5), (4, 6), (8, 7), (11, 8),
        (10, 9), (8, 10), (29, 11), (11, 12), (15, 13), (15, 14), (8, 15),
        (15, 16), (22, 17), (20, 18), (18, 19), (22, 20), (22, 21), (24, 22),
        (22, 23), (15, 24), (26, 25), (0, 26), (26, 27), (29, 28), (26, 29),
        (26, 30)
    ]], [[
        (2, 1), (3, 2), (0, 3), (5, 4), (3, 5), (5, 6), (6, 7), (3, 8),
        (3, 9), (11, 10), (9, 11), (11, 12), (11, 13), (22, 14), (16, 15),
        (22, 16), (21, 17), (20, 18), (20, 19), (21, 20), (22, 21), (11, 22),
        (3, 23)
    ]], [[
        (2, 1), (0, 2), (2, 3), (3, 4), (14, 5), (8, 6), (8, 7), (14, 8),
        (10, 9), (14, 10), (14, 11), (13, 12), (14, 13), (3, 14), (2, 15),
        (2, 16), (16, 17), (17, 18), (20, 19), (17, 20), (23, 21), (23, 22),
        (20, 23), (2, 24)
    ]], [[
        (2, 1), (0, 2), (2, 3), (6, 4), (6, 5), (2, 6), (6, 7), (9, 8), (7, 9),
        (11, 10), (9, 11), (2, 12), (2, 13), (13, 14), (23, 15), (23, 16),
        (16, 17), (23, 18), (20, 19), (18, 20), (22, 21), (20, 22), (14, 23),
        (2, 24)
    ]]
]


def test1():
    # List[nodedist, tokendist, indicies]
    results = ndr.node_token_distances(
        batch_all_edges, batch_num_nodes, cutoff=25)
    assert len(results) == 4
    assert len(results[0]) == 3


def test2():
    # List[nodedist, tokendist, indicies]
    results = ndr.node_token_distances(
        batch_all_edges, batch_num_nodes, cutoff=25)
    assert len(results) == 4
    assert len(results[0]) == 3
    # List[xobs, pdf, freq]
    nodedist = [res[0] for res in results]
    results2 = ndr.nodedist_distribution(nodedist, xmin=1, xmax=12)
    assert len(results2) == 4
    assert len(results2[0]) == 3


def test3():
    # List[nodedist, tokendist, indicies]
    results = ndr.node_token_distances(
        batch_all_edges, batch_num_nodes, cutoff=25)
    assert len(results) == 4
    assert len(results[0]) == 3
    # List[xobs, pdf, freq]
    nodedist = [res[0] for res in results]
    tokendist = [res[1] for res in results]
    results2 = ndr.tokenvsnode_distribution(
        tokendist, nodedist, xmin=-5, xmax=15)
    assert len(results2) == 4
    assert len(results2[0]) == 3
