# Agent Black Box

A flight recorder and counterfactual debugger for tool-using agents.

## Problem

A failed agent trace shows what happened but rarely explains which tool observation caused the mistake.

## Approach

Record typed events, tool inputs, observations, decisions and outcomes. Replay a deterministic sandbox while intervening on one observation at a time. Compare task outcomes and locate minimal failure-inducing changes.

## Demo concept

A support agent issues the wrong refund after stale policy data. Replay the trace with fresh policy, a timeout, and a malformed tool result; show which intervention fixes the outcome.

## First implementation

A Python trace schema, deterministic simulated support workflow, replay CLI, and three intervention types with regression tests. No real customer data.

## Evaluation

Measure reproducibility, mutation detection and known-cause localization on seeded failures. Compare with naive retry and full-trace inspection. Label model reruns as stochastic and avoid claiming formal causality from a single replay.

## Milestones

1. Deterministic sandbox and replay engine
2. Provider-independent recorded trace import and local model adapter
3. Counterfactual comparison UI and minimal failure cases
4. Held-out failure suite and evidence-backed case study

## Your contribution

Describe an automation that failed in a surprising way and what the correct result should have been.

## Status and license

Design brief only; no implementation or measured results yet. Original code will use GPL-3.0-only.
