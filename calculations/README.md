# Calculations made for the book

Every calculation run for a chapter or appendix is kept here, so that it can
become an ECCE example later (most will). The layout is the one the ECCE
example importer reads (data/client/examples/<set>/<topic>/<example>/):

    calculations/<chapter>/<code>-<name>/
        <input file(s)>       as ECCE wrote them (owner and host neutralised)
        <output file(s)>      the code's main output
        NOTES.txt             one paragraph: system, method/basis, run type, what the
                              chapter uses it for; the ECCE example category it fits
    calculations/<chapter>/topic.txt   line 1: title; line 2: one-sentence description

CATALOG.tsv has one row per calculation (keep it sorted by chapter).
Files over 5 MB (trajectories, cube files, .gbw, wavefunctions) are not committed:
list them in the row's `large_files` column with where they are kept.
A coupled chain (e.g. CREST -> xTB -> ORCA) keeps every step, each in its own
directory, named in run order (01-crest-..., 02-xtb-..., 03-orca-...).
