# Reader's audit, 2026-11-14 (no chapter edits)

Chapters: coupling.tex, crest.tex, teaching-atomic-orbitals.tex,
teaching-periodic-trends.tex (as of 87187c9).

Categories:
- **(1)** a number is stated, but the reader is not shown how to get it in ECCE.
- **(2)** a step is not a GUI step.
- **(3)** a term is used before it is defined.
- **(4)** a figure was made outside ECCE.

Each entry gives the missing fact where I found it, marked in one of three ways:
- **VERIFIED**: read off the calculation files or the ECCE source/help.
- **NOT VERIFIED**: inferred, needs a check.
- **ARITH**: checked by arithmetic only.

Constant used throughout: 1 hartree = 27.2114 eV = 627.51 kcal/mol = 2625.5 kJ/mol.

## coupling.tex

- **L84 (1)** "21 conformers in four minutes".
  - Missing: where the count and the run time are read.
  - The count is the number of rows in the Conformers panel.
  - The run time is the ETIME property, or the job log. Which Organizer column shows it is NOT VERIFIED.
- **L93, L120 (1)** The timings ("under a minute", "one to two minutes", "six minutes") have the same gap.
  - VERIFIED from the calculation NOTES: 34 s per xTB run, 33–102 s per ORCA single point, 341 s for the ORCA optimisation.
- **L98–115 (1)** Table coupling-rank: the GFN2-xTB and r2SCAN-3c relative energies.
  - Not said: where to read them, or the unit conversion. The Conformers panel gives kcal/mol for the GFN-FF column only.
  - For the other two columns: select the eight xTB calculations (then the eight ORCA ones) and right-click > Compare Energies.... This lists dE relative to the lowest, but in kJ/mol and eV, not kcal/mol (help compare-energies, VERIFIED). So the reader must divide kJ/mol by 4.184.
  - Alternatively, the book could print kJ/mol.
  - Compare Energies refuses to mix methods, which fits the rule in L46.
  - The ranks follow from sorting.
- **L120 (1)** "heavy atoms moved by 0.096 Å (RMSD)".
  - Not said: how to get it in ECCE.
  - Route: Builder on the ORCA optimisation, Geometry Trace > Displacement > Compare with... the xTB calculation. This gives the aligned RMSD after a rotation and shift fit (help displacement, VERIFIED).
  - That RMSD is over all atoms. Whether the panel can restrict it to heavy atoms ("Looking at part of the structure" section) is NOT VERIFIED.
  - The 0.096 may not be reproducible in the GUI as stated.
- **L120 (1)** C=O 1.201→1.209 Å, C–O 1.340→1.357 Å, O–H 0.971 Å.
  - Missing: the procedure and the atom numbers.
  - Procedure: select the two atoms first, then Measure > Distance. With nothing selected ECCE says "Select two atoms to create a distance measure." (seen in a running Builder, 2026-11-14).
  - Atom numbers: not given in the text, NOT VERIFIED.
- **L56, L72 (3)** "heavy-atom RMSD after a fit" is used without explanation. RMSD is first explained nowhere in these chapters.
- **L72–73 vs the calculations (2)** Different tools were used for the stored run:
  - Selection: the eight conformers were picked with the command-line `ecce-ensemble pick n=8` at heavy-atom RMSD 0.5 Å (calculations/coupling/03-*/NOTES.txt, VERIFIED), not with Select Distinct... (which is not in a release yet, \XXX at L56).
  - Setup: the steps "were not done in the windows" (L133).
  - The text says this honestly. But until Select Distinct... exists, step 4 cannot be done in the GUI as written.
- **L127 (1)** Geometry Trace "energy relative to the first": fine, it is read off the panel.
- **L46 (3)** "never subtract an energy from one method from another" is fine.

## crest.tex

- **L48 (3)** "Boltzmann population at 298.15 K" has no formula.
  - VERIFIED against the stored ensemble: p_i = exp(−ΔE_i/RT) / Σ_j exp(−ΔE_j/RT), with RT = 0.5925 kcal/mol, over all 16 conformers, with no degeneracy weights.
  - Example: rank 2, ΔE 0.373 → 26.0 %.
