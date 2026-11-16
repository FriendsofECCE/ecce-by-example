#!/usr/bin/env python3
"""The book's chapter plan: writes a stub for each chapter that does not exist
yet and the part/chapter list chapters/plan.tex; 'check' lists ECCE help pages
no chapter covers (every capability must be demonstrated somewhere)."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
HELP = os.path.expanduser("~/tmp/ecce/ECCE/help/src")
# part -> [(file, title, example, help pages, index terms)]
PLAN = [
("Getting started", [
 ("first-calculation", "Your first calculation: water", "Getting Started > ecceqm-water",
  "first-calculation example-calculations viewer-panels run-states",
  "Builder|Calculation Editor|Launcher|Viewer|ECCE-QM|ORCA|Run states|Properties list"),
 ("organizer", "Organising calculations", "Getting Started",
  "organizer-menus rename-and-move checks-table reparse-outputs excluded",
  "Organizer|Projects|Annotations|Move to...|Copy to...|Checks table|Re-Parse Outputs|Excluded calculations"),
 ("machines", "Running on this computer", "Getting Started",
  "machines running-codes-on-linux running-codes-on-macos running-codes-on-windows",
  "Machines!this computer|localhost|Launcher|Run states|Codes!installing"),
 ("hpc", "Running on clusters and supercomputers", "",
  "register-machines allocations launch-selected reconnect-selected",
  "HPC|Clusters|Supercomputers|Register Machines|Queues|Slurm|PBS|HTCondor|Allocations|Projects (accounts)|ssh|ssh keys|Two-factor authentication|Scratch|Job scripts|Modules (environment modules)|Launch Selected|Reconnect|ecce-launch|ecce-reconnect|Moving a job to another machine"),
 ("code-registration", "Registering codes: programs, environments and new codes", "",
  "",
  "Code registration|Registering a code|Codes!environment variables|Codes!job script|EDML|Parsers|Input generators|Adding a new code|Pseudopotential paths"),
 ("structures", "Building and importing structures", "Getting Started",
  "importing-a-structure importing-a-calculation bonds-and-clean constraints-and-dummy-atoms",
  "Builder!import|Structure Library|SMILES|Add from SMILES|Replace Group|Clean|Constraints|Dummy atoms|Importing calculations"),
 ("scripting", "ECCE from scripts and AI assistants", "Getting Started",
  "scripting-and-ai new-series",
  "Command line|AGENTS.md|ecce-rerun|ecce-reparse|Series of calculations|AI assistants"),
]),
("Methods", [
 ("coupling", "Coupling computations: screening, refinement and hand-offs between codes", "Getting Started",
  "", "Coupling computations|New from This|Screening|Refinement|Hand-offs between codes"),
 ("ai-project", "A project done with an AI assistant, from method choice to Supporting Information", "",
  "", "AI assistants|Claude Code|AGENTS.md|ECCE skill|Method choice|Series of calculations|Tables of results|Supporting Information"),
 ("workflows", "Workflows and recipes: when to automate a chain", "Workflows",
  "workflows recipes writing-a-recipe", "Workflows|Recipes|Auto-run|Launch Ready Steps|Writing a recipe|ecce-workflow"),
 ("qsar", "QSAR: descriptors, PCA and PLS", "QSAR",
  "qsar-table qsar-analysis batch-from-smiles", "QSAR|Descriptors|PCA|PLS|Batch Add from SMILES|ecce-qsar"),
 ("ecce-qm", "ECCE-QM, the built-in quantum chemistry program", "Getting Started > ecceqm-water",
  "ecce-qm ecce-qm-files", "ECCE-QM|Analytic Hessian|D3 dispersion"),
 ("methods-choice", "Choosing methods and checking inputs", "Getting Started",
  "orca-composite-methods", "Composite methods|r2SCAN-3c|Verify|Input checks"),
 ("results", "Results, reports and citations", "Getting Started",
  "results-file-format si-export citing-ecce", "results.h5|Supporting Information|Citing ECCE|Export"),
]),
("Physical chemistry", [
 ("thermochemistry", "Thermochemistry: optimisation, frequencies and high-level single points", "Organic Chemistry > Reactions",
  "thermochemistry energy-calculator compare-energies", "Thermochemistry|Enthalpy|Gibbs energy|Zero-point energy|Energy calculator|Single point"),
 ("reaction-rates", "Transition states, reaction paths and rate constants", "Workflows > SN2 Cl- and CH3Br",
  "", "Transition state|IRC|QST2|QST3|Eyring equation|Rate constant|Imaginary frequency"),
 ("scans", "Potential energy scans and conformations", "Organic Chemistry > Conformations",
  "", "Potential energy scan|Relaxed scan|Conformations|Torsion"),
 ("bond-dissociation", "Bond dissociation: RHF, UHF and CCSD", "Computational > H2 dissociation with RHF, UHF and CCSD",
  "", "Bond dissociation|RHF|UHF|CCSD|Spin contamination|Static correlation"),
 ("basis-sets", "Convergence with basis set and method", "Getting Started",
  "", "Basis sets|Complete basis set limit|Jacob's ladder|Method convergence"),
 ("density-views", "Electron densities, orbitals and dipole moments", "Getting Started",
  "density-profile density-map electron-density-views localised-orbitals dipole-moment",
  "Electron density|Density map|Density profile|Localised orbitals|Dipole moment|Isosurfaces"),
 ("mo-analysis", "Molecular orbital diagrams from a calculation", "Inorganic Chemistry",
  "mo-diagram", "MO diagram|Molecular orbitals|Orbital symmetry|Bond order"),
]),
("Spectroscopy and spectrometry", [
 ("vibrations", "IR and Raman spectra and mode symmetry", "Spectroscopy",
  "mode-composition match-bands displacement", "IR spectrum|Raman spectrum|Normal modes|Mode symmetry|Scaling factors"),
 ("ir-experiment", "Comparing spectra with experiment", "Spectroscopy > Sulfate coordination",
  "ir-spectrum-difference-experiment", "Experimental spectra|Difference spectrum|Band assignment"),
 ("excited-states", "Electronic excitations and UV-vis spectra", "Spectroscopy",
  "", "TD-DFT|Excited states|UV-vis spectrum|Oscillator strength"),
 ("nmr", "NMR shielding and chemical shifts", "",
  "", "NMR|Chemical shift|Shielding tensor|GIAO"),
 ("epr", "EPR parameters: g-tensors and hyperfine couplings", "",
  "", "EPR|g-tensor|Hyperfine coupling|Spin density"),
]),
("Organic chemistry", [
 ("crest", "Conformer searches with CREST: from one structure to a refined ensemble", "Workflows > Aminopyridine protonation",
  "crest", "CREST|Conformer search|Boltzmann weights|Coupled codes"),
 ("xtb", "Fast calculations with xTB", "Getting Started",
  "xtb", "xTB|GFN2-xTB|GFN-FF|Semiempirical methods"),
 ("protonation", "Protonation sites and pKa: CREST, xTB and ORCA in one workflow", "Workflows > Aminopyridine protonation",
  "", "Protonation|pKa|Solvation|CPCM|Workflows"),
]),
("Inorganic chemistry", [
 ("organometallics", "Organometallic and coordination compounds: geometries and spin states", "Inorganic Chemistry",
  "organometallics", "Organometallics|Coordination compounds|Spin states|Broken symmetry"),
 ("ligand-field", "Ligand field splitting from a calculation", "Inorganic Chemistry",
  "", "Ligand field|Crystal field|d-orbital splitting|Octahedral complexes"),
 ("pom-solvation", "A polyoxometalate in water: explicit water molecules and counter ions", "Inorganic Chemistry",
  "recipes", "Polyoxometalates|Explicit solvation|Counter ions|Solvation shell|CREST!QCG|Microsolvation"),
 ("fragment-orbitals", "Fragment orbitals, DOS and OPDOS", "Inorganic Chemistry",
  "density-of-states-opdos", "Fragment orbitals|Density of states|OPDOS|ecce-fragorb|Interaction diagram"),
]),
("Biochemistry", [
 ("docking", "Docking a ligand with AutoDock Vina", "Biochemistry",
  "vina", "Docking|AutoDock Vina|PDBQT|Docking box|Poses|Select Protein|Select Ligand"),
 ("umbrella", "Free energy profiles by umbrella sampling", "Biochemistry",
  "umbrella-sampling gromacs-prepare gromacs-md-settings", "Umbrella sampling|PMF|WHAM|Pull force|ecce-umbrella"),
 ("protein-md", "Analysing a protein simulation", "Computational > GROMACS",
  "md-analysis", "MD Analysis|RDF|RMSD|Radius of gyration|Hydrogen bonds|ecce-gmxanalysis"),
]),
("Materials chemistry", [
 ("crystals", "Crystal structures: building, CIF import and periodic models", "General Chemistry > Packing in solids",
  "qe-first-calculation", "Crystal structures|CIF|Unit cell|Supercell|Periodic models"),
 ("liquids", "Liquids by MD: density, diffusion and structure", "General Chemistry > Gases, liquids and solids",
  "gromacs-first-calculation md-speeds-and-diffusion", "GROMACS|Liquids|Diffusion coefficient|RDF|Density"),
 ("diffraction", "Powder, single-crystal and fibre diffraction from a model", "General Chemistry > Diffraction",
  "fibre-diffraction", "Powder pattern|Single crystal|Precession photograph|Detector frame|Fibre diffraction|Debye scattering"),
 ("qe-settings", "Periodic DFT with Quantum ESPRESSO", "General Chemistry > Packing in solids",
  "qe-choosing-settings", "Quantum ESPRESSO|k-points|Cutoff|Pseudopotentials|vc-relax"),
 ("cp2k", "Periodic structures in CP2K", "Getting Started",
  "cp2k-scf cp2k-basis-potential", "CP2K|GTH pseudopotentials|SCF convergence"),
 ("mlp", "Machine-learned potentials (MACE)", "Materials Chemistry",
  "mlp", "MACE|Machine-learned potentials|ML potential|Site screening"),
 ("clays", "Layered structures: building clay models and running them in GROMACS", "Materials Chemistry > Clays",
  "layer-builder gromacs-prepare", "Layer builder|Clay minerals|MINFF|atomipy|Interlayer|Basal spacing|Isomorphic substitution|Montmorillonite"),
 ("stress", "Stress and cell relaxation", "Materials Chemistry",
  "", "Stress tensor|Pressure|Cell relaxation"),
]),
# Reference appendices: every menu item and setting, kept current with ECCE.
# The 6th field lists ECCE source paths whose menus/settings the appendix
# describes; chapters.py check reports ECCE commits to them since \checkedwith.
("Teaching", [
 ("teaching", "Teaching with ECCE", "General Chemistry",
  "molecules-for-teaching", "Teaching|Example sets|Central server|ECCE-QM"),
]),
("Appendices", [
 ("menus-organizer", "Organizer menus and settings", "",
  "organizer-menus", "Organizer!menus|Organizer!Preferences",
  "src/apps/organizer data/client/config/ResourceDescriptor.xml src/wxgui/wxdialogs/GlobalPrefs.C"),
 ("menus-builder", "Builder and viewer menus and settings", "",
  "viewer-panels", "Builder!menus|Viewer!menus|Builder!Preferences|Properties list",
  "src/apps/builder src/wxviz data/client/config/PropertyPanelDescriptor.xml"),
 ("settings", "Settings files and environment variables", "",
  "", "Preferences|Environment variables|Settings files",
  "src/util/Preferences.C src/util/Ecce.C bin docs/AGENTS.md"),
]),

]

# Chemical formulas typeset with mhchem: \chem{H2} (ecce-macros.tex).
ELEMENTS = set("""H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni
Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr
Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn U""".split())
NOT_FORMULAS = {"CP2K", "SN2", "CO", "NO", "I", "In", "As", "At", "Be", "He", "No", "B", "C", "N", "O", "F", "S", "P", "K", "U", "V", "W", "Y"}
DIGITLESS = {"NaCl", "KCl", "CsCl", "HCl", "HF", "LiF", "CsF"}
TOKEN = re.compile(r"(?<![\w\\{@-])((?:[A-Z][a-z]?\d*)+)(?![\w}-])")
def is_formula(tok):
    if tok in NOT_FORMULAS:
        return False
    parts = re.findall(r"([A-Z][a-z]?)(\d*)", tok)
    if "".join(a + b for a, b in parts) != tok or not all(a in ELEMENTS for a, _ in parts):
        return False
    return tok in DIGITLESS or any(b for _, b in parts)
# Chemistry notation that is not a formula (sort key @ typeset form for the index).
NOTATION = [("SN2", r"S\textsubscript{N}2"), ("pKa", r"p\textit{K}\textsubscript{a}"),
            ("alpha-helix", r"$\alpha$-helix"), ("beta-sheet", r"$\beta$-sheet")]
def chemify(text, index=False):
    for plain, typeset in NOTATION:
        text = re.sub(r"(?<![\w@])%s(?![\w}])" % re.escape(plain),
                      lambda m: ("%s@%s" % (plain, typeset)) if index else typeset, text)
    def rep(m):
        t = m.group(1)
        if not is_formula(t):
            return t
        return "%s@\\chem{%s}" % (t, t) if index else "\\chem{%s}" % t
    return TOKEN.sub(rep, text)
# Running-header titles for long chapter titles (a long header runs into the page number).
SHORT = {"diffraction": "Diffraction from a model", "ai-project": "A project done with an AI assistant",
         "reaction-rates": "Transition states and rate constants", "organometallics": "Organometallic compounds"}
def short_title(f, title):
    return SHORT.get(f, title.split(":")[0])
PART_STUB = r"""%% Part overview, set before the part's first chapter.
\XXX[ part overview (chapter to be written): the kinds of calculations and projects
%(part)s research does (one paragraph each, e.g. what is computed and why),
and for each the ECCE route and the chapter that shows it (chapters %(chapters)s),
including where ECCE couples codes.]

