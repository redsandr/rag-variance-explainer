# Website design

## Purpose and structure

The static website explains a local SEC filing research prototype to independent analysts. It is not a hosted analysis service. The homepage shows the use case and its evidence boundary before the implementation. `/example` offers a visitor-controlled, illustrative workpaper. `/method`, `/install`, `/about`, and `/contact` provide focused reading paths. The FAQ remains on `/`.

## Visual direction

- Default to charcoal `#121310`, off-white `#f6f3e9`, and pale gold `#ead2a0`. Gold marks actions, selected stages, and evidence labels. A visitor can choose paper mode with background `#f5f2e9`, ink `#20231d`, and darker gold `#785323`.
- Use a restrained floating navigation, broad editorial headings, quiet rules, and research-paper surfaces. The first viewport pairs the analyst benefit with an illustrative workpaper that visibly withholds unreviewed results.
- Supporting pages use the same navigation and palette but prioritize reading. A warm contrasting band distinguishes evidence limits and setup requirements from surrounding sections.

## Behavior

- The shared theme control stores the preference locally and applies it before paint when browser storage is available. The navigation becomes a menu at widths below 1130 px. Escape closes the menu and restores focus to its trigger.
- The four example stages move only when the visitor selects a stage or uses the previous or next control. The selected stage highlights the relevant field on the workpaper. Reduced motion removes spatial transitions; no analysis starts automatically.
- `/install` switches between Windows PowerShell and macOS or Linux commands and reports the result of copying commands. FAQ rows use native disclosure controls.
- The site is statically exported. `landing/vercel.json` maps clean page URLs to the exported HTML files on Vercel. A case request opens a public GitHub issue, not a contact form. No signup, hosted query, or automatic case publication is promised.

## Evidence rule

The sample workpaper is a process illustration, not an SEC answer. No SEC quote, page reference, financial conclusion, numerical claim, or verification badge is published as evidence before a complete case is checked against its original filing. A quote match establishes that words occur in a retrieved passage. It does not verify causation or arithmetic. The method page explains the release gates.
