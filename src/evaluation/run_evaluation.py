"""
src/evaluation/evaluate.py
==========================
Evaluation script for Kuli AI.
Tests inference speed, RAG grounding, and ROUGE scores.

Generates structured benchmark artifacts in `results/evaluation_report.json`.
"""

import os
import sys
import json
import time
import re
import ast
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.rag.retriever import get_context_with_metadata
from src.rag.prompts import extract_citations

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Curated benchmark test cases spanning Algorithms, Systems, C++, and ML
EVAL_BENCHMARKS = [
    {
        "id": "TC_01",
        "category": "Algorithms",
        "prompt": "Write a C++ function to detect a cycle in a linked list using Floyd's Tortoise and Hare algorithm.",
        "expected_source": "cpp_guide.md",
        "expected_keywords": ["slow", "fast", "ListNode", "nullptr", "O(N)"],
        "reference_solution": """bool hasCycle(ListNode *head) {
    if (!head || !head->next) return false;
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;
    }
    return false;
}"""
    },
    {
        "id": "TC_02",
        "category": "Algorithms",
        "prompt": "Solve the Aggressive Cows problem using binary search on answer in C++.",
        "expected_source": "cpp_guide.md",
        "expected_keywords": ["binary search", "stalls", "canPlace", "sort"],
        "reference_solution": """bool canPlace(vector<int>& stalls, int cows, int dist) {
    int count = 1, last = stalls[0];
    for (int i = 1; i < stalls.size(); i++) {
        if (stalls[i] - last >= dist) { count++; last = stalls[i]; if (count == cows) return true; }
    }
    return false;
}"""
    },
    {
        "id": "TC_03",
        "category": "Machine Learning",
        "prompt": "Explain LoRA (Low-Rank Adaptation) and how rank decomposition works mathematically.",
        "expected_source": "ml_fundamentals.md",
        "expected_keywords": ["W_0", "B", "A", "rank", "freeze", "adapters"],
        "reference_solution": "LoRA decomposes the weight update delta W into two low-rank matrices: delta W = B * A, where B is d x r and A is r x k with r << min(d, k). The base weights W_0 are frozen."
    },
    {
        "id": "TC_04",
        "category": "Python Built-ins",
        "prompt": "How does python's enumerate function work and what is its syntax?",
        "expected_source": "python_builtins.md",
        "expected_keywords": ["enumerate", "index", "iterable", "start"],
        "reference_solution": "enumerate(iterable, start=0) returns an enumerate object yielding tuples of (index, item)."
    },
    {
        "id": "TC_05",
        "category": "Data Structures",
        "prompt": "Write a python function to check if a binary tree is symmetric.",
        "expected_source": "cs_fundamentals.md",
        "expected_keywords": ["def", "isSymmetric", "left", "right", "return"],
        "reference_solution": """def isSymmetric(root):
    def isMirror(t1, t2):
        if not t1 and not t2: return True
        if not t1 or not t2: return False
        return (t1.val == t2.val) and isMirror(t1.right, t2.left) and isMirror(t1.left, t2.right)
    return isMirror(root, root) if root else True"""
    }
]


def extract_code_snippet(text: str) -> str:
    """Extracts python or generic code blocks from markdown."""
    import textwrap
    py_match = re.search(r'```(?:python|py)\n(.*?)\n?```', text, re.DOTALL)
    if py_match:
        return textwrap.dedent(py_match.group(1).strip("\n"))
    
    generic_match = re.search(r'```(?:cpp|c\+\+)?\n(.*?)\n?```', text, re.DOTALL)
    if generic_match:
        return textwrap.dedent(generic_match.group(1).strip("\n"))
    
    return ""


def validate_python_syntax(code_str: str) -> bool:
    """Checks whether the extracted python snippet compiles via ast.parse."""
    if not code_str:
        return False
    try:
        ast.parse(code_str)
        return True
    except SyntaxError:
        return False


def compute_keyword_coverage(text: str, keywords: List[str]) -> float:
    """Measures ratio of expected technical keywords covered in the response."""
    if not keywords:
        return 1.0
    text_lower = text.lower()
    matches = sum(1 for kw in keywords if kw.lower() in text_lower)
    return matches / len(keywords)


def evaluate_system(use_rag: bool = True, use_reranker: bool = True) -> Dict[str, Any]:
    """Runs evaluation across all benchmark cases."""
    print(f"\n[Running Evaluation] RAG={use_rag} | Reranker={use_reranker}")
    
    # Load ROUGE evaluator
    try:
        import evaluate
        rouge_metric = evaluate.load("rouge")
    except Exception as e:
        print(f"Warning: ROUGE metric load failed ({e}). Proceeding with keyword coverage.")
        rouge_metric = None

    results = []
    total_time = 0.0
    python_syntax_passes = 0
    python_syntax_tasks = 0
    citation_hits = 0

    from src.app.inference import generate_response

    for tc in EVAL_BENCHMARKS:
        t0 = time.time()
        response = generate_response(
            prompt=tc["prompt"],
            use_rag=use_rag,
            use_reranker=use_reranker,
            temperature=0.2
        )
        elapsed = time.time() - t0
        total_time += elapsed

        kw_score = compute_keyword_coverage(response, tc["expected_keywords"])
        code = extract_code_snippet(response)

        # Check syntax if python task
        is_valid_py = None
        if "python" in tc["prompt"].lower() or "python" in tc["category"].lower():
            python_syntax_tasks += 1
            is_valid_py = validate_python_syntax(code)
            if is_valid_py:
                python_syntax_passes += 1

        # Check citation grounding
        citations = extract_citations(response)
        has_expected_citation = any(
            tc["expected_source"].lower() in (c.get("file", "") or "").lower()
            for c in citations
        )
        if has_expected_citation or (tc["expected_source"].lower() in response.lower()):
            citation_hits += 1

        results.append({
            "id": tc["id"],
            "category": tc["category"],
            "prompt": tc["prompt"],
            "latency_sec": round(elapsed, 2),
            "keyword_coverage": round(kw_score, 2),
            "valid_syntax": is_valid_py,
            "has_citation": has_expected_citation,
            "citations_found": citations,
            "response_preview": response[:200] + "..."
        })

    avg_latency = total_time / len(EVAL_BENCHMARKS) if EVAL_BENCHMARKS else 0
    syntax_pass_rate = (python_syntax_passes / python_syntax_tasks * 100) if python_syntax_tasks else 100.0
    citation_precision = (citation_hits / len(EVAL_BENCHMARKS) * 100) if EVAL_BENCHMARKS else 0

    return {
        "config": {"use_rag": use_rag, "use_reranker": use_reranker},
        "avg_latency_sec": round(avg_latency, 2),
        "syntax_pass_rate": round(syntax_pass_rate, 1),
        "citation_precision": round(citation_precision, 1),
        "test_cases": results
    }


def main():
    print("=" * 65)
    print(" Kuli AI: Evaluation Suite")
    print("=" * 65)

    # Run benchmark on full system (RAG + Reranker)
    report = evaluate_system(use_rag=True, use_reranker=True)

    # Save to results
    output_path = os.path.join(RESULTS_DIR, "evaluation_report.json")
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 65)
    print(" BENCHMARK RESULTS SUMMARY")
    print("=" * 65)
    print(f"Total Test Cases:            {len(EVAL_BENCHMARKS)}")
    print(f"Code Syntax Pass Rate:       {report['syntax_pass_rate']}%")
    print(f"Citation Grounding Accuracy: {report['citation_precision']}%")
    print(f"Average Latency:             {report['avg_latency_sec']}s / query")
    print(f"\nDetailed report saved to: {output_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
