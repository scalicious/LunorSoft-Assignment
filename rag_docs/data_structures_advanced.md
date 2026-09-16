# Advanced Data Structures for Engineering Students

## Segment Tree

A **Segment Tree** is a binary tree used to efficiently answer **range queries** (sum, min, max) and support **point or range updates** in O(log N) time.

### When to Use
- Range sum / min / max queries with updates
- Problems like "sum of elements from index L to R after K updates"

### Implementation (Range Sum)
```cpp
#include <vector>
using namespace std;

class SegmentTree {
    int n;
    vector<int> tree;

public:
    SegmentTree(vector<int>& arr) {
        n = arr.size();
        tree.resize(4 * n);
        build(arr, 0, 0, n - 1);
    }

    void build(vector<int>& arr, int node, int start, int end) {
        if (start == end) {
            tree[node] = arr[start];
        } else {
            int mid = (start + end) / 2;
            build(arr, 2*node+1, start, mid);
            build(arr, 2*node+2, mid+1, end);
            tree[node] = tree[2*node+1] + tree[2*node+2];
        }
    }

    void update(int node, int start, int end, int idx, int val) {
        if (start == end) {
            tree[node] = val;
        } else {
            int mid = (start + end) / 2;
            if (idx <= mid) update(2*node+1, start, mid, idx, val);
            else            update(2*node+2, mid+1, end, idx, val);
            tree[node] = tree[2*node+1] + tree[2*node+2];
        }
    }

    int query(int node, int start, int end, int l, int r) {
        if (r < start || end < l) return 0;          // Out of range
        if (l <= start && end <= r) return tree[node]; // Fully in range
        int mid = (start + end) / 2;
        return query(2*node+1, start, mid, l, r)
             + query(2*node+2, mid+1, end, l, r);
    }

    void update(int idx, int val) { update(0, 0, n-1, idx, val); }
    int query(int l, int r)       { return query(0, 0, n-1, l, r); }
};
```

> **Complexity:** Build: O(N), Query: O(log N), Update: O(log N). Space: O(N).

---

## Fenwick Tree (Binary Indexed Tree)

A simpler alternative to Segment Trees for **prefix sum queries** and **point updates** only. More memory-efficient.

```cpp
class FenwickTree {
    int n;
    vector<int> tree;

public:
    FenwickTree(int n) : n(n), tree(n + 1, 0) {}

    void update(int i, int delta) {  // 1-indexed
        for (; i <= n; i += i & (-i))  // i & (-i): lowest set bit
            tree[i] += delta;
    }

    int prefix_sum(int i) {           // Sum [1..i]
        int sum = 0;
        for (; i > 0; i -= i & (-i))
            sum += tree[i];
        return sum;
    }

    int range_sum(int l, int r) {     // Sum [l..r]
        return prefix_sum(r) - prefix_sum(l - 1);
    }
};
```

> **Complexity:** Update: O(log N), Query: O(log N). Space: O(N).

---

## Trie (Prefix Tree)

Efficient data structure for **string prefix search**, autocomplete, and word dictionaries.

```cpp
struct TrieNode {
    TrieNode* children[26] = {};
    bool is_end = false;
};

class Trie {
    TrieNode* root;

public:
    Trie() { root = new TrieNode(); }

    void insert(const string& word) {
        TrieNode* cur = root;
        for (char c : word) {
            int idx = c - 'a';
            if (!cur->children[idx])
                cur->children[idx] = new TrieNode();
            cur = cur->children[idx];
        }
        cur->is_end = true;
    }

    bool search(const string& word) {
        TrieNode* cur = root;
        for (char c : word) {
            int idx = c - 'a';
            if (!cur->children[idx]) return false;
            cur = cur->children[idx];
        }
        return cur->is_end;
    }

    bool startsWith(const string& prefix) {
        TrieNode* cur = root;
        for (char c : prefix) {
            int idx = c - 'a';
            if (!cur->children[idx]) return false;
            cur = cur->children[idx];
        }
        return true;
    }
};
```

