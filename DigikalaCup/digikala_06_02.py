# Python program for implementation of Ford Fulkerson algorithm 
# reference: https://www.geeksforgeeks.org/ford-fulkerson-algorithm-for-maximum-flow-problem/

from collections import defaultdict
import sys 

class Graph: 

	def __init__(self,graph): 
		self.graph = graph # residual graph 
		self. ROW = len(graph) 
		#self.COL = len(gr[0]) 
		

	'''Returns true if there is a path from source 's' to sink 't' in 
	residual graph. Also fills parent[] to store the path '''
	def BFS(self,s, t, parent): 

		# Mark all the vertices as not visited 
		visited =[False]*(self.ROW) 
		
		# Create a queue for BFS 
		queue=[] 
		
		# Mark the source node as visited and enqueue it 
		queue.append(s) 
		visited[s] = True
		
		# Standard BFS Loop 
		while queue: 

			#Dequeue a vertex from queue and print it 
			u = queue.pop(0) 
		
			# Get all adjacent vertices of the dequeued vertex u 
			# If a adjacent has not been visited, then mark it 
			# visited and enqueue it 
			for ind, v in enumerate(self.graph[u]): 
				if visited[v] == False and self.graph[u][v] > 0 : 
					queue.append(v) 
					visited[v] = True
					parent[v] = u 

		# If we reached sink in BFS starting from source, then return 
		# true, else false 
		return True if visited[t] else False
			
	
	# Returns tne maximum flow from s to t in the given graph 
	def FordFulkerson(self, source, sink): 

		# This array is filled by BFS and to store path 
		parent = [-1]*(self.ROW) 

		max_flow = 0 # There is no flow initially 

		# Augment the flow while there is path from source to sink 
		while self.BFS(source, sink, parent) : 

			# Find minimum residual capacity of the edges along the 
			# path filled by BFS. Or we can say find the maximum flow 
			# through the path found. 
			path_flow = float("Inf") 
			s = sink 
			while(s != source): 
				path_flow = min (path_flow, self.graph[parent[s]][s]) 
				s = parent[s] 

			# Add path flow to overall flow 
			max_flow += path_flow 

			# update residual capacities of the edges and reverse edges 
			# along the path 
			v = sink 
			while(v != source): 
				u = parent[v] 
				self.graph[u][v] -= path_flow 
				if u not in self.graph[v]:
					self.graph[v][u] = 0
				self.graph[v][u] += path_flow 
				v = parent[v] 

		return max_flow 

if __name__ == "__main__":

	n = int(input())
	nodes_type = list(map(int, input().split()))
	e = int(input())
		
	graph = [dict() for _ in range(n+2)]

	for i in range(e):
		start, end, capacity = list(map(int, input().split()))
		
		graph[start][end] = capacity
		if nodes_type[start-1] == 1: # source node
			if start not in graph[0]:
				graph[0][start] = 0
			graph[0][start] += capacity

		if nodes_type[end-1] == 2: # sink node
			if n+1 not in graph[end]:
				graph[end][n+1] = 0
			graph[end][n+1] += capacity

	g = Graph(graph) 

	# compute max flow
	source = 0
	sink = n+1

	print(g.FordFulkerson(source, sink))