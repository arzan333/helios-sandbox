---
owner: Developer
version: 1.0
effective_date: 2026-03-02
review_date: 2026-09-02
---

# Prompt skeleton

The shape every efficient working prompt in this programme has. Five blocks,
in this order. If a block is empty, delete the heading; do not pad it.

```
<Task in one sentence, naming the ticket or file it is about.>

Inputs:
- <path to a file Claude should read>            (T1: reference, do not paste)
- <path>, <section or line range only>            (T2: targeted read)

Output: <one file path>, and nothing else.
- <shape: table with named columns | numbered list | JSON with named keys>   (T3)
- <size: N to M rows | under N lines>                                        (T4)
- <exact strings or values that must appear, so a tester can check them>

Rules:
- <what counts as done, in one line>
- <what must not be invented or decided>
- <what to do with anything undecided: list it under "Open questions">

Reply in chat with one line: <the one fact you want back>.                  (T4)
```

## Why each block earns its place

| Block | Without it |
|---|---|
| Task | Claude infers the job from the inputs and sometimes infers a different job |
| Inputs | Claude searches the repository, reading whatever looks relevant; that is the biggest single leak |
| Output path | The answer lands in the chat, cannot be scored, diffed or committed |
| Output shape and size | Output is the expensive half; an unshaped answer is a long one |
| Rules | The two most common failures are invented rules and quietly resolved open questions |
| Reply line | Without it Claude recaps the whole file in the chat, paying for the output twice |

## What is deliberately not in the skeleton

- A role paragraph. One clause at most ("as the BA on this ticket"). Twenty years of experience is zero tokens of instruction.
- Examples. Add one only when the shape cannot be stated in fewer tokens than the example costs (T5).
- Restated constraints, hedges, courtesy (T6).

## The judge is the same shape

The scoring prompt (`prompts/week2-lab/score.md`) follows the skeleton: task, two
inputs, a shaped reply, rules (evidence per row, no other files, do not edit).
Run it on a stronger model than the one that did the work. That is the pattern
Week 3 uses at the design gate and Week 4 packages as a Skill.

## Worked instance

`prompts/week2-lab/ac-320.md` is this skeleton filled in for HEL-142. Compare it
with `ac-2000.md`, which asks for the same thing with none of the blocks and all
of the omissions above.

## Turning your best v1 into a team template

A template is a v1 with the parts that change turned into placeholders, so the
next person types the placeholders and nothing else. Save it as
`week2/prompts/templates/<name>.md`, in this shape:

```
<!-- template: <name>  v1   owner: <role from docs/helios-landscape.md>
     baseline: v0 <N> fresh tokens, <S>/25  ->  v1 <N> fresh tokens, <S>/25 (scorer: <model>)
     techniques: T1 T2 T4 T6 -->

Task: <one sentence> for {{TICKET}}.

Inputs (read; do not paste back):
- helios-backlog/{{TICKET}}.json
- {{SPEC_FILE}}, section {{SECTION}} only (grep for the heading, read to the next one)

Output: write {{OUTPUT_FILE}} containing
- <fixed structure, one line each>
- <bounds and exact strings>

Rules:
- <checkable outcomes>
- <what must not be invented; open questions go under "Open questions">

Reply in chat with one line: <count or verdict>.
```

| Placeholder | Comes from |
|---|---|
| `{{TICKET}}` | The ticket key. Everything else about the ticket comes from its file |
| `{{SPEC_FILE}}`, `{{SECTION}}` | The file and heading your v1 pointed at. If the document has no usable headings, that is a Week 4 problem; note it in the comment |
| `{{OUTPUT_FILE}}` | Always a file. The chat gets one line |

The comment at the top is the evidence that the template earned its place. A
template with no numbers on it is a preference. Week 4 turns templates like this
into Skills.
