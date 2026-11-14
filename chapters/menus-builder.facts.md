# Facts for appendix 1c: Builder menus (not chapter text)

ECCE main e6ff4018a (9.5.3-dev), read 2026-11-14 from the source (read only) and help/src.
Sources: src/apps/builder/BuilderGUI.C (menu bar), src/apps/builder/Builder.C
(createMenus, updateMenus, updateResource, setSaveState, read-only list,
right-click menu, Properties menu), src/wxviz/viztools/ViewerEvtHandler.C
(Options, Render, Build, Measure menus).

Legend: **Help:** the help page (help/src/<page>.md) that documents the item.
UNVERIFIED = known from the code only, no help page says it; check in a
running Builder before printing. Shortcuts are as wx writes them (Ctrl = Cmd
on macOS, not checked here).

General rules (code):
- When the structure is read-only (a calculation that has been submitted, or
  opened read-only), these are greyed: File > Add Structure from File...;
  Tools > Add Dummy Atom..., Add from SMILES..., Replace Group...; Build >
  Clean, Add Hydrogen, Remove Hydrogen, Generate Bonds, Clear Residue Info,
  Make into Residue-Based System, Center XYZ/X/Y/Z, Orient; Mode > Atom,
  Bond, Add Structure (and the element-list and Shape modes). (Builder.C
  p_readOnlyDisabledIds.) UNVERIFIED as user-facing wording; help says
  nothing general about read-only Builder menus.
- Several menus are filled at start-up, not in the menu-bar file: Options,
  Render, Build, Measure (ViewerEvtHandler), Mode and Tools (Builder.C),
  Properties (one entry per property panel the calculation has), Context
  (history of open structures).

## File
| Menu text | Shortcut | Does | Grey / hidden | Help |
|---|---|---|---|---|
| Add Structure from File... | | Adds the atoms of a structure file (PDB, CIF, XYZ, MVM, CAR, ...) to the current structure; Local Filesystem chooses this computer | grey when read-only | importing-a-structure |
| Import Calculation from Output File... | | Makes a calculation from a code's output file | removed from the menu when the Builder runs stand-alone (UNVERIFIED: code deletes it under isStandalone()) | importing-a-calculation |
| New | Ctrl+N | Starts another empty structure (listed in Open structures) | | importing-a-structure ("File > New starts another empty structure") |
| Open... | Ctrl+O | Opens a structure file as its own structure | grey when the Builder shows a calculation (code comment: Open vs Load confused users) | importing-a-structure |
| Close | Ctrl+W | Closes the current structure | | importing-a-structure |
| Save | Ctrl+S | Saves the structure into the calculation | grey unless there are unsaved changes; always grey for a structure with no calculation behind it and when read-only | UNVERIFIED (code setSaveState) |
| Save As... | Ctrl+E | Writes the structure to a file; type CIF, P1 writes cell + all atoms as P1 | | importing-a-structure |
| Create Thumbnail | | Makes the calculation's thumbnail picture | grey when no calculation is shown | UNVERIFIED |
| Dump Scene Graph | | Developer: writes the Open Inventor scene graph | hidden unless ECCE_DEVELOPER is set | ENVIRONMENT.md (ECCE_DEVELOPER: "Dump menu item") |
| Quit | Ctrl+Q | Closes the Builder | | |

## Edit
| Menu text | Shortcut | Does | Grey / hidden | Help |
|---|---|---|---|---|
| Undo.. (two dots in the source) | Ctrl+Z | Undoes the last command | grey when nothing to undo; label may name the command (UNVERIFIED) | UNVERIFIED |
| Redo | Ctrl+Y | Redoes | grey when nothing to redo | UNVERIFIED |
| Cut / Copy / Paste | Ctrl+X / C / V | clipboard of atoms | | UNVERIFIED |
| (wxID_CLEAR, empty label in the source) | | stock "Clear" item, label from wx | | UNVERIFIED: check what text appears |
| Delete Selection | Ctrl+D | Deletes the selected atoms | | UNVERIFIED |
| Distort Bonds... | | Changes bond lengths around one selected atom (also in the right-click menu when exactly one atom is selected) | | UNVERIFIED (no help page) |
| Take Coordinates From... | | Copies coordinates of chosen atoms (numbers from 1, e.g. 1-12,40) from another calculation in the same folder | | bonds-and-clean |
| Select All | Ctrl+A | | | |
| Select Molecule | | Extends the selection to whole molecules | | UNVERIFIED |
| Select Within Distance... | | Extends a selection to atoms within a centre-to-centre distance (0.1-50 Å, initially 3.5; remembered) | needs a selection first | importing-a-structure |
| Select Solvent | | Selects water (residue names SOL, HOH, WAT, TIP3, TIP4, SPC, H2O..., and water added by Solvate); not ions | | importing-a-structure |
| Select Ions | | Selects ions | | importing-a-structure |
| Select Protein / Select Ligand | | by residue type | | UNVERIFIED (Select Ligand not in help) |
| Select Backbone / Select Side Chains | | protein parts | grey when the structure has no residues (updateMenus) | UNVERIFIED |
| Reverse Selection | Ctrl+R | | | importing-a-structure |
| Clear Selection | Ctrl+U | | | importing-a-structure |