- **L61 (1)** "40 s", "three minutes": same gap as for coupling (where the time is read). The numbers are VERIFIED from the calculation NOTES (40 s; 193 s and 201 s).
- **L61, table crest-gas (1)** τ and d "we measured on the stored structures".
  - Missing: how, in ECCE.
  - Fact (VERIFIED from crest_conformers.xyz, atom order of the SMILES COCCO plus H):
    - τ is O2–C3–C4–O5.
    - d is H13···O2.
    - H13 is the hydroxyl hydrogen on O5.
  - All eight rows reproduce exactly from the file (τ 63, −58, 172, −82, 178, 169, 45, −96; d 2.40 … 3.11).
  - In ECCE, for each row:
    1. Click the row in the Conformers panel.
    2. Select atoms 2, 3, 4, 5, then Measure > Torsion.
    3. Select atoms 13 and 2, then Measure > Distance.
  - That this works in the Conformers view is NOT VERIFIED; the Measure order is VERIFIED.
  - Whether the Conformers panel can show τ/d as columns (ecce-contacts patterns, #682) is NOT VERIFIED.
- **L83 (1, 3)** "77 %" (hydrogen-bonded) and "15 %" (anti) are sums over criteria the text never states.
  - VERIFIED from the file: 77 % is the sum over conformers with d < 2.7 Å (ranks 1, 2, 7), and 15 % the sum over |τ| > 150° (ranks 3, 5, 6 plus small ones).
  - The text should give the two cut-offs.
- **L85 (1)** Water: "16 conformers", "50 %", "29 %".
  - No water table is shown, so the reader cannot check.
  - VERIFIED with the same criteria on 03-crest-methoxyethanol-water: 16 conformers, d < 2.7 Å → 50 %, |τ| > 150° → 29 %.
  - Lowest conformer in water: τ −68°, d 2.53 Å.
- **L88 (1)** "Re-optimising rank 1 … did not move it": no number or route is given.
  - Route: Geometry Trace > Displacement on 04-xtb-methoxyethanol-rank1 (max/rms per atom), or Compare with... the CREST calculation.
  - NOT VERIFIED: no number recorded in calculations/crest/04-*/NOTES.txt. Get the RMSD.
- **L92 (1)** "the eight … carry 96 %": ARITH, the sum of the table's eight populations is 96.1 %.
- **L95 (2)** Run without the windows: stated in the text.

## teaching-atomic-orbitals.tex

- **L46 (1)** Orbital energies of Ar.
  - Missing: where they are read (MOs panel, column E (Hartree)). The column name is given in periodic-trends L131, not here.
  - VERIFIED from Ar.qmout: −115.117938, −11.141524, −8.692664 (×3), −0.967863, −0.425869 (×3).
- **L73 (1)** 1s maximum at 0.0299 Å: read from the note under the Density Profile plot (step 5 says so). Fine.
  - The comparison value 0.0294 Å = 0.529/18 is ARITH.
  - NOT VERIFIED: that the note prints 0.0299 for the current build. Figures are still .ecce-unknown (borrowed).
- **L38 (3)** "effective nuclear charge" is used here; it is defined only in periodic-trends L28. It has a cross-reference, so this is minor.
- **L78, 88, 97, 104 (4)** All four figures are .ecce-unknown ("borrowed", MANIFEST). They are ECCE views, but must be retaken from the Ar example.

## teaching-periodic-trends.tex

- **General (3)** No conversion factor between hartree and eV is given anywhere. Eight numbers depend on it: L76 "24 eV", L117 eV values, table pt-ie Koopmans and B3LYP columns, L189 relaxation. Add the constant, 1 hartree = 27.2114 eV.
- **L39 (3)** These terms are used without definition:
  - "correlation" (L39 is the first use);
  - "HOMO" (first use L39; never spelled out);
  - "ROKS" / restricted open-shell (L47; explained only in part at L112);
  - "UHF" / unrestricted (L48);
  - basis-set names (aug-cc-pVTZ etc.; acceptable to point to a basis-set chapter).
- **L76 (1)** "24 eV apart": ARITH, (1.459 − 0.572) × 27.2114 = 24.1 eV.
- **Table pt-config (1)** Every value is read from the MOs panel E (Hartree) of the Atoms topic, but the procedure only tells the reader to do it for Ne (step 2).
  - The "singly occupied first" values need the Occ # column. Steps 2–3 cover this partly.
- **L109 (1)** ⟨S²⟩ 2.000 / 3.750 / 12.000.
  - Missing: where it is read.
  - VERIFIED: ECCE-QM writes s_squared to the output (C.qmout line 32, "s_squared 2.000000000000") and stores it as property S2. In data/client/config/PropertyPanelDescriptor.xml, S2 is listed in the "Energies" property panel.
  - So: Properties > Energies. The label shown is NOT VERIFIED.
- **L117 (1, 4)** The Ca, Cr and Cu 4s/3d energies are given in eV, "averaged over each subshell".
  - The MOs panel gives single orbitals in hartree, so the reader must:
    1. pick out the 3d orbitals (by Compute, step 4);
    2. average them;
    3. convert to eV.
  - None of this is said.
- **L121, figure tm-levels (4)** Made by figures/periodic-trends/make_figures.py, not in ECCE.
  - The ECCE view nearest to it is the MO Diagram panel of each atom (Properties > MO Diagram), or the MOs panel list. That it shows 4s/3d/4p levels for one atom usefully is NOT VERIFIED.
  - The text does not tell the reader how to get a comparable view in ECCE.
- **L131–135 (1)** Zeff: fixed in c99a586. The values are VERIFIED from the outputs:

  | Calculation | Orbital | ε (hartree), output | Book |
  |---|---|---|---|
  | Li_HF | 2s (alpha) | −0.196355 | −0.1964 |
  | Ne_HF | 2p | −0.851213 | |
  | Na_HF | 3s (alpha) | −0.182201 | |

  - L135 "3.26 (Ar)" comes from the figure; Ar_HF 3p ε is not quoted. ARITH: implies ε ≈ −0.590.
- **L137, figure zeff (4)** Made by the python script. There is no ECCE view; the reader can only compute atom by atom (step 6). Say so, or present it as "plotted from the MOs panel values".
- **Table pt-ie (1)** How the columns are obtained:
  - **Koopmans:** −ε_HOMO × 27.2114. For the UHF open shells the HOMO is the highest occupied of the alpha and beta sets. The text does not say to compare both sets.
    - VERIFIED: in O_HF the highest is beta (−0.521805, index 3), above the alpha (−0.611817).
  - **ΔSCF:** Energy Calculator B − A in eV (direct, step 7). Fine.
  - **B3LYP:** −ε_HOMO of the Atoms topic × 27.2114. Not in the procedure.
  - **Experiment:** NIST, cited.
- **L183, figure ie (4)** Made by the python script. ECCE has no plot of IE across atoms. The reader can tabulate with the Energy Calculator, or with Compare Energies (only within one method). NOT VERIFIED whether any ECCE plot fits.
- **L189 (1)**
  - "relaxation energy 1.1 eV for C, 3.5 eV for Ne" = Koopmans − ΔSCF (ARITH: 11.94 − 10.80 = 1.14; 23.16 − 19.69 = 3.47). The subtraction is not stated.
  - "agree to 10⁻⁴ hartree" for Li: the Energy Calculator gives kJ/mol, kcal/mol and eV, not hartree (help energy-calculator / L54). So the reader cannot see this in hartree without converting. Give the eV figure, or the hartree arithmetic.
- **L200 (1)**
  - N alpha 2p −0.571 and O beta 2p −0.522 hartree: VERIFIED (N_HF alpha index 5 −0.570741; O_HF beta index 3 −0.521805).
  - Not said: how the MOs panel separates alpha and beta. A spin choice in the MOs panel is NOT VERIFIED.
  - "ΔSCF drops by 1.87 eV": ARITH, 13.90 − 12.03.
  - "measured 0.92 eV": ARITH from the rounded table, 14.53 − 13.62 = 0.91. Use 0.91, or give experiment to three decimals.
  - "O⁺ is a quartet, N⁺ a triplet": the multiplicity is read in the Organizer (multiplicity column, or the Calculation Editor). Not said; NOT VERIFIED which column.
- **L203 (1)** "Beryllium is 0.90 eV too low": ARITH, 9.32 − 8.42.
- **L207, table pt-ea (1)** EA from the Energy Calculator (eV and kJ/mol, step 8). Fine. The Experiment column is still \XXX.
- **L228 (1)** "HOMO of Li⁻ and C⁻ lies above zero": read in the MOs panel of Li_anion / C_anion. Not in the procedure. NOT VERIFIED numerically (outputs not read in this audit).
- **L126 (open)** \XXX: Cu 3d⁹4s² in ECCE-QM. Not checked.
- **L232 (open)** \XXX: Hund citation.
