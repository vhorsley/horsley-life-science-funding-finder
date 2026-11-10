# Life Science Funding Finder

Grants, fellowships, career awards, pilot funds and student programs for Yale life scientists: cell and molecular biology, stem cells and regeneration, skin biology, immunology and fibrosis, cancer, neuroscience, genetics, microbiology, metabolism and aging, women's health, cardiovascular, computational, translational and ecological research.

## Use it

Live page: https://vhorsley.github.io/horsley-life-science-funding-finder/

`index.html` is a single file with all its data built in. Open it in a browser, or publish it with GitHub Pages (Settings → Pages → Deploy from branch → `main`, folder `/`).

Features:

- 17 research areas (cell and molecular biology, skin biology, autoimmunity and fibrosis, cancer, neuroscience, women's health and more), with optional topic and disease chips (e.g. lupus, diabetes, melanoma, Alzheimer's) and a box to hide programs open to every field
- filters by research area and career stage (pick one or more of each), eligibility (US-only, nomination or limited submission, career development awards), status, type and deadline window
- an **I'm at Yale** option (off by default) that adds Yale's own pilot funds and fellowships and shows Yale's internal and limited-submission steps next to each deadline. Link to `…/#yale` to open the page with it already on (e.g. `…/#yale-pd` for Yale postdocs)
- tips for each career stage and a "What's changed at funders" panel (NIH application cap, late-submission rules, discontinued programs)
- a **New** tag on programs added in the last 7 days (search for `new`)
- tick boxes to export the programs you care about as a calendar file (`.ics`, with reminders 6 and 4 weeks before each deadline) or a CSV
- per-program **Google Calendar**, **Outlook** and **Apple Calendar** links

## Data

`catalog/programs/*.json` is the source of truth, grouped by source (federal, postdoc, early-career faculty, established faculty and disease funders, students, Yale internal). `catalog/notes.json` holds the career-stage tips and the "What's changed" panel. `data/programs.json` is the whole catalog as one list, rebuilt by the build script.

Each program has these fields:

| Field | Meaning |
|---|---|
| `id` | Stable slug |
| `n`, `f`, `c` | Program name, funder, type |
| `s` | `open` (deadline posted), `rolling` (any time) or `watch` (recurs; next deadline not posted yet) |
| `d`, `dt` | Next funder deadline (ISO date or null) and a deadline note |
| `a`, `e`, `u` | Award, eligibility and notes, official link |
| `fields` | Research areas (`all` = every field): `cell`, `struct`, `stem`, `derm`, `imm`, `fib`, `cancer`, `neuro`, `gen`, `micro`, `metab`, `aging`, `repro`, `cardio`, `comp`, `trans`, `bioeng`, `eco` |
| `t` | Optional disease/topic tags shown as chips: `melanoma`, `blood-cancer`, `pancreatic`, `prostate`, `pediatric-cancer`, `lupus`, `scleroderma`, `psoriasis`, `arthritis`, `ibd`, `cf`, `alzheimers`, `parkinsons`, `mental-health`, `eye`, `diabetes`, `liver`, `menopause`, `pregnancy`, `plant`, `global-health`. New tags must be added to `TOPICS` in both `engine/build.py` and `engine/template.html` |
| `stages` | `ug`, `gr`, `pd`, `tt` (early-career faculty), `ten` (established faculty) |
| `us`, `nom` | US citizens/permanent residents only; needs nomination or limited submission |
| `cd` | Career development award (mentored or training-focused: K awards, CDAs, NSF CAREER and similar); the page can hide these |
| `yale` | Yale internal step `{d, t, u}` |
| `unv` | Anything that could not be confirmed on the funder's page |
| `added`, `checked` | Date added, date last checked |

## Suggest a program

Use the **Suggest a program** form on the page (it opens a GitHub issue labelled `suggestion`). The weekly recheck reads open suggestions, verifies them on the funder's page, adds or corrects the program, and closes the issue from the commit.

Yale internal calls that have no web page can be suggested by attaching the call PDF to the form. These are accepted only when the program is run by Yale and the PDF names the Yale office or contact person running it; PDFs for non-Yale programs are not accepted. An accepted PDF is saved in `calls/` (named after the program id), the row links to the copy on the site (`https://vhorsley.github.io/horsley-life-science-funding-finder/calls/<id>.pdf`), and the row's `unv` note says the details come from a submitted call document. Remove the row when the call closes unless a newer PDF or web page is sent in.

## Update it

1. Edit or add rows in `catalog/programs/`. Check every date on the funder's own page.
2. Run `python3 engine/build.py` (or `python3 engine/build.py --check` to validate without writing).
3. Commit `index.html`, `data/programs.json` and your catalog changes.

The build moves any program whose deadline has passed to **Watch** with no date, so stale dates never show as open. Deadlines move: check the funder's page before you commit to a date.

## Credits and license

Page design and the calendar/CSV export code are adapted from Chiara Mingarelli's [Funding Finders](https://github.com/ChiaraMingarelli/funding-finders) (MIT License). The code is released under the [MIT License](LICENSE). The catalog and page text are released under [CC BY 4.0](LICENSE-DATA). Not an official Yale University page.
