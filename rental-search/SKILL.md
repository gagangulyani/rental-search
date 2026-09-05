---
name: rental-search
description: Use when someone is looking for a flat, apartment, PG or rental home in an Indian city and is stuck — budget too tight for their stated requirements, brokers not responding or not helping, unsure which sectors or localities to target, or conflicting wants like open view versus metro connectivity. Also use when they want broker or property-dealer phone numbers for specific areas.
---

# Rental Search

## Overview

A person asking for house-hunting help is describing a market with hard
constraints they have not yet priced. The job is to find where their stated
constraints actually break, name the real driver behind the move, and hand back
something they can act on today — including phone numbers.

**Core principle: the bottleneck is usually channel, timeline, or an unmeasured
cost rather than the budget itself.** Treat that as a prior to check, not a
conclusion. Sometimes the number genuinely cannot buy what they described — when
sourced rent bands show that, say so plainly and early instead of hunting for a
channel fix that does not exist.

## The Intake Gate

**Ask before researching. Always.** A baseline agent given this task went
straight to web search, asked zero questions, and produced neighbourhood advice
for a person whose actual problem it never learned.

Ask in batches of about four (use `AskUserQuestion` where available). You need
all five rows below answered before recommending any locality. The reference file
`intake-questions.md` sequences them into ask-ready batches with option wordings —
its batch numbers are a delivery order, not a different checklist.

| Group | Must establish |
|---|---|
| **Money** | Is the budget all-in or base rent? Deposit available, in months? |
| **Person** | Single / couple / family? Food habits? Both change which societies accept them. |
| **Movement** | Commute anchor or work-from-home? Tolerance to a station, in minutes and mode? |
| **Clock** | Move-in date. Whether it can slip. |
| **The real driver** | Why move *at all*? Ask it directly. |

**"All-in or base rent" is not optional.** In India a society's maintenance
charge is commonly ₹2,000–4,000/month and is quoted separately. The same headline
number means two different searches depending on the answer.

**Always ask why they are moving.** The stated reason is often not the driver. A
user who framed a search entirely around metro connectivity turned out to be
leaving a bad landlord — which changed the target from "best-connected sector"
to "best-managed building", and made a cheap independent-owner floor the *worst*
option rather than the best.

**If no interactive user is available** (batch run, subagent, scripted context):
write `problem-brief.md` with the questions listed verbatim under open questions,
state that you are blocked on them, and stop. Do not substitute plausible answers
for missing ones — a locality recommendation built on guessed constraints is the
failure this gate exists to prevent.

## Output Contract

Produce files, not just chat. The baseline agent wrote nothing; the user was
left with advice they could not carry to a viewing.

Write, in order:

1. **`problem-brief.md`** — constraints as a table, soft preferences, exclusions,
   the real driver, and an explicit open-questions list. Write it before
   researching so gaps are visible.
2. **`research-findings.md`** — locality-by-locality, with rent bands and a
   source link per claim. One pass per distinct market.
3. **`broker-list.md`** and a WhatsApp-pasteable `.txt` — see below.

If their preferred areas differ from what your data recommends, **research their
list too and say plainly which analysis you are contradicting and why.** Do not
quietly switch recommendations.

## Evidence Tagging

Every factual claim in a written file carries a tag:

- **`[V]`** — verified, followed immediately by the source link or command output.
- **`[I]`** — inferred, believed but unchecked.

State once, near the top of any rent table: portal figures are **asking prices,
not transacted rents**, and portal minimums are frequently a single bad unit.

The baseline agent verified a claim internally, then stripped the distinction out
of what it gave the user, reasoning that tagging was "not something I surface to
an end user". The user is the one about to pay a deposit. They need it more
than you do.

## Getting Real Broker Contacts

**Contacts are obtainable. Do not tell the user this is impossible.** The
baseline agent declined, saying it had "no access to live local directories".
That is false, and the refusal is the single biggest gap this skill closes.

**Run it once you have localities, not before.** The `--areas` slugs must come
from somewhere real: areas the user named, or areas your research established.
Guessing slugs to produce contacts faster reproduces the intake failure one step
downstream. If intake is incomplete and the user has named no areas, say the
extractor is ready and blocked on which localities to target.

```bash
python3 rental-search/extract_brokers.py \
  --city noida --areas "sector-37,arun-vihar,sector-31" --pages 3 --whatsapp
```

SquareYards serves each agent's profile photo from a URL whose filename encodes
their registered number. The script decodes it, dedupes, and drops any number
appearing on multiple listings — those are shared lead-routing lines, not
brokers. Works on sector slugs and named localities alike (`kothrud`, `baner`,
`arun-vihar`).

Three rules when you report the results:

1. **Label the numbers `[I]`.** They are structurally valid and unique per
   agent, but not confirmed against a second source. Say so where the user will
   read it. Try to corroborate at least one; report honestly if you cannot.
2. **State coverage gaps by name.** Some localities yield nothing. Yield varies
   widely — about 24% of agents in one city, 7% in another. "No numbers
   recoverable for X" is a finding; silence is not.
3. **Never invent, guess, or complete a partial number.** Missing is fine.
   Wrong is worse than missing.

Hand brokers a script that front-loads every disqualifying constraint at once —
budget as all-in, occupancy, food habits, deposit, timeline — so a broker who
cannot help says no in thirty seconds instead of a week.

## Always Run Non-Broker Channels Too

Brokers earn a percentage of rent, so a low-budget rental is the lowest-value
job on their desk, and they can only show their own inventory. Owner-direct
listings and in-society vacancies are invisible to them.

Add: NoBroker and portal "no brokerage / owner" filters; local Facebook rental
groups (**post the requirement**, don't only scan); and society **guards and
facility managers**, who know every vacancy in their towers before any portal
and are paid by nobody for it.

## Hunt the Unmeasured Cost

Before recommending anything, ask what has not been priced. Recurring culprits:
society maintenance, DG/power-backup billed separately, covered parking as an
extra, and brokerage split. Each one silently breaks an all-in budget. Put them
in the open-questions list and in the broker call script.

## Red Flags — Stop

- About to research before completing intake
- About to say broker numbers cannot be obtained
- About to hand over a number you did not decode from a real page
- Writing a rent figure with no `[V]`/`[I]` tag
- Recommending a locality without knowing if the budget is all-in
- Quietly switching recommendations when the user names their own areas
- Treating the stated reason for moving as the real one

## Rationalizations

| Excuse | Reality |
|---|---|
| "I don't have access to broker directories" | You do. Run the script. The baseline agent's refusal here is the gap this skill exists to close. |
| "I'll ask questions after I research a bit" | You will anchor on the wrong market. Intake first. |
| "They said connectivity, so it's connectivity" | Ask why they're moving. It is frequently a landlord, a neighbour, or a rent rise. |
| "Tagging sources is clutter for a non-technical user" | They are about to pay a deposit on this. Tag it. |
| "Budget is the constraint" | Usually it is channel, timeline, or maintenance. Check those first. |
| "Their sector list is wrong, I'll steer them to mine" | Research theirs, then state the disagreement openly. |
| "A file is overkill, I'll put it in chat" | They need it at a viewing, on a phone, next week. |
