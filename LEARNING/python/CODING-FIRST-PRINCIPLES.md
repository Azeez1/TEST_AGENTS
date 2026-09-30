# Coding from first principles

Two small maps to use before writing Python. Start with the question in plain English, then translate one step at a time. These are thinking aids, not answer keys.

## 1. The coding map

**Input → remember data → apply rules → repeat when needed → output → verify**

| Ask yourself | Python building block |
| --- | --- |
| What comes in, and what must come out? | Function parameters and `return` |
| What do I need to keep track of? | Variables, lists, dictionaries, or sets |
| When should something happen? | `if` / `else` |
| What happens more than once? | `for` / `while` loops |
| What is a reusable piece of work? | A function |
| How do I know it worked? | Examples, tests, and error inspection |

Not every problem needs every step. Identify the needed steps before choosing syntax.

## 2. The remembering cheat code

**What will I need to know later about the items I have already passed?**

| Future question | Keep track with |
| --- | --- |
| How many have I found? | A counter |
| What is the best value so far? | A variable |
| Have I seen this before? | A set |
| How many times, or at which index, did I see it? | A dictionary |
| Do I need the items in order? | A list |

While processing each item: **check what you remember → make a decision → update what you remember**. Think about whether the current item should count as something already seen; that determines whether checking or updating happens first.

Choose the *future question* first. It tells you what to store, rather than making you guess a data structure from the problem name.

## 3. The edge-case sweep

Start with the **contract**: Which inputs are allowed, and what result is required? Then name an assumption, change it, and predict what the code should do.

| Check | Ask |
| --- | --- |
| Size | What happens with zero items, one item, the smallest valid input, or a very large input? |
| Values | What about zero, negatives, duplicates, ties, or special characters when relevant? |
| Position | Does it work at the first or last item, or when order changes? |
| Branches and state | Can each `if` go both ways? Can a loop run zero, once, or many times? Did I check or update remembered data in the right order? |
| Outcome | What if there is no result or more than one, **if the contract allows that**? |

For Two Sum, `nums = [3, 3]` and `target = 6` checks that equal values at *different indices* can form a pair. For an FDE integration, also check missing fields, failed API calls, and duplicate requests.

This sweep is a prompt for finding likely misses, not a guarantee that every edge case has been found. Turn each relevant case into an input with an expected output before changing code.

## Practice prompt

Before coding a problem, say or write: “My input is __. I must return __. I need to remember __ because later I will ask __. I repeat __. I will verify it with __.” Then write the smallest Python version yourself and run it.
