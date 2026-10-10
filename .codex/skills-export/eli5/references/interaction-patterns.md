# Teaching patterns

Choose the smallest pattern that makes the central relationship observable.

## Follow the journey
For a sequence: stable spatial positions, Next/Back/Reset, one active stage,
and a sentence explaining the transition. Back must restore state, not merely
change the highlight. Show the final state without requiring motion.

## Compare fairly
For alternatives: same input, same units, matched scale. Show both the result
and its cause. Use a toggle only if the previous state remains easy to recall.
Do not claim a performance comparison from decorative animation durations.

## Change one thing
For cause/effect: a slider or small set of buttons modifies a real local model.
Render both the input and computed result from one state object. Explain units,
assumptions, boundaries, and what the model leaves out. Label simulations.
Test endpoints, rapid repeated input, reset, and a counterexample.
The caching example demonstrates this pattern; its response is computed from
origin/cache state. Its animation is illustrative, not a network benchmark.

## Predict, then reveal
For a misconception: ask a small concrete question, accept a choice, then
explain why the outcome follows. Avoid scoreboards or shaming.
Bundled enhancement:
```html
<section class="prediction" data-prediction>
  <h2>Will the saved copy change by itself?</h2>
  <div class="choices">
    <button type="button" data-choice="wrong">Yes</button>
    <button type="button" data-choice="correct">No</button>
  </div>
  <p data-feedback role="status"></p>
  <div data-answer>It stays the same until it is refreshed or replaced.</div>
</section>
```
The answer starts visible in source HTML. The enhancement hides it only when
working JavaScript is available and shows it on either choice.

## Layer the real terms
Use a small <details> section to map analogy → actual term → limitation.
Do not generate enormous glossaries; choose only terms used in the lesson.
