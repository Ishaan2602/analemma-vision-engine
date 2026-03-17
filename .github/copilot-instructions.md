# Analemma Project - Copilot Instructions

## End-of-prompt protocol

At the END of every prompt response in this project:

1. **Update `PROJECT_LOG.md`**: Add or update the current session entry (most recent at top). Log what was done, what was changed, key findings, and next steps.

2. **Update `IMPLEMENTATION_NOTES.md`**: If the user asked any questions about theory, implementation details, or "why" something works a certain way, add an explanation under the current session heading. Most recent session at the top.

## Question prompt protocol

- When the user says "ask me with a question prompt" or "ask me" or "give me a question prompt", use the `vscode_askQuestions` tool to present clickable option choices. **Do NOT end prompt execution** -- present the question and wait for the answer, then continue based on the selected option.
- This applies anytime the user wants to make a choice before you proceed.

## Verification protocol

- After making code changes, always rerun relevant notebook cells or tests to verify the fix.
- If you cannot visually verify a result (images, plots), **ASK the user** via `vscode_askQuestions`. Phrase it as a clear question: "Can you check cell N and confirm whether [specific thing] looks correct?"
- When diagnosing visual issues (overlay alignment, plot shapes), describe what you expect the user to see and ask them to confirm or describe discrepancies.

## Project conventions

- Core engine code lives in `analemma/` (calculator.py, sky_mapper.py, plotter.py, image_anchor.py, metadata_parser.py)
- Documentation lives in `docs/`
- `docs/PROJECT_LOG.md` and `docs/IMPLEMENTATION_NOTES.md` track session history
- Input images are in `input_images/<name>/metadata.txt` + image file
- The notebook `analysis.ipynb` is the primary interactive testing tool
- All metadata files use KEY=VALUE format; parser stops at `--- REFERENCE DATA` separator

## Plotting conventions

- When creating side-by-side comparison plots of analemma curves (e.g., old vs new timezone, approximate vs HP), always use **fixed axes** so visual comparison is meaningful. Compute the combined data range across both plots and set `xlim`/`ylim` identically.
- Default precision mode is `high-precision` (Astropy/JPL DE440).

## Code style

- Use numpy for vectorized calculations where possible
- Maintain the 3-layer architecture: Calculator -> SkyMapper -> Plotter
- ImageAnchorer is a 4th layer that composes the other three
- Type hints on public methods; docstrings in numpy style

## Writing style

All documentation, README text, log entries, and generated text must read like it was hand-written by a developer. This applies to all subagents and processes.

- No em-dashes. Use double hyphens (--) or restructure the sentence.
- No emoji anywhere in docs or code.
- No "**Topic**: description of topic" formatting pattern. Vary structure.
- No filler: "It's important to note...", "This ensures that...", "In order to...", "Leveraging..."
- Use contractions where natural (it's, doesn't, we've).
- Short paragraphs. Direct phrasing. Technical precision over verbosity.
- Write like you're explaining to a colleague, not generating a report.
- The README and TECHNICAL_DESCRIPTION should be highly technical and theory/implementation-focused. Key formulas, techniques, and technologies used.
- Avoid any formatting or phrasing that signals AI generation.
