# System Design Fundamentals for Engineering Students

## What is System Design?
System design is the process of defining the architecture, components, modules, and data flow of a system to satisfy specified requirements. At FAANG-level interviews, you're expected to design scalable distributed systems that serve millions of users.

---

## CAP Theorem

The CAP Theorem states that a distributed system can guarantee at most **2 of 3 properties simultaneously**:

| Property | Definition |
|---|---|
| **Consistency** | Every read sees the most recent write (all nodes agree on data) |
| **Availability** | Every request receives a response (not necessarily the latest data) |
| **Partition Tolerance** | System continues operating despite network splits |

Since **network partitions are unavoidable** in practice, you must choose between:
- **CP systems** (consistent + partition-tolerant): HBase, Zookeeper, etcd. Sacrifice availability during partitions.
- **AP systems** (available + partition-tolerant): Cassandra, DynamoDB, CouchDB. Return stale data but stay online.

```
CAP Rule: In presence of network partition (P), choose either C or A.
```

---

## Consistent Hashing

Used in distributed caches and databases to distribute load evenly while minimizing redistribution when nodes join/leave.

**Algorithm:**
1. Hash all server nodes onto a ring `[0, 2^32)`.
2. Hash each key onto the same ring.
3. A key is served by the **nearest clockwise node**.
4. When a node is added/removed, only `K/N` keys need remapping (where K = keys, N = nodes).

**Virtual Nodes:** Each physical server maps to multiple points on the ring to ensure uniform load distribution.

```python
import hashlib

class ConsistentHash:
    def __init__(self, nodes=None, replicas=150):
        self.replicas = replicas  # Virtual nodes per physical node
        self.ring = {}            # hash_value → node
        self.sorted_keys = []

        for node in (nodes or []):
            self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        for i in range(self.replicas):
            virtual_key = self._hash(f"{node}:{i}")
            self.ring[virtual_key] = node
            self.sorted_keys.append(virtual_key)
        self.sorted_keys.sort()

    def remove_node(self, node: str):
        for i in range(self.replicas):
            virtual_key = self._hash(f"{node}:{i}")
            del self.ring[virtual_key]
            self.sorted_keys.remove(virtual_key)

    def get_node(self, key: str) -> str:
        h = self._hash(key)
        for ring_key in self.sorted_keys:
            if h <= ring_key:
                return self.ring[ring_key]
        return self.ring[self.sorted_keys[0]]  # Wrap around ring
```

> **Complexity:** `add_node`: O(R log R), `get_node`: O(log N) where N = virtual nodes, R = replicas

---

## Load Balancing

Distributes incoming traffic across multiple servers to prevent overload.

### Algorithms

| Algorithm | Best For | Notes |
|---|---|---|
| **Round Robin** | Equal capacity servers | Simple, no state |
| **Least Connections** | Variable request times | Directs to least busy server |
| **IP Hash** | Session stickiness | Same client → same server |
| **Weighted Round Robin** | Mixed capacity | Higher weight = more traffic |

### Layer 4 vs Layer 7
- **L4 (TCP/UDP):** Routes based on IP + port. Faster, no content inspection.
- **L7 (HTTP):** Routes based on URL path, headers, cookies. Enables advanced routing (A/B testing, canary deploys).

---

## Rate Limiting

Prevents API abuse by capping request rates. Common algorithms:

### Token Bucket
```python
import time

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        """capacity: max tokens, refill_rate: tokens per second"""
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True  # Request allowed
        return False  # Request throttled
```

### Sliding Window Counter
Better than fixed-window: prevents burst at window boundaries.
```
window_start = now - window_size
count = redis.zcount(user_key, window_start, now)
if count < limit:
    redis.zadd(user_key, {now: now})
    process_request()
else:
    return 429_TOO_MANY_REQUESTS
```

---

## Message Queues (Kafka / RabbitMQ)

Decouple producers and consumers for async processing, buffering spikes, and microservice communication.

### Kafka Architecture
```
Producers → [Topic: Partition 0 | Partition 1 | Partition 2] → Consumers (Consumer Group)
```
- **Topic:** Named stream of messages.
- **Partition:** Ordered, immutable log. Enables parallel consumption.
- **Consumer Group:** Multiple consumers share partitions for horizontal scaling.
- **Offset:** Position in partition log. Enables replay and exactly-once semantics.

### When to Use
| Scenario | Tool |
|---|---|
| High-throughput event streaming (logs, metrics) | Apache Kafka |
| Task queues with routing and priority | RabbitMQ |
| Simple job queue | Redis Lists / AWS SQS |

---

## SQL vs NoSQL

| Dimension | SQL (PostgreSQL, MySQL) | NoSQL (MongoDB, DynamoDB, Cassandra) |
|---|---|---|
| Schema | Fixed, relational | Flexible, document/key-value/wide-column |
| Scaling | Vertical (scale up) | Horizontal (scale out) |
| Transactions | ACID guaranteed | Eventual consistency (BASE) |
| Best For | Complex joins, financial data | High write throughput, unstructured data |

---

## Caching (Redis / Memcached)

### Cache Eviction Policies
- **LRU (Least Recently Used):** Evict the item that hasn't been accessed longest. Most common.
- **LFU (Least Frequently Used):** Evict the item accessed fewest times.
- **TTL (Time To Live):** Expire entries after a fixed time.

### Cache Patterns
```
Cache-Aside (Lazy Loading):
  1. App checks cache → HIT: return data
  2. MISS: fetch from DB → store in cache → return data

Write-Through:
  1. App writes to cache AND DB synchronously. Always consistent, higher write latency.

Write-Behind (Write-Back):
  1. App writes to cache only → async flush to DB. Lower latency, risk of data loss.
```

> **Complexity:** Redis GET/SET: O(1). LRU eviction: O(1) using HashMap + Doubly Linked List.
