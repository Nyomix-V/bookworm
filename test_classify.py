"""test_classify.py — Script de validation de classify_with_dict()"""
import time
from bookworm import classify_with_dict, _cleaner

books = [
    (11,   "Alice's Adventures in Wonderland", "Children's Literature"),
    (345,  "Dracula",                           "Science Fiction and Fantasy"),
    (1661, "Sherlock Holmes",                   "Crime and Mystery"),
    (84,   "Frankenstein",                      "Science Fiction and Fantasy"),
    (164,  "Twenty Thousand Leagues",           "Science Fiction and Fantasy"),
    (113,  "Treasure Island",                   "Children's Literature"),
]

for bid, name, expected in books:
    with open(f"{bid}.txt", "r", encoding="utf-8") as f:
        raw = f.read()
    text = _cleaner(raw, lower=False)
    t0 = time.time()
    detected = classify_with_dict(text)
    elapsed = time.time() - t0
    status = "OK  " if detected == expected else "FAIL"
    print(f"[{status}] {name[:35]:<35}  detected={detected}  expected={expected}  ({elapsed:.3f}s)")