## Options (ViewerEvtHandler::createOptionMenu)
| Menu text | Kind | Does | Help |
|---|---|---|---|
| Show Hydrogen Atoms | check | | UNVERIFIED |
| Show Hydrogen Bonds | check | draws H bonds | bonds-and-clean |
| Hydrogen Bond Settings... | | distance and angle; remembered | bonds-and-clean |
| Atom Labels > None / Element with Number / Atom Name / Charge--2 decimal digits / Charge--3 decimal digits / Charge--4 decimal digits / Type | submenu | label choice | viewer-panels (Labels) |
| Show Bond Labels / Show Residue Labels / Show Summary Text Labels | check | | viewer-panels mentions bond, residue, summary labels |
| Show Axes / Show Aromatic Rings | check | | UNVERIFIED |
| Auto Normalize Display / Enable Spinning / Auto Open Residue Table | check | | UNVERIFIED |
| Clean Parameters... | | settings of Clean | UNVERIFIED (bonds-and-clean covers Clean, not this dialog) |
| Advanced > Show Bond Orders Used by Clean | check | | UNVERIFIED |
| Reset Default Tools/Toolbars | | restores panel and toolbar layout | UNVERIFIED |

## Render (ViewerEvtHandler::createRenderMenu + Builder.C)
| Menu text | Shortcut | Does | Help |
|---|---|---|---|
| Style > Ball And Wireframe / Ball And Stick / Stick / Wireframe / CPK / Residue Wire / Residue Cylinders / Line Ribbon / Flat Ribbon / Solid Ribbon / Cartoon / Custom Style... | Alt+1 ... Alt+7, Line and Flat Ribbon none, Solid Ribbon Alt+8, Cartoon Alt+9, Custom Style... Alt+0 | display style; applies to the selected atoms only when there is a selection | importing-a-structure (selection rule), viewer-panels (Custom Style: sphere/cylinder quality) |
| Enable Depth Cueing | check | | UNVERIFIED |
| Enable Orthographic | check | orthographic camera | UNVERIFIED |
| Hide Selected Atoms/Bonds | Ctrl+J | | UNVERIFIED |
| Hide Unselected Atoms/Bonds | Ctrl+I | | UNVERIFIED |
| Show Hidden Atoms/Bonds | Ctrl+L | | UNVERIFIED |
| View All | Ctrl+= | fit structure in view | UNVERIFIED |
| Reset View | Home | "Undo rotation and zoom; atoms are not changed" (status text) | UNVERIFIED |
| Zoom To Selection | Ctrl+* | | UNVERIFIED |
| Zoom In / Zoom Out | Ctrl++ / Ctrl+- | | UNVERIFIED |
| Background Color... | | | UNVERIFIED (book uses script `background 1 1 1`) |
| Foreground Color... | | "color used for labels, axis, measures, and text" (status text) | UNVERIFIED |
Commented out in the source (not shown): Stereo, Enable Transparency, Use Antialiasing.

## Build (ViewerEvtHandler::createBuildMenu)
| Menu text | Shortcut | Does | Help |
|---|---|---|---|
| Clean | Ctrl+K | force-field clean-up of the geometry | bonds-and-clean, first-calculation |
| Add Hydrogen | Ctrl+F | fills valences with H | first-calculation, importing-a-structure |
| Remove Hydrogen | Ctrl+G | | UNVERIFIED |
| Generate Bonds | Ctrl+B | bonds from distances | UNVERIFIED |
| Clear Residue Info | | | UNVERIFIED |
| Make into Residue-Based System | | | UNVERIFIED |
| Center XYZ / Center X / Center Y / Center Z | | moves the structure to the origin along those axes | UNVERIFIED |
| Orient | | "Orient moment of inertia tensor with axis" (status text) | UNVERIFIED |
All grey when read-only.

