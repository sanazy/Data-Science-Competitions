//Name: Hy Truong Son
//School: Informatics, ELTE
//Date: Saturday, 2nd November, 2013

#include <iostream>
#include <cstring>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <set>
#include <map>
#include <queue>
#include <iterator>
#include <algorithm>

#define MaxN 1002
#define INF 1000000000

using namespace std;

int n, m, s, t, TotalFlow;
int c[MaxN][MaxN];
int f[MaxN][MaxN];
int trace[MaxN];
int node_type[MaxN];

void input(){
	int i, u, v, w;
	cin >> n;
	s = n+1;
	t = n+2;
	for (i = 0; i < n; ++i){
		cin >> node_type[i];
	}
	cin >> m;
	memset(c, 0, sizeof(c));
	for (i = 1; i <= m; i++){
		cin >> u >> v >> w;
		c[u][v] = w;
		//c[v][u] = w;

		if (node_type[u-1] == 1){
			c[n+1][u] += w;
			//c[u][n+1] += w;
		}
		if (node_type[v-1] == 2){
			c[v][n+2] += w;
			//c[n+2][v] += w;
		}
	}
	
}

void BFS(){
	int i, j;
	queue<int> q;
	memset(trace, 0, sizeof(trace));
	q.push(s);
	trace[s] = -1;
	while (!q.empty()){
		i = q.front();
		q.pop();
		for (j = 1; j <= n+2; j++)
			if ((trace[j] == 0) && (c[i][j] > f[i][j])){
				q.push(j);
				trace[j] = i;
				if (j == t) return;
			}
	}
}

void IncFlow(){
	int u, v, delta;
	delta = INF;
	v = t;
	while (v != s){
		u = trace[v];
		delta = min(delta, c[u][v] - f[u][v]);
		v = u;
	}
	v = t;
	while (v != s){
		u = trace[v];
		f[u][v] += delta;
		f[v][u] -= delta;
		v = u;
	}
	TotalFlow += delta;
}

void Ford_Fulkerson_Edmond_Karp(){
	memset(f, 0, sizeof(f));
	TotalFlow = 0;
	while (true){
		BFS();
		if (trace[t] == 0) break;
		IncFlow();
	}
	cout << TotalFlow << endl;
}

int main(){
	input();
	Ford_Fulkerson_Edmond_Karp();
}