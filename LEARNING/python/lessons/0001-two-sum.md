# 0001 — Two Sum

## Problem

You receive a list of integers, `nums`, and an integer, `target`. Find the **indices** of two different elements whose values add up to `target`. Return the two indices as a list in either order.

Assume each input has exactly one valid pair. You may use each element at most once. The list can contain duplicate values and negative numbers.

Write a Python function that takes `nums` and `target` and returns the two indices.

## Examples

| `nums` | `target` | One valid return value | Why |
| --- | ---: | --- | --- |
| `[2, 7, 11, 15]` | `9` | `[0, 1]` | `nums[0] + nums[1] == 9` |
| `[3, 2, 4]` | `6` | `[1, 2]` | The values at indices 1 and 2 add to 6. |
| `[3, 3]` | `6` | `[0, 1]` | Equal values at different indices can form a pair. |

## Progress — first verbal attempt

You described a pair search: for each index, compare its value with values at later indices until their sum equals `target`. Add the **values**; return the two **indices**. Starting the inner comparison after the current index avoids using one element twice and checking the same pair again. Because the problem guarantees one valid pair, you can return as soon as you find it.

**Next step:** Write your full Python answer from scratch in the [practice file](../practice/0001-two-sum.py), then trace it on `[3, 3]`.

## Work through it with the tutor

1. In your own words, what goes into the function, and what must come out? Why do the examples return positions rather than values?
2. How would you solve this with pencil and paper if you had no special data structure? Which checks repeat as the list grows?
3. What information would let you decide, while looking at one value, whether its partner appeared earlier? Where could you keep that information?
4. Describe your approach before writing code. Then implement it in Python.
5. Trace your code on `[3, 3]` and `[3, 2, 4]`. Add one test with a negative number. Can one element accidentally pair with itself?
6. How many operations and how much extra memory does your approach need as the list grows? Explain why in plain English.

## After you solve it

With notes closed, explain the key idea as if teaching someone new to Python. Record only the part you could not explain clearly, then retry that explanation.
