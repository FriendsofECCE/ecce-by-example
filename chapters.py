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
 ("workflows", "Workflows and recipes", "Workflows",
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
("Teaching", [
 # For teachers: calculations that show a classical discovery or a core
 # concept in a lecture. Not tied to any course; no course references.
 ("atomic-orbitals", "Atomic orbitals: radial distributions and slices", "General Chemistry > Atoms",
  "density-profile density-map", "Radial distribution|Atomic orbitals|Density Profile|Density Map|Nodes|Inner maxima"),
 ("periodic-trends", "The periodic table from calculation: configurations, shielding and ionisation", "General Chemistry > Atoms",
  "ecce-qm", "Periodic trends|Aufbau principle|Hund's rule|Electron configuration|Chromium|Copper|Effective nuclear charge|Ionisation energy|Electron affinity|Koopmans' theorem"),
 ("bond-formation", "The covalent bond: H2 from Heitler and London to the Morse curve", "General Chemistry > How a chemical bond forms",
  "", "Covalent bond|H2|Potential energy curve|Morse potential|ecce-morse|Bond energy|Heitler-London"),
 ("oxygen", "Why O2 is paramagnetic: molecular orbitals of the diatomics", "General Chemistry > Molecular orbitals of diatomics",
  "mo-diagram molecules-for-teaching", "MO diagram|Molecular orbitals|Bond order|Paramagnetism|O2|Antibonding orbitals"),
 ("symmetry-mos", "Symmetry builds the MO diagram: water, ammonia and borane", "Inorganic Chemistry",
  "", "Point groups|Symmetry-adapted linear combinations|SALC|Character tables|MO diagram|Water|Ammonia|Borane|Mulliken symbols"),
 ("methane", "Methane: four equivalent bonds, two ionisation energies", "Inorganic Chemistry",
  "", "Methane|Photoelectron spectroscopy|Valence bond theory|MO theory|t2 and a1 orbitals|Hybridisation"),
 ("vibrations-symmetry", "Group theory and vibrations: counting IR and Raman bands", "Spectroscopy",
  "", "Group theory|Normal modes|IR selection rules|Raman selection rules|Mutual exclusion|CO2|H2O|CH4|CCl4|Mode symmetry"),
 ("cft-lft", "Crystal field and ligand field theory: the octahedral complex", "Inorganic Chemistry",
  "", "Crystal field theory|Ligand field theory|d-orbital splitting|Octahedral complexes|Spectrochemical series|pi-donor|pi-acceptor|Colour of complexes|Laporte rule|Spin-allowed transitions"),
 ("shapes", "Molecular shapes, polarity and the dipole moment", "General Chemistry > VSEPR",
  "dipole-moment localised-orbitals", "VSEPR|Electron domains|Molecular shape|Dipole moment|Bond dipoles|Lone pairs|Hybridisation"),
 ("benzene", "Benzene: resonance, delocalisation and aromaticity", "Organic Chemistry > Bonding in hydrocarbons",
  "", "Benzene|Resonance|Kekule structures|Delocalisation|Aromaticity|pi orbitals|Huckel"),
 ("colour", "Colour from conjugation: polyenes and the particle in a box", "Spectroscopy",
  "", "Colour|Conjugation|Particle in a box|Polyenes|UV-vis|HOMO-LUMO gap"),
 ("greenhouse", "Why CO2 and H2O absorb infrared: vibrations and the greenhouse effect", "Spectroscopy > Small molecules",
  "", "Greenhouse effect|IR active modes|CO2|H2O|Dipole derivative|Vibrational modes"),
 ("hydrogen-bond", "The hydrogen bond: the water dimer, ice and the boiling point of water", "General Chemistry > Intermolecular interactions",
  "electron-density-views", "Hydrogen bond|Water dimer|Ice|Boiling point|Dispersion|Intermolecular interactions"),
 ("kinetic-theory", "Kinetic theory: Maxwell's distribution of speeds", "General Chemistry > Gases, liquids and solids",
  "md-speeds-and-diffusion", "Maxwell distribution|Speed distribution|Kinetic theory|Temperature|Molecular dynamics"),
 ("phases", "Gases, liquids and solids, and the change between them", "General Chemistry > Gases, liquids and solids",
  "gromacs-first-calculation", "Phase change|Melting|Evaporation|Ideal gas|Real gas|GROMACS|Ion-dipole interactions"),
 ("packing", "Packing spheres: metals and ionic crystals", "General Chemistry > Packing in solids",
  "qe-first-calculation", "Unit cell|Close packing|bcc|fcc|hcp|Coordination number|NaCl|CsCl"),
 ("solids", "Molecular, covalent and layered solids", "General Chemistry > Molecular and covalent solids",
  "", "Molecular crystals|Network solids|Diamond|Graphite|Ice|Dry ice"),
 ("bragg", "Bragg's law and the first crystal structures", "General Chemistry > Diffraction",
  "fibre-diffraction", "Bragg's law|Powder pattern|X-ray diffraction|NaCl|KCl|Precession photograph|Detector frame|Debye scattering"),
 ("dna-helix", "Photograph 51, the double helix and the alpha-helix", "General Chemistry > Diffraction",
  "", "DNA|Photograph 51|Double helix|alpha-helix|Fibre diffraction|Helical transform"),
 ("hf-dft", "What a calculation approximates: Hartree-Fock, DFT and Jacob's ladder", "Computational > H2 dissociation with RHF, UHF and CCSD",
  "", "Hartree-Fock|Density functional theory|Jacob's ladder|Electron correlation|Chemical accuracy|Model chemistry"),
 ("basis-sets", "Basis sets: from minimal to the complete basis set limit", "Getting Started",
  "", "Basis sets|Zeta|Polarisation functions|Diffuse functions|Complete basis set limit|Effective core potentials"),
 ("rhf-uhf", "Breaking a bond: restricted and unrestricted Hartree-Fock", "Computational > H2 dissociation with RHF, UHF and CCSD",
  "", "RHF|UHF|ROHF|Spin contamination|Bond dissociation|Static correlation"),
 ("equilibrium", "From Gibbs energy to the equilibrium constant", "Organic Chemistry > Reactions",
  "", "Equilibrium constant|Gibbs energy|Standard state|log K|Energy Calculator"),
 ("reaction-energy", "Energy in reactions: Hess's law, barriers and the Arrhenius equation", "Organic Chemistry > Reactions",
  "", "Hess's law|Reaction energy|Activation energy|Arrhenius equation|Transition state|SN2|Walden inversion"),
 ("acids-bases", "Acids and bases: where the proton goes", "Workflows > Aminopyridine protonation",
  "", "Protonation|Basicity|pKa|Acids and bases"),
]),
("Physical chemistry", [
 ("thermochemistry", "Thermochemistry and reaction energies", "Organic Chemistry > Reactions",
  "thermochemistry energy-calculator compare-energies", "Thermochemistry|Gibbs energy|Enthalpy|Energy Calculator|Compare Energies|Standard state|ecce-thermo"),
 ("reaction-rates", "Transition states, reaction paths and rates", "Workflows > SN2 Cl- and CH3Br",
  "", "Transition state|IRC|QST3|Rate constant|Tunnelling|Reaction overview|ecce-rate"),
 ("scans", "Potential energy scans and conformations", "Organic Chemistry > Conformations",
  "", "Scan|Torsion|Relaxed scan|Geometry Trace"),
 ("density-views", "Looking at electron densities", "Getting Started",
  "", "Electrostatic potential|ELF|NCI|Isosurface|Surfaces|Density difference"),
]),
("Spectroscopy", [
 ("vibrations", "IR and Raman spectra", "Spectroscopy",
  "mode-composition match-bands displacement", "IR spectrum|Raman spectrum|Vibrations|Mode composition|Match bands|Displacement"),
 ("ir-experiment", "Comparing spectra with experiment", "Spectroscopy > Sulfate coordination",
  "ir-spectrum-difference-experiment", "Experimental spectrum|Difference spectrum|Scaling factors"),
 ("excited-states", "Electronic excitations", "Spectroscopy",
  "", "TD-DFT|UV-vis|Excited states"),
]),
("Organic chemistry", [
 ("crest", "Conformers with CREST", "Workflows > Aminopyridine protonation",
  "crest", "CREST|Conformers|Ensembles|ecce-ensemble|Topology check"),
 ("xtb", "Fast calculations with xTB", "Getting Started",
  "xtb", "xTB|GFN2-xTB|GFN-FF|Semiempirical methods"),
 ("protonation", "Protonation sites and pKa", "Workflows > Aminopyridine protonation",
  "", "Protonation|pKa|Solvation|CPCM"),
]),
("Inorganic chemistry", [
 ("organometallics", "Organometallic and coordination compounds", "Inorganic Chemistry",
  "organometallics", "Organometallics|Ligand field|Coordination compounds|Spin states"),
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
 ("biofibres", "Fibre patterns of biomolecules", "General Chemistry > Diffraction",
  "", "B-DNA|A-DNA|alpha-helix|Coiled coil|beta-sheet|Collagen|Amyloid"),
]),
("Materials chemistry", [
 ("qe-settings", "Periodic DFT with Quantum ESPRESSO", "General Chemistry > Packing in solids",
  "qe-choosing-settings", "Quantum ESPRESSO|k-points|Cutoff|Pseudopotentials|vc-relax"),
 ("cp2k", "CP2K", "Getting Started",
  "cp2k-scf cp2k-basis-potential", "CP2K|GTH pseudopotentials|SCF convergence"),
 ("mlp", "Machine-learned potentials (MACE)", "Materials Chemistry",
  "mlp", "MACE|Machine-learned potentials|ML potential|Site screening"),
 ("clays", "Clay minerals: layers, interlayer water and MINFF", "Materials Chemistry > Clays",
  "layer-builder gromacs-prepare", "Layer builder|Clay minerals|MINFF|atomipy|Interlayer|Basal spacing|Isomorphic substitution|Montmorillonite"),
 ("stress", "Stress and cell relaxation", "Materials Chemistry",
  "", "Stress tensor|Pressure|Cell relaxation"),
]),
# Reference appendices: every menu item and setting, kept current with ECCE.
# The 6th field lists ECCE source paths whose menus/settings the appendix
# describes; chapters.py check reports ECCE commits to them since \checkedwith.
("Appendices", [
 ("menus-organizer", "Organizer menus and settings", "",
  "organizer-menus", "Organizer!menus|Organizer!Preferences",
  "src/apps/organizer"),
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
STUB = r"""\chapter{%(title)s}
\label{ch:%(file)s}
%(index)s
%(exline)s
%(help)s
\XXX[ chapter to be written]

\section{Background}

\section{What ECCE shows}

\section{Procedure}

\section{Results}

"""
def main():
    os.makedirs(os.path.join(HERE, "chapters"), exist_ok=True)
    lines = []
    for part, chapters in PLAN:
        if part == "Appendices":
            lines.append("\\appendix")
        lines.append("\\part{%s}" % part)
        for f, title, ex, helps, terms, *src in chapters:
            path = os.path.join(HERE, "chapters", f + ".tex")
            if not os.path.exists(path):
                idx = "\n".join("\\index{%s}" % chemify(t, True) for t in terms.split("|") if t)
                hp = "\n".join("\\helppage{%s}" % h for h in helps.split())
                if src:
                    hp += "\n\\eccesource{%s}" % src[0]
                with open(path, "w") as out:
                    out.write(STUB % dict(title=chemify(title), file=f, exline=('\\eccexample{Examples > %s}' % ex) if ex else '', index=idx, help=hp))
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
        src = re.search(r"\\eccesource\{([^}]+)\}", text)
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
