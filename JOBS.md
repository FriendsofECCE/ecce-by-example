# Writing queue
PRINCIPLE (Andy 11-14, more important than any single example): show the reader how to use the fact that ECCE couples computations: MACE, CP2K, QE, xTB, CREST, ORCA, GROMACS, Vina... at their fingertips. Patterns: (1) screening funnel: a cheap method ranks many candidates, an expensive one refines the few (CREST -> xTB -> DFT; MACE -> QE/CP2K; Vina -> xTB/DFT rescoring); (2) multi-level: geometry at a lower level, energy or property at a higher one; (3) hand-offs across scales: QM charges/parameters -> MD, MD snapshots -> QM properties, periodic model -> cluster for a molecular code; (4) one structure, each property from the code best at it. Every chapter has a "Coupling with other codes" section. Coupling does NOT mean workflows (Andy 11-14): most hand-offs in this book are done by hand (a new calculation from a finished one's structure or orbitals, in another code; importing; cutting a cluster from a periodic model). Use a workflow or recipe only where automating the chain pays (e.g. CREST conformers -> xTB -> DFT, TS search -> IRC). The core chapter is "coupling" (first in Methods); "workflows" is a separate, smaller chapter on when to automate. For organic chemists CREST conformer searches are a game changer: the Organic part leads with them. Never show energy differences between methods (rule); coupling compares structures and ranks, not cross-method energies.
Voice (Andy 11-14): write in the COMPENDIUM voice, ../notes/compendium-voice.md (pedagogical "we", the reader as "you" now and then, why before what, active voice, prose not bullets, numbered lists only for steps, subordinate clauses instead of dashes); ../notes/voice-guide.md applies for facts and citations. "The user decides ...", not "... are choices of the user".
Every chapter opens with a "This requires" section (Andy 11-14): the programs its calculations need (e.g. xTB, CREST, ORCA), versions used, where to get them; "Nothing beyond ECCE" for ECCE-QM-only chapters.
Teaching chapter (Andy 11-14): use ECCE-QM where practical instead of ORCA, NWChem or G16, so a teacher needs no other code installed; the research chapters showcase all codes.
Audience (Andy 11-14): the book is for scientists doing research calculations in their field: each chapter shows how to do that field's computations in ECCE AND uses what ECCE adds (coupling codes, e.g. CREST -> xTB -> ORCA; workflows; building models; analysis). Only ONE chapter is about teaching. Example: a clay scientist looks up how to build layered structures and run them in GROMACS, or how to run periodic structures in CP2K. Each field part opens with an overview (chapters/part-*.tex): the kinds of calculations and projects done in that field, each with its ECCE route and chapter, so a biochemist or inorganic chemist sees at once what the field does in ECCE. Chapters should use what is unique to ECCE where it helps (Andy: e.g. an inorganic chemist adding water molecules and counter ions to a small polyoxometalate: CREST solvation shell -> xTB -> DFT via the Solvation shell recipe). If ECCE cannot yet do a step the field needs (e.g. placing counter ions), file an ECCE issue and say so in the report; never fake it.
Existing calculations OK to use: the nylon-6,10 (alpha, gamma), quartz and cellulose periodic CP2K runs in the local ECCE tree: neutral names and descriptions only (polymer and silica crystals); never connect them to battery separators, electrolytes or ions; ion-binding runs stay out (Andy 11-14).
Calculations: EVERY calculation run for the book is kept in calculations/<chapter>/<code>-<name>/ (inputs, outputs, NOTES.txt) with a row in calculations/CATALOG.tsv (see calculations/README.md); most will become ECCE examples in their categories (Andy 11-14). Copy them off the offload host before its isolated HOME is removed.
Screenshots: every chapter has screenshots of the real ECCE views it describes (Andy 11-14), taken headless with the test machinery from that chapter's own calculations, named <name>.ecce-<version>.png and listed in figures/MANIFEST.tsv; the 3-D viewer on a WHITE background (Builder script command `background 1 1 1` before the shot; Andy).
Chemistry typesetting: formulas always \chem{H2O} (mhchem; plain in bookmarks), ions \ce{Cl-}, S\textsubscript{N}2, p\textit{K}\textsubscript{a}, Greek letters as symbols, units with a thin space. ECCE's own menu text (\menu, \eccexample) stays as ECCE shows it. `make check` reports bare formulas.
Versions: every chapter and appendix carries \checkedwith; when ECCE is updated, run `make check` and recheck what it lists (help pages or, for the appendices, \eccesource paths changed since the check) before the book shows the new version.
Agents never write the final chapter text (Andy 11-14): an agent job runs the calculations, takes the screenshots and writes facts/notes (calculations/<chapter>/NOTES.txt); the lead writes the chapter. One chapter per agent job; 1-2 chapters after every 2-3 ECCE tickets (Andy 11-14: ECCE still changes a lot; do not over-prioritise the book). Each job: run the chapter's calculation headless (isolated HOME, test machinery, NOT on niobium), take the screenshots, write the chapter to the voice guide, index it, `make` and `make check`, tick it here.

PRIORITY NOW (Andy 11-15): manual work focuses on the material of the TEACHING LABS (5KE176 spring course). The lab content goes into the DISCIPLINE chapters where its calculations belong (the Teaching part is for teachers only; Andy 11-15), done by hand step by step (New from This > Continue from Last Geometry / Continue in Another Code, set up, launch, check, analyse), no workflows in these sections. QM in ORCA, MD in GROMACS; for the book on the offload hosts (NerdEgg/radium; >12 h -> Kebnekaise through Andy's ECCE session only). Every ECCE gap a lab step hits becomes an issue (parity with GaussView/SAMSON, no more).

WAITING FOR ECCE (Andy 11-20): a chapter whose central step ECCE cannot do yet waits for that feature instead of being written around the gap. Check the issue before starting the chapter; when it closes, the chapter can go ahead.
- protein-md: RMSF (and the RMSD/hydrogen-bond tools of the issue) -- ECCE #822.
- ligand-field: a proper ligand-field diagram for ML6 (sigma-only, pi-donor, pi-acceptor) -- ECCE #162.
- pom-solvation: CREST solvation shell (QCG) crashes with Debian's xtb 6.7.1 -- ECCE #758.
- organometallics (heavier metals): relativistic Hamiltonians (ZORA/DKH/X2C) -- ECCE #820; ECPs in ECCE-QM -- ECCE #1197.
- coarse-grained chapter (Materials): coarse-grained setup -- ECCE #1201; LAMMPS -- ECCE #1030.
- mass spectrometry (Spectroscopy part, to be decided): no ECCE route yet.

- [ ] L1a. scans (+ density-views): s-trans butadiene opt+freq, relaxed dihedral scan 36 x 10 deg (ORCA %geom Scan), dE-vs-angle plot/csv, freq at the ~100 deg maximum (one imaginary torsion), s-cis opt+freq; NBO charges (NBO 7) and HOMO/LUMO of s-cis butadiene and ethene -> density-views.
- [ ] L1b. reaction-rates: Diels-Alder butadiene + ethene: reactant complex with one atom numbering, cyclohexene product, TS (ORCA NEB-TS from reactant+product), one imaginary frequency, IRC both directions; thermochemistry profile dH, dS, dG (students subtract) -> thermochemistry section on reactions.
- [ ] L1c. density-views (H-bond complex: interaction energy, dipoles, distance/angle, density mapped with ESP) and vibrations (Raman of benzocaine vs cocaine; cost check first).
- [ ] L2. umbrella: 2BEG, gromos53a6+SPC, NaCl, EM, NPT with per-chain POSRES, COM pull, windows, gmx wham PMF; stages split when started.

- [ ] 1. teaching: the one chapter for teachers (example sets, teaching MO diagram, ECCE-QM in class, central server). Sections atomic-orbitals and periodic-trends are written.
- [ ] 1-srv. ON HOLD until development settles (Andy 11-16). teaching: setting up a central server for a class (Andy 11-16: "absolutely" needed; a chapter of its own in the Teaching part). Done for real, not from the docs: one server machine (data server + broker, ecce-broker.service) and student clients as separate Unix accounts (podman containers as in ECCE's tests/containers/central_server_test.py, on beryllium/NerdEgg, never niobium). Steps to record with exact commands and screenshots: install the server packages; create the teacher and student accounts (ecce-dataserver-adduser); firewall/ports; publish the class's example set; a student's first start (Start window, Connect to a server) on a client; launching a job on the department machine; what each user can and cannot see (passwords separate users; no claim that the teacher sees students' work unless shown); ending a session. Every ECCE gap found becomes an issue. Frame it as a course from the teacher's side (Andy 11-16 "in the context of teaching"): before the course (server set up, one account per student from a class list, the course's example set published, ECCE-QM jobs on the department machine so students need no other code); the first class (students install the client on their laptops, Windows/macOS/Linux, and connect); a class session (everyone opens the same example, runs a calculation, the queue on the department machine with 20-30 jobs at once); after the course (accounts and data removed or kept). Teacher-facing, not student lab instructions. Agent: facts, commands, screenshots in calculations/teaching-server/NOTES.txt; lead writes the chapter.
- [ ] 1a. frontispiece / title page: top two thirds one large ECCE figure (a real Density Map in the spirit of the ECCE logo, print-friendly colours); below the title block six small captioned panels of real ECCE views (orbital, IR/Raman spectrum, B-DNA fibre pattern, docked ligand, PMF, powder pattern); made headless, .ecce-<version>, in MANIFEST; mock-up to Andy first
- [x] 1b. appendix menus-organizer (12 \XXX gaps to fill from a running ECCE)
- [ ] 1c. appendix menus-builder
- [ ] 1d. appendix settings: preference files, per-user state, environment variables (from docs/AGENTS.md)
- [x] 1e. part overviews (chapters/part-*.tex), one job for all six fields
- [x] 1f. coupling (core chapter: coupling computations, mostly by hand)
- [ ] 1f2. ai-project: one small research project from beginning to end, done by talking to an AI assistant (Claude Code with ECCE's AGENTS.md/ECCE skill), in this order: (1) deciding on the method (benchmark/literature reasoning, a small test of method and basis, the assistant's proposal and the scientist's decision); (2) setting up the structures (build/import, conformers with CREST where it fits); (3) the calculations (series, launch on a machine, monitoring, failures and reruns); (4) tabulating the results (energies/properties table in ECCE, export); (5) the Supporting Information (SI export: coordinates, energies, methods text, citations). Show the prompts, what the assistant did in ECCE, what the scientist checked in the GUI, and where the assistant needed correcting. Real calculations (offload hosts), real transcript excerpts, results visible in the Organizer.
- [x] 1g. crest (organic lead chapter)
- [ ] 1h. PDF in the repo (Andy 11-14): commit main.pdf (built by make) and keep it current after each chapter; within the next ~10 tickets, no hurry
- [ ] 2. hpc
- [ ] 3. code-registration
- [ ] 4. clays
- [x] 5. cp2k
- [ ] 5a. pom-solvation
- [ ] 7. protonation
- [x] 9. first-calculation
- [ ] 10. organizer
- [ ] 11. machines
- [ ] 12. structures
- [ ] 13. scripting
- [ ] 14. qsar
- [ ] 15. ecce-qm
- [ ] 16. methods-choice
- [ ] 17. results
- [x] 18. thermochemistry
- [ ] 19. reaction-rates
- [ ] 20. scans
- [ ] 21. bond-dissociation
- [ ] 22. basis-sets
- [ ] 23. density-views
- [ ] 24. mo-analysis
- [x] 25. vibrations
- [ ] 26. ir-experiment
- [ ] 27. excited-states
- [x] 28. xtb
- [ ] 29. organometallics
- [ ] 30. ligand-field
- [ ] 31. fragment-orbitals
- [ ] 32. docking
- [ ] 33. umbrella
- [ ] 34. protein-md
- [ ] 35. biofibres
- [ ] 36. crystals
- [ ] 37. liquids
- [ ] 38. diffraction
- [ ] 39. qe-settings
- [ ] 40. mlp
- [ ] 41. stress