> **Complexity:** Insert: O(L), Search: O(L), Prefix: O(L) where L = word length. Space: O(N×26).

---

## Union-Find (Disjoint Set Union - DSU)

Tracks which elements belong to the same connected component. Used in Kruskal's MST, social networks, cycle detection in undirected graphs.

```cpp
class DSU {
    vector<int> parent, rank_;

public:
    DSU(int n) : parent(n), rank_(n, 0) {
        iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        if (parent[x] != x)
            parent[x] = find(parent[x]);  // Path compression
        return parent[x];
    }

    bool unite(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return false;  // Already connected
        // Union by rank
        if (rank_[px] < rank_[py]) swap(px, py);
        parent[py] = px;
        if (rank_[px] == rank_[py]) rank_[px]++;
        return true;
    }

    bool connected(int x, int y) { return find(x) == find(y); }
};
```

> **Complexity:** `find` and `unite` are nearly O(1) amortized (inverse Ackermann α(N)).

---

## Monotonic Stack

A stack that maintains elements in strictly increasing or decreasing order. Used for **Next Greater Element**, histogram problems, and span calculations.

```cpp
// Next Greater Element for each index
vector<int> nextGreater(vector<int>& arr) {
    int n = arr.size();
    vector<int> result(n, -1);
    stack<int> stk;  // Stores indices, not values

    for (int i = 0; i < n; i++) {
        // Pop all smaller elements: arr[i] is their next greater
        while (!stk.empty() && arr[stk.top()] < arr[i]) {
            result[stk.top()] = arr[i];
            stk.pop();
        }
        stk.push(i);
    }
    return result;  // Remaining indices have result = -1
}

// Largest Rectangle in Histogram - O(N) using monotonic stack
int largestRectangle(vector<int>& heights) {
    stack<int> stk;
    int maxArea = 0;
    heights.push_back(0);  // Sentinel

    for (int i = 0; i < (int)heights.size(); i++) {
        while (!stk.empty() && heights[stk.top()] > heights[i]) {
            int h = heights[stk.top()]; stk.pop();
            int w = stk.empty() ? i : i - stk.top() - 1;
            maxArea = max(maxArea, h * w);
        }
        stk.push(i);
    }
    return maxArea;
}
```

> **Complexity:** O(N) time - each element is pushed and popped at most once. Space: O(N).

---

## Monotonic Deque (Sliding Window Maximum)

A double-ended queue that maintains the maximum (or minimum) in a sliding window of size K in O(N).

```cpp
vector<int> slidingWindowMax(vector<int>& nums, int k) {
    deque<int> dq;     // Stores indices; front = max of current window
    vector<int> result;

    for (int i = 0; i < (int)nums.size(); i++) {
        // Remove elements outside current window
        if (!dq.empty() && dq.front() <= i - k)
            dq.pop_front();

        // Maintain decreasing order: pop smaller elements from back
        while (!dq.empty() && nums[dq.back()] < nums[i])
            dq.pop_back();

        dq.push_back(i);

        if (i >= k - 1)
            result.push_back(nums[dq.front()]);
    }
    return result;
}
```

> **Complexity:** O(N) time - each element enters/exits deque once. Space: O(K).

---

## Complexity Comparison

| Data Structure | Build | Query | Update | Best Use Case |
|---|---|---|---|---|
| Segment Tree | O(N) | O(log N) | O(log N) | Range sum/min/max + updates |
| Fenwick Tree | O(N log N) | O(log N) | O(log N) | Prefix sums only |
| Trie | O(N·L) | O(L) | O(L) | String prefix search |
| DSU | O(N) | O(α(N)) | O(α(N)) | Connected components |
| Monotonic Stack | O(N) | O(1) | - | Next greater element |
| Monotonic Deque | O(N) | O(1) | - | Sliding window max/min |
