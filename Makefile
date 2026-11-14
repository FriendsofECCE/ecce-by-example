# lualatex + makeindex + bibtex (biber is not installed here; the class uses backend=bibtex)
main.pdf: chapters/plan.tex main.tex ecce-macros.tex frontmatter.tex chapters/*.tex references.bib LegrandOrangeBook.cls
	lualatex -interaction=nonstopmode -halt-on-error main
	makeindex main.idx -s indexstyle.ist
	bibtex main
	lualatex -interaction=nonstopmode -halt-on-error main
	lualatex -interaction=nonstopmode -halt-on-error main

chapters/plan.tex: chapters.py
	python3 chapters.py

plan: chapters/plan.tex

check:
	python3 chapters.py check

clean:
	rm -f *.aux chapters/*.aux *.bbl *.blg *.idx *.ilg *.ind *.log *.out *.toc *.ptc *.bcf *.run.xml *.lof *.lot

.PHONY: clean plan check
