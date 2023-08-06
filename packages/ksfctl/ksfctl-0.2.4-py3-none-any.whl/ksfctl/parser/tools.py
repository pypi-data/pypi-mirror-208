from collections import defaultdict, deque


class Graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.visited = {}
        self.path = []

    def add_edge(self, u, v):
        if u not in self.graph:
            self.graph[u] = []
        if v not in self.graph:
            self.graph[v] = []

        if v not in self.graph[u]:
            self.graph[u].append(v)
            return True
        else:
            return False

    def add_node(self, u):
        if u not in self.graph:
            self.graph[u] = []

    def find_cycle(self):
        # 初始化所有节点的访问状态
        for node in self.graph:
            self.visited[node] = False

        # 从每个节点开始搜索，直到找到第一个环
        for node in self.graph:
            if node in self.visited and not self.visited[node]:
                self.path = []
                if self._dfs(node):
                    return self.path[::-1]  # 反转环的顺序，以使其符合正常的阅读顺序

        return None

    def _dfs(self, node):
        self.visited[node] = True
        self.path.append(node)

        # 沿着出度的路径进行搜索
        for neighbor in self.graph[node]:
            if neighbor in self.visited and not self.visited[neighbor]:
                # 如果邻接节点还没有被访问，则继续搜索
                if self._dfs(neighbor):
                    return True

            elif neighbor in self.path:
                # 如果当前节点的邻接节点已经在路径中，则说明存在环
                index = self.path.index(neighbor)
                self.path = self.path[index:]
                return True

        self.path.pop()
        return False

    def bfs(self, start, callback):
        # 标记所有节点的访问状态
        visited = {node: False for node in self.graph}

        # 创建队列，并将起点加入队列中
        queue = deque()
        queue.append(start)

        # 广度优先搜索算法
        node = None
        while queue:
            node = queue.popleft()

            # 如果当前节点还没有被访问，则将其标记为已访问，并输出
            if node in visited and not visited[node]:
                visited[node] = True
                callback(node)

                # 将所有邻接节点加入队列中
                for neighbor in self.graph.get(node, []):
                    queue.append(neighbor)

        return visited

    def get_all_prev(self, curr, with_self=True):
        """
        获取所有前向节点
        :return:
        """
        nodes = set()
        self.bfs(curr, lambda a: nodes.add(a) if with_self or a != curr else None)

        return nodes

    def bfs_dag(self, callback):
        # perform topological sorting to get linear ordering of vertices
        in_degree = {u: 0 for u in self.graph}
        for u in self.graph:
            for v in self.graph[u]:
                in_degree[v] += 1
        queue = deque([u for u in self.graph if in_degree[u] == 0])
        visited = []
        while queue:
            u = queue.popleft()
            visited.append(u)
            for v in self.graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        # perform BFS traversal in topological order
        visited_nodes = set()
        bfs_queue = deque(visited)
        visited_nodes.update(visited)
        while bfs_queue:
            current_node = bfs_queue.popleft()
            callback(current_node)
            for neighbor in self.graph[current_node]:
                if neighbor not in visited_nodes:
                    bfs_queue.append(neighbor)
                    visited_nodes.add(neighbor)

    def has_node(self, node):
        return node in self.graph


def run_once(func):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)
    wrapper.has_run = False
    return wrapper
