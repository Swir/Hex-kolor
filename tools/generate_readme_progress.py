from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "readme"

CARD = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180" role="img" aria-labelledby="title desc">
  <title id="title">HEX Color Tool product progress</title>
  <desc id="desc">Product roadmap progress is not available because this repository has no canonical measurable roadmap.</desc>
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient><pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" stroke="#62E5FF" stroke-opacity="0.06"/></pattern></defs>
  <rect x="1" y="1" width="1198" height="178" rx="24" fill="url(#bg)" stroke="#62E5FF" stroke-opacity="0.22"/><rect x="1" y="1" width="1198" height="178" rx="24" fill="url(#grid)"/>
  <text x="50" y="46" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="17" font-weight="700" letter-spacing="4">SWIR PROGRESS</text>
  <text x="50" y="82" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="31" font-weight="800">HEX COLOR TOOL</text>
  <text x="50" y="108" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="15">Scope: product roadmap · no canonical measurable checklist</text>
  <text x="1090" y="82" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="34" font-weight="800">N/A</text>
  <text x="1090" y="108" text-anchor="end" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="1.3">NO ROADMAP</text>
  <rect x="50" y="126" width="1100" height="24" rx="12" fill="#08131F" stroke="#62E5FF" stroke-opacity="0.14"/>
  <text x="50" y="169" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="13">Verified product completion is intentionally not estimated.</text>
</svg>
'''

MINI = '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="72" viewBox="0 0 900 72" role="img" aria-labelledby="title desc">
  <title id="title">HEX Color Tool roadmap progress</title><desc id="desc">Roadmap progress is N/A because no canonical measurable roadmap exists.</desc>
  <rect x="1" y="1" width="898" height="70" rx="18" fill="#02050A" stroke="#62E5FF" stroke-opacity="0.22"/>
  <text x="24" y="27" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="700" letter-spacing="2">PRODUCT ROADMAP</text>
  <text x="24" y="53" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="21" font-weight="800">N/A</text>
  <rect x="170" y="24" width="700" height="20" rx="10" fill="#08131F"/>
  <text x="870" y="59" text-anchor="end" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">No canonical checklist</text>
</svg>
'''

EXPECTED = {"progress-card.svg": CARD, "progress-mini.svg": MINI}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate/check SWIR README progress assets.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    template = ASSETS / "progress-template.svg"
    if not template.exists() or "TEMPLATE / NOT PROJECT DATA" not in template.read_text(encoding="utf-8"):
        print("progress-template.svg is missing or not clearly labelled")
        return 1
    stale = []
    for name, content in EXPECTED.items():
        path = ASSETS / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        print("Stale progress assets: " + ", ".join(stale))
        return 1
    print("Progress assets are current." if args.check else "Progress assets generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