## Mode (radio items; Builder.C)
Previous Mode (Ctrl+,), Next Mode (Ctrl+.), then Select (Ctrl+1), Rotate
(Ctrl+2), Translate (Ctrl+3), Zoom (Ctrl+4), Atom (Ctrl+5), Bond (Ctrl+6),
Add Structure (Ctrl+7). Atom, Bond, Add Structure grey when read-only.
Help: UNVERIFIED (no help page describes the Mode menu; first-calculation may
describe the toolbar).

## Measure (ViewerEvtHandler::createMeasureMenu)
Distance, Angle, Torsion, Clear. Help: UNVERIFIED. (The Measure Toolbar also
has "Measure Dihedral Angle" and "Measure Clear" as tool tips, Builder.C.)

## Tools (Builder.C)
Fixed items:
| Menu text | Does (status text in quotes) | Grey / hidden | Help |
|---|---|---|---|
| Toolbars > File Toolbar / Mode Toolbar / View Toolbar / Style Toolbar / Manipulator Toolbar / Measure Toolbar | "Show/Hide Toolbars" | | UNVERIFIED |
| Dock Floating Panels | "Return every floating panel to its dock" | | viewer-panels, first-calculation |
| Geometry Constraints... | "Fix atoms and constrain bonds, angles and torsions" | | constraints-and-dummy-atoms, ecce-qm |
| Add Dummy Atom... | "Place a dummy atom X from the selected atoms" | grey when read-only | constraints-and-dummy-atoms |
| Add from SMILES... | "Build a molecule from a SMILES string" | grey when read-only | bonds-and-clean |
| Diffraction... | "Calculated diffraction pattern of this structure or the selected atoms"; a separate window | | fibre-diffraction |
| Replace Group... | "Replace the selected terminal group by a SMILES fragment" ([*] marks the attachment) | grey when read-only | bonds-and-clean |
| Docking Box Around Selection | sets the AutoDock Vina box of this calculation | grey unless the calculation is a Vina docking job (updateMenus: vinaJob()) | vina |
Then one check item per tool panel (shows/hides the panel), in this order:
Open structures, Build, Coordinates, Selection, Atom Table, Residue Table,
Symmetry, DNA Builder, Peptide Builder, Periodic Builder, Layer Builder,
Slicer, Clipping plane, then a separator, Log, and (only with ECCE_DEVELOPER)
Command Line. Residue Table is never greyed (opening it on a structure without
residues gives default ones; code comment). Help: Open structures
(importing-a-structure), Periodic Builder (importing-a-structure,
qe-first-calculation, layer-builder), Layer Builder (layer-builder),
Clipping plane (viewer-panels "Cutting the structure open"); Coordinates
(bonds-and-clean, energy-calculator); Symmetry (UNVERIFIED for the panel);
DNA Builder, Peptide Builder, Slicer, Atom Table, Log: UNVERIFIED (no help
page). Structure Library (NAME_TOOL_STRUCTLIB) is a panel too; whether it has a
Tools entry is UNVERIFIED (it is the Add Structure mode's panel).

## Properties
One check item per property panel the shown calculation has (e.g. MOs,
Geometry Trace, Conformers, Vibrations, Diffraction, ...); ticking shows the
panel. A "Surfaces" item ("Density, spin density, ESP, ELF, LOL and NCI
surfaces") follows "MOs" only when the calculation has a density.
Help: viewer-panels (Surfaces, panels); the full list of panels: UNVERIFIED
here, take it from viewer-panels.md and docs/claude/codereg (how properties
reach the Properties menu).

## Context
History of the structures/calculations opened in this Builder (wx file
history on this menu). UNVERIFIED wording.

## Help
on Builder... (Ctrl+H), Report a Problem..., About ECCE.... Help: index,
installation (Report a Problem).

## Right-click in the 3-D view (Builder.C mouseEvent)
Only on a click (not a drag) with atoms selected and not read-only:
Constrain Selected Atoms... (absent when constraints are read-only),
Add Dummy Atom..., and Distort Bonds... when exactly one atom is selected.
Help: constraints-and-dummy-atoms (right-click mention).
