# CS Fundamentals

## Big-O Notation
Big-O notation is used in Computer Science to describe the performance or complexity of an algorithm. Big-O specifically describes the worst-case scenario, and can be used to describe the execution time required or the space used (e.g. in memory or on disk) by an algorithm.

- **O(1) - Constant Time:** The algorithm will always execute in the same time (or space) regardless of the size of the input data set. Example: Looking up a dictionary key.
- **O(N) - Linear Time:** The performance will grow linearly and in direct proportion to the size of the input data set. Example: Searching an unsorted list.
- **O(N^2) - Quadratic Time:** The performance is directly proportional to the square of the size of the input data set. This is common with algorithms that involve nested iterations over the data set. Example: Bubble sort.
- **O(log N) - Logarithmic Time:** The execution time goes up linearly while the n goes up exponentially. Example: Binary search.

## Sorting Algorithms
- **Bubble Sort:** Repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order. O(N^2).
- **Merge Sort:** A divide and conquer algorithm that divides the input array into two halves, calls itself for the two halves, and then merges the two sorted halves. O(N log N).
- **Quick Sort:** Picks an element as pivot and partitions the given array around the picked pivot. O(N log N) on average.

## Data Structures
- **Array/List:** A collection of items stored at contiguous memory locations.
- **Linked List:** A linear collection of data elements whose order is not given by their physical placement in memory. Instead, each element points to the next.
- **Stack:** A linear data structure which follows a particular order in which the operations are performed. The order may be LIFO (Last In First Out).
- **Queue:** A linear structure which follows a particular order in which the operations are performed. The order is First In First Out (FIFO).
- **Hash Table (Dictionary):** A data structure that implements an associative array abstract data type, a structure that can map keys to values.
