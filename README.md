# ECCE by Example

Worked calculations that show what ECCE does.
LaTeX in the Legrand Orange Book layout.

**Rules:** the book never refers to lectures, courses or lab numbers, and chapters have no "Try this" section.

- Build: `make` (lualatex, makeindex, bibtex). `make clean` removes the aux files.
- One chapter per file in `chapters/`, from `chapters/TEMPLATE.tex`; figures in `figures/<chapter>/`.
- Screenshots come from ECCE's headless shot tools (tools/screenshots, tests/apps hooks) so they can be regenerated for each release; the release the book shows is `\ecceversion` in `ecce-macros.tex`.
- Writing: the author's style guide (kept outside the repository); `\XXX` marks any fact not yet checked.
- Licence: CC BY-NC-SA 4.0 (text and figures), ECL-2.0 (build scripts); see LICENSE.

## Chapter plan and coverage
- `chapters.py` holds the plan (parts, chapters, the example each uses, the help pages it demonstrates, its index terms) and writes `chapters/plan.tex` and a stub for each new chapter. `make plan` regenerates; existing chapter files are never overwritten.
- `make check` lists ECCE help pages that no chapter demonstrates (`\helppage{}` in a chapter). Every capability must be shown somewhere: when ECCE gains a help page, the check fails until a chapter covers it.

## Index
The index is how readers find things, so index generously, in the text where the thing is explained:
- every menu item and control by its name: `\index{Diffraction!Options...}`, and under its menu: `\index{Tools menu!Diffraction...}`;
- every command under Commands: `\index{Commands!ecce-xrd}`;
- every concept, with the everyday word as well as the technical one: `\index{Radial distribution}`, `\index{Orbitals!radial distribution|see{Radial distribution}}`;
- every code under its name and under Codes: `\index{CREST}`, `\index{Codes!CREST}`;
- a task as the reader would phrase it: `\index{Docking a ligand}`, `\index{Comparing with experiment}`.

## Repository
github.com/FriendsofECCE/ecce-by-example. Figures named `.ecce-unknown` are placeholders to be retaken from ECCE. Each chapter job ends with a commit and `git push`. Material that is not the book (style guides, sources, course material) is never added.

## Versions: figures and text
- **Figures** are named `<name>.ecce-<version>.<ext>` (e.g. `rdf-argon.ecce-9.5.2.png`; `.ecce-unknown` for anything whose ECCE version is not known, which must be retaken) and listed in `figures/MANIFEST.tsv`: file, ECCE version, ECCE commit, kind (screenshot / plot from ECCE data / drawing), how it was made (the script or test hook command, so it can be remade), date.
- **Chapters** carry `\checkedwith{<ECCE version>}{<ECCE commit>}` under the title: the release and commit the menus, steps and numbers were checked against (printed small under the title).
- **`make check`** reports figures from an older ECCE than the book shows (`\ecceversion`), unknown-version figures, unnamed or unlisted figures, chapters without `\checkedwith`, and **every chapter whose ECCE help pages changed since its check** (git log of the ECCE repository from the chapter's commit), so changed functionality is found and the chapter re-checked.
