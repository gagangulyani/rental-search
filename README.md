# rental-search

An [Agent Skill](https://agentskills.io/specification) for helping someone find a
rental flat in an Indian city — structured intake, locality research with sourced
rent bands, and a script that pulls property-dealer contacts for named localities.

Works with Claude Code and other runtimes that read `~/.claude/skills/` or
`~/.agents/skills/`.

## Why

Ask a general-purpose agent to help with a flat hunt and it will usually start
web-searching immediately, hand back a tidy list of neighbourhoods, and end
there. Tested against that baseline, four things were consistently missing:

- **It asked nothing first.** No budget clarification, no occupancy, no timeline
  — so the advice was aimed at a market the person may not be shopping in.
- **It wrote no file.** Everything lived in chat, which is not where you are when
  you're standing in a flat deciding whether to take it.
- **It dropped source confidence.** It verified a claim internally, then
  presented verified and assumed facts identically, on the reasoning that
  provenance was internal bookkeeping. The person about to pay a deposit needs it
  more than the agent does.
- **It refused to produce contacts**, stating it had "no access to live local
  directories." That is not true, and it is the gap this skill mainly exists to
  close.

## What it does

**Gates on intake.** Five question groups — money, person, movement, clock, and
why they are moving at all — before any locality gets recommended. Two of these
carry most of the weight:

- *Is the budget all-in or base rent?* Society maintenance in India is commonly
  ₹2,000–4,000/month and quoted separately, so the same headline figure describes
  two different searches.
- *Why are you moving?* The stated reason is often a proxy. A search framed
  entirely around metro connectivity turned out to be about escaping a bad
  landlord — which flipped the target from "best-connected area" to
  "best-managed building", and made the cheapest independent-owner option the
  worst one rather than the best.

**Writes files, tagged.** A problem brief before research, then findings with a
source link per claim. Every factual claim carries `[V]` verified — with the
receipt — or `[I]` inferred. Rent figures are labelled as portal *asking* prices,
not transacted rents.

**Gets actual phone numbers.** `extract_brokers.py` reads SquareYards' public
locality agent directories. Each agent's profile photo is served from a URL whose
filename encodes their registered number; the script decodes it, deduplicates,
and discards any number appearing across multiple listings — those are shared
lead-routing lines rather than individual brokers.

```bash
python3 rental-search/extract_brokers.py \
  --city noida --areas "sector-37,arun-vihar,sector-31" --pages 3 --whatsapp
```

Emits a markdown table and a WhatsApp-pasteable text block. Handles sector slugs
and named localities alike. Tested across two cities; yield varies a lot by
market (~24% of listed agents in one, ~7% in another), so the skill requires
reporting coverage gaps by name rather than passing over them.

## Honesty rules the skill enforces

These are constraints on the agent, and they matter more than the scraping:

- **Decoded numbers are labelled inferred, never verified.** They are
  structurally valid and unique per agent, but unconfirmed against any second
  source. Some will be stale or reassigned.
- **Never invent, guess, or complete a partial number.** Missing is fine. Wrong
  is worse than missing.
- **Say which localities returned nothing.** A gap is a finding; silence is not.
- **If the user names their own preferred areas, research those too** — and if
  the data disagrees with an earlier recommendation, say so out loud instead of
  quietly switching.

## Install

```bash
git clone https://github.com/gagangulyani/rental-search.git
cp -r rental-search/rental-search ~/.claude/skills/
```

Then invoke `/rental-search`, or just describe a stuck flat hunt and it triggers.

## Scope and limits

- **India-focused.** Assumptions about maintenance charges, deposits in months,
  brokerage at one month's rent, and bachelor-tenant restrictions are specific to
  that market.
- **One directory source.** The extractor targets SquareYards only. If the site
  changes its markup or image URL scheme, extraction breaks — it will report zero
  contacts rather than fail loudly.
- **No harvested data ships here.** The repo contains no phone numbers. Run the
  script locally to generate contacts for your own search; `.gitignore` is set up
  to keep the output uncommitted.
- Scrapes public directory pages at ordinary browsing rates. Verify any agent
  independently — in India, via [UP RERA](https://up-rera.in) or your state's
  equivalent — before transacting.

## Files

| File | Purpose |
|---|---|
| `rental-search/SKILL.md` | Workflow, evidence rules, rationalization table |
| `rental-search/intake-questions.md` | Five batches of ready-to-paste questions |
| `rental-search/extract_brokers.py` | Contact extractor, no dependencies beyond curl |

## License

MIT
