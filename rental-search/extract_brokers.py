#!/usr/bin/env python3
"""
Extract broker/agent contacts from SquareYards locality directories.

SquareYards serves each agent's profile photo from a URL whose filename starts
with their registered number:  .../profilepic/91<10-digit><timestamp>.jpg
This decodes that. Numbers are INFERRED, never independently verified.

Usage:
  python3 extract_brokers.py --city noida --areas "sector-37,sector-25,arun-vihar" --pages 3
  python3 extract_brokers.py --city pune --areas "kothrud,baner" --pages 5 --whatsapp
"""
import argparse, collections, json, re, subprocess, sys, time
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
BASE = "https://www.squareyards.com"


def fetch(url, retries=2):
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                ["curl", "-sL", "--max-time", "30", "-A", UA,
                 "-H", "Accept-Language: en-IN,en;q=0.9", url],
                capture_output=True, text=True, timeout=45)
            if r.stdout and len(r.stdout) > 2000:
                return r.stdout
        except subprocess.TimeoutExpired:
            pass
        if attempt < retries:
            time.sleep(1.5)
    return ""


def candidate_urls(city, area):
    """SquareYards uses a few directory URL shapes; try each."""
    return [f"{BASE}/real-estate-agents-in-{area}-{city}",
            f"{BASE}/real-estate-agents-in-{city}-{area}",
            f"{BASE}/real-estate-agents-in-{area}"]


def parse(html):
    out = []
    for b in re.split(r'<div class="agentTileBox', html)[1:]:
        def g(p):
            m = re.search(p, b)
            return m.group(1).strip() if m else ""
        uid = g(r'data-id="([^"]*)"')
        if not uid:
            continue
        pic = g(r'profilepic/(\d+)\.jpg')
        phone = ""
        # 91 + 10-digit Indian mobile (starts 6-9) + timestamp
        if pic.startswith("91") and len(pic) > 12 and pic[2] in "6789":
            phone = pic[2:12]
        out.append(dict(uid=uid, name=g(r'data-username="([^"]*)"'),
                        loc=g(r'data-sublocalityname="([^"]*)"'),
                        exp=g(r'data-experience="([^"]*)"'),
                        slug=g(r'data-urlslug="([^"]*)"'), phone=phone))
    return out


def crawl(city, areas, pages):
    recs, resolved = {}, {}
    for area in areas:
        base_url = None
        for cand in candidate_urls(city, area):
            html = fetch(cand)
            if "agentTileBox" in html:
                base_url = cand
                break
        if not base_url:
            print(f"  [!] {area}: no directory found", file=sys.stderr)
            continue
        resolved[area] = base_url
        found = 0
        for p in range(1, pages + 1):
            html = fetch(base_url if p == 1 else f"{base_url}?page={p}")
            got = parse(html)
            if not got:
                break
            found += len(got)
            for r in got:
                r["area"] = area
                prev = recs.get(r["uid"])
                if prev is None:
                    recs[r["uid"]] = r
                elif r["phone"] and not prev["phone"]:
                    prev["phone"] = r["phone"]
        print(f"  [+] {area}: {found} cards", file=sys.stderr)
    return list(recs.values()), resolved


def expnum(r):
    e = (r.get("exp") or "").replace("+", "")
    return int(e) if e.isdigit() else -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True, help="e.g. noida, pune, gurgaon")
    ap.add_argument("--areas", required=True,
                    help="comma-separated slugs, e.g. sector-37,arun-vihar,kothrud")
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--whatsapp", action="store_true",
                    help="also emit a WhatsApp-pasteable block")
    ap.add_argument("--out", default="brokers")
    a = ap.parse_args()

    areas = [s.strip() for s in a.areas.split(",") if s.strip()]
    print(f"Crawling {len(areas)} areas in {a.city}...", file=sys.stderr)
    rows, resolved = crawl(a.city, areas, a.pages)

    counts = collections.Counter(r["phone"] for r in rows if r["phone"])
    shared = {p for p, n in counts.items() if n > 1}
    usable = [r for r in rows if r["phone"] and r["phone"] not in shared]

    Path(f"{a.out}.json").write_text(json.dumps(rows, indent=1))

    print(f"\n{len(rows)} agents | {len(usable)} with a unique number "
          f"| {len(shared)} shared/call-centre lines excluded", file=sys.stderr)
    if shared:
        print(f"  excluded (appeared on multiple listings): {', '.join(sorted(shared))}",
              file=sys.stderr)

    by_area = collections.defaultdict(list)
    for r in usable:
        by_area[r["area"]].append(r)

    md = ["# Broker Contacts\n",
          "**Numbers are INFERRED, not verified.** Decoded from the agent's "
          "profile-image filename on SquareYards. Structurally valid and unique "
          "per agent, but not confirmed against any second source. Expect some "
          "to be stale or reassigned. Open with the person's name.\n"]
    for area in areas:
        items = sorted(by_area.get(area, []), key=lambda r: -expnum(r))
        md.append(f"\n## {area} — {len(items)} contacts\n")
        if not items:
            md.append(f"_None recoverable. Check {resolved.get(area, 'the directory')} "
                      "in a browser._\n")
            continue
        md += ["| Name / Firm | Yrs | Phone | Profile |", "|---|---|---|---|"]
        for r in items:
            md.append(f"| {r['name']} | {r['exp'] or '—'} | **+91 {r['phone']}** | "
                      f"[profile]({BASE}/agent/{r['slug']}/{r['uid']}) |")
    Path(f"{a.out}.md").write_text("\n".join(md))
    print(f"wrote {a.out}.md", file=sys.stderr)

    if a.whatsapp:
        wa = [f"*Broker contacts - {a.city.title()}*", ""]
        for area in areas:
            items = sorted(by_area.get(area, []), key=lambda r: -expnum(r))
            if not items:
                continue
            wa.append(f"*{area.replace('-', ' ').upper()}*")
            for r in items:
                yrs = f" ({r['exp']}y)" if r["exp"] else ""
                wa.append(f"{r['name']}{yrs} - +91{r['phone']}")
            wa.append("")
        wa.append("_Numbers from SquareYards directory, not individually "
                  "verified - some may be stale._")
        Path(f"{a.out}_whatsapp.txt").write_text("\n".join(wa))
        print(f"wrote {a.out}_whatsapp.txt", file=sys.stderr)


if __name__ == "__main__":
    main()
