# Systematic debugging

## Iron law

> No fix without root-cause investigation first.

1. **Investigate:** read the entire error, reproduce it, inspect recent changes, instrument
   boundaries, and trace data backward to its source.
2. **Compare:** find a working example, read it fully, and list every difference.
3. **Hypothesize:** state one cause and test one variable. If disproved, remove the intervention
   before testing another hypothesis.
4. **Implement:** write a failing reproduction test, apply one root-cause fix, and run the full
   suite.

After three failed fix attempts, stop. Repeated failure is evidence that the specification or
architecture may be wrong. Return to architecture review with the symptom, hypotheses, observations,
and suspected structural cause.

