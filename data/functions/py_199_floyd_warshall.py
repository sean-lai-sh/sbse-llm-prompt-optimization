from typing import List, Optional


def floyd_warshall(
    num_nodes: int,
    edges: List[tuple],
) -> Optional[List[List[float]]]:
    INF = float('inf')
    dist = [[INF] * num_nodes for _ in range(num_nodes)]

    for i in range(num_nodes):
        dist[i][i] = 0

    for edge in edges:
        u, v, w = edge[0], edge[1], edge[2]
        if w < dist[u][v]:
            dist[u][v] = w
        if w < dist[v][u]:
            dist[v][u] = w

    for k in range(num_nodes):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    for i in range(num_nodes):
        if dist[i][i] < 0:
            return None

    return dist
