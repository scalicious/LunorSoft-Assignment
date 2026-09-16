# C++ Reference Guide for Engineering Students

## Core C++ Concepts

### STL (Standard Template Library)
The STL provides ready-made data structures and algorithms - knowing these is essential for competitive programming and interviews.

**Vectors (Dynamic Arrays)**
```cpp
#include <vector>
vector<int> v = {1, 2, 3};
v.push_back(4);       // Add to end: O(1) amortized
v.pop_back();         // Remove from end: O(1)
v.size();             // Number of elements
v[i];                 // Access by index: O(1)
sort(v.begin(), v.end()); // Sort: O(N log N)
```

**Maps and Unordered Maps**
```cpp
#include <map>
#include <unordered_map>
map<string, int> m;       // Ordered, O(log N) operations
unordered_map<string, int> um; // Hash-based, O(1) average
um["key"] = 42;
um.count("key");          // 1 if exists, 0 if not
```

**Sets**
```cpp
#include <set>
set<int> s = {3, 1, 4, 1, 5}; // Stores {1, 3, 4, 5} - no duplicates, sorted
s.insert(6);
s.find(3) != s.end(); // true if 3 exists
```

**Priority Queue (Heap)**
```cpp
#include <queue>
priority_queue<int> maxHeap;       // Max-heap by default
priority_queue<int, vector<int>, greater<int>> minHeap; // Min-heap
maxHeap.push(5);
maxHeap.top();   // Peek: O(1)
maxHeap.pop();   // Remove top: O(log N)
```

**Stack and Queue**
```cpp
stack<int> stk;
stk.push(1); stk.top(); stk.pop();

queue<int> q;
q.push(1); q.front(); q.pop();
```

---

## Key Algorithms in C++

### Sorting
```cpp
sort(arr.begin(), arr.end());                     // Ascending
sort(arr.begin(), arr.end(), greater<int>());      // Descending
sort(arr.begin(), arr.end(), [](int a, int b) {   // Custom
    return a % 2 < b % 2;  // odd numbers last
});
```

### Binary Search
```cpp
#include <algorithm>
// Array must be sorted first!
bool found = binary_search(v.begin(), v.end(), 7);

// Lower bound: first element >= target
auto it = lower_bound(v.begin(), v.end(), 7);
int idx = it - v.begin(); // Convert iterator to index

// Upper bound: first element > target
auto it2 = upper_bound(v.begin(), v.end(), 7);
```

### Two Pointers Pattern
```cpp
// Find pair with target sum in sorted array
int left = 0, right = arr.size() - 1;
while (left < right) {
    int sum = arr[left] + arr[right];
    if (sum == target) return {left, right};
    else if (sum < target) left++;
    else right--;
}
```

### Sliding Window
```cpp
// Maximum sum of subarray of size k
int maxSum = 0, windowSum = 0;
for (int i = 0; i < k; i++) windowSum += arr[i];
maxSum = windowSum;
for (int i = k; i < n; i++) {
    windowSum += arr[i] - arr[i - k];
    maxSum = max(maxSum, windowSum);
}
```

---

## Bit Manipulation

```cpp
x & (x - 1)     // Clear lowest set bit
x & (-x)         // Isolate lowest set bit
x | (1 << i)     // Set bit i
x & ~(1 << i)    // Clear bit i
x ^ (1 << i)     // Toggle bit i
(x >> i) & 1     // Check if bit i is set
__builtin_popcount(x)  // Count set bits (GCC)
```

### Common Bit Tricks
```cpp
// Check if n is power of 2
bool isPow2 = (n > 0) && (n & (n - 1)) == 0;

// Swap without temp
a ^= b; b ^= a; a ^= b;

// Find the only non-repeating number in array (XOR trick)
int result = 0;
for (int x : arr) result ^= x;
// result is the unique number
```

---

## Dynamic Programming Patterns

### 1D DP - Climbing Stairs
```cpp
// How many ways to climb n stairs (1 or 2 steps at a time)?
int climbStairs(int n) {
    if (n <= 2) return n;
    int a = 1, b = 2;
    for (int i = 3; i <= n; i++) {
        int c = a + b;
        a = b; b = c;
    }
    return b;
}
```

### 2D DP - Longest Common Subsequence
```cpp
int lcs(string s1, string s2) {
    int m = s1.size(), n = s2.size();
    vector<vector<int>> dp(m+1, vector<int>(n+1, 0));
    for (int i = 1; i <= m; i++)
        for (int j = 1; j <= n; j++)
            dp[i][j] = (s1[i-1] == s2[j-1]) ? dp[i-1][j-1] + 1
                                              : max(dp[i-1][j], dp[i][j-1]);
    return dp[m][n];
}
```

### Knapsack Pattern
```cpp
// 0/1 Knapsack: max value with weight capacity W
int knapsack(vector<int>& wt, vector<int>& val, int W) {
    int n = wt.size();
    vector<int> dp(W+1, 0);
    for (int i = 0; i < n; i++)
        for (int j = W; j >= wt[i]; j--)  // Reverse order for 0/1
            dp[j] = max(dp[j], dp[j - wt[i]] + val[i]);
    return dp[W];
}
```

---

## Graph Algorithms

### BFS (Breadth-First Search)
```cpp
// Shortest path in unweighted graph
void bfs(vector<vector<int>>& graph, int start) {
    vector<bool> visited(graph.size(), false);
    queue<int> q;
    q.push(start);
    visited[start] = true;
    while (!q.empty()) {
        int node = q.front(); q.pop();
        for (int neighbor : graph[node]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                q.push(neighbor);
            }
        }
    }
}
```

### DFS (Depth-First Search)
```cpp
void dfs(vector<vector<int>>& graph, int node, vector<bool>& visited) {
    visited[node] = true;
    for (int neighbor : graph[node])
        if (!visited[neighbor])
            dfs(graph, neighbor, visited);
}
```

### Dijkstra's Algorithm (Shortest Path)
```cpp
#include <queue>
vector<int> dijkstra(vector<vector<pair<int,int>>>& graph, int src) {
    int n = graph.size();
    vector<int> dist(n, INT_MAX);
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;
    dist[src] = 0;
    pq.push({0, src});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto [w, v] : graph[u])
            if (dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
    }
    return dist;
}
```

---

## Complexity Cheat Sheet

| Operation             | Array  | Linked List | BST      | Hash Map |
|-----------------------|--------|-------------|----------|----------|
| Access by index       | O(1)   | O(N)        | O(log N) | O(1)     |
| Search                | O(N)   | O(N)        | O(log N) | O(1)     |
| Insert (end)          | O(1)   | O(1)        | O(log N) | O(1)     |
| Insert (arbitrary)    | O(N)   | O(1)        | O(log N) | O(1)     |
| Delete                | O(N)   | O(1)        | O(log N) | O(1)     |