"""
STUB = r"""\chapter{%(title)s}%(mark)s
\label{ch:%(file)s}
%(index)s
%(exline)s
%(help)s
\XXX[ chapter to be written]

\section{Background}

\section{What ECCE shows}

\section{Procedure}

\section{Results}

\section{Coupling with other codes}
%% What feeds this calculation (a cheaper screen, a structure from another code)
%% and what it feeds (refinement, a property from the code best at it); which
%% hand-off is made (usually by hand: a new calculation from this one's
%% structure or orbitals in another code); a workflow only where it pays.

"""
def main():
    os.makedirs(os.path.join(HERE, "chapters"), exist_ok=True)
    lines = []
    for part, chapters in PLAN:
        if part == "Appendices":
            lines.append("\\appendix")
        lines.append("\\part{%s}" % part)
        if part not in ("Getting started", "Methods", "Teaching", "Appendices"):
            # Part overview: the calculations and projects of the field and where the book covers them
            slug = "part-" + part.lower().replace(" ", "-")
            ppath = os.path.join(HERE, "chapters", slug + ".tex")
            if not os.path.exists(ppath):
                with open(ppath, "w") as out:
                    out.write(PART_STUB % dict(part=part, chapters=", ".join("\\ref{ch:%s}" % c[0] for c in chapters)))
            lines.append("\\input{chapters/%s}" % slug)
        for f, title, ex, helps, terms, *src in chapters:
            path = os.path.join(HERE, "chapters", f + ".tex")
            if not os.path.exists(path):
                idx = "\n".join("\\index{%s}" % chemify(t, True) for t in terms.split("|") if t)
                hp = "\n".join("\\helppage{%s}" % h for h in helps.split())
                if src:
                    hp += "\n\\eccesource{%s}" % src[0]
                with open(path, "w") as out:
                    out.write(STUB % dict(mark=("\n\\chaptermark{%s}" % chemify(short_title(f, title))) if len(title) > 50 else '', title=chemify(title), file=f, exline=('\\eccexample{Examples > %s}' % ex) if ex else '', index=idx, help=hp))
            lines.append("\\input{chapters/%s}" % f)
        lines.append("")
    with open(os.path.join(HERE, "chapters", "plan.tex"), "w") as out:
        out.write("% Written by chapters.py: edit the PLAN there, not this file.\n" + "\n".join(lines))
ECCE = os.path.expanduser("~/tmp/ecce/ECCE")
FIG_RE = re.compile(r"^[\w.-]+\.ecce-(\d+\.\d+\.\d+(?:-dev)?|unknown)\.(png|jpg|pdf)$")

def version_check():
    """Chapters and figures against the ECCE release the book shows: every
    figure is named <name>.ecce-<version>.<ext> and listed in
    figures/MANIFEST.tsv; every written chapter carries \\checkedwith; a
    chapter whose help pages changed in ECCE since its check is listed."""
    import subprocess
    current = re.search(r"\\newcommand\{\\ecceversion\}\{([^}]+)\}",
                        open(os.path.join(HERE, "ecce-macros.tex")).read()).group(1)
    manifest = {}
    mf = os.path.join(HERE, "figures", "MANIFEST.tsv")
    if os.path.exists(mf):
        for line in open(mf):
            if line.strip() and not line.startswith("#"):
                cols = line.rstrip("\n").split("\t")
                manifest[cols[0]] = cols
    bad = 0
    for f in sorted(os.listdir(os.path.join(HERE, "chapters"))):
        if not f.endswith(".tex") or f in ("TEMPLATE.tex", "plan.tex", "introduction.tex"):
            continue
        text = open(os.path.join(HERE, "chapters", f)).read()
        written = "chapter to be written" not in text
        for fig in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", text):
            name = os.path.basename(fig)
            m = FIG_RE.match(name)
            if not m:
                print("figure not named <name>.ecce-<version>.<ext>:", fig); bad += 1
            elif m.group(1) == "unknown":
                print("figure of unknown ECCE version (retake):", fig)
            elif m.group(1) != current:
                print("figure from ECCE %s, book shows %s:" % (m.group(1), current), fig)
            if fig not in manifest:
                print("figure missing from figures/MANIFEST.tsv:", fig); bad += 1
        if not written:
            continue
        plain = re.sub(r"\\(ce|chem|menu|ctrl|cmd|texttt|eccexample|helppage|label|ref|index|includegraphics|eccesource|checkedwith|cite\w*)(\[[^]]*\])?\{[^}]*\}(\{[^}]*\})?", "", text)
        plain = re.sub(r"\$[^$]*\$|%.*", "", plain)
        bare = sorted({t for t in TOKEN.findall(plain) if is_formula(t)})
        if bare:
            print("formulas not in \\ce/\\chem in %s: %s" % (f, " ".join(bare))); bad += 1
        cw = re.search(r"\\checkedwith\{([^}]+)\}\{([^}]+)\}", text)
        if not cw:
            print("chapter without \\checkedwith:", f); bad += 1
            continue
        if cw.group(1) not in (current,) and not cw.group(1).startswith(current.split("-")[0][:3]):
            print("chapter checked with ECCE %s, book shows %s:" % (cw.group(1), current), f)
        pages = re.findall(r"\\helppage\{([^}]+)\}", text)
        if pages and os.path.isdir(ECCE):
            log = subprocess.run(["git", "-C", ECCE, "log", "--oneline", cw.group(2) + "..origin/main", "--"]
                                 + ["help/src/%s.md" % p for p in pages],
                                 capture_output=True, text=True).stdout.strip()
            if log:
                print("ECCE help changed since %s was checked (%s):" % (f, cw.group(2)))
                for l in log.splitlines()[:8]: print("   ", l)
        srcpaths = " ".join(re.findall(r"\\eccesource\{([^}]+)\}", text))
        src = re.match(r"(.+)", srcpaths)
        if src and os.path.isdir(ECCE):
            log = subprocess.run(["git", "-C", ECCE, "log", "--oneline", cw.group(2) + "..origin/main", "--"]
                                 + src.group(1).split(), capture_output=True, text=True).stdout.strip()
            if log:
                n = len(log.splitlines())
                print("ECCE source changed since %s was checked (%s): %d commits, recheck" % (f, cw.group(2), n))
                for l in log.splitlines()[:8]: print("   ", l)
    return bad

def check():
    cover = set()
    for f in os.listdir(os.path.join(HERE, "chapters")):
        if f.endswith(".tex"):
            cover |= set(re.findall(r"\\helppage\{([^}]+)\}", open(os.path.join(HERE, "chapters", f)).read()))
    pages = {p[:-3] for p in os.listdir(HELP) if p.endswith(".md")} - {"index", "installation"}
    missing = sorted(pages - cover)
    print("help pages: %d, covered: %d" % (len(pages), len(pages & cover)))
    for m in missing: print("not covered:", m)
    return 1 if (missing or version_check()) else 0
if __name__ == "__main__":
    sys.exit(check() if sys.argv[1:] == ["check"] else main())
