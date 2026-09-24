LATEX = latexmk -lualatex -interaction=nonstopmode -file-line-error
MAIN  = main
BW    = main-bw
EN    = english
EN_BW = english-bw
PL    = polish
PL_BW = polish-bw

.PHONY: all all-formats english polish generate build build-bw build-english \
        build-english-bw build-polish build-polish-bw check check-bw check-english \
        check-english-bw check-polish check-polish-bw clean watch

# "Aprendo los números": main.tex en color y main-bw.tex en blanco y
# negro, con el mismo body.tex y el mismo contenido generado -- lo único
# que cambia es \bookcolor, fijado antes de \input{preamble} (ver
# preamble.tex). "First Numbers", el mismo cuaderno en inglés, página a
# página: english.tex y english-bw.tex, con \booklang{english} (ver
# tools/idiomas.py); y "Poznaję liczby", en polaco: polish.tex y
# polish-bw.tex, con \booklang{polish}. `all` es el cuaderno en color;
# `english` y `polish`, los de inglés y polaco; `all-formats` compila y
# comprueba los seis PDF, y es lo que corre el CI.
all: generate build check

english: generate build-english check-english

polish: generate build-polish check-polish

all-formats: generate build check build-bw check-bw \
             build-english check-english build-english-bw check-english-bw \
             build-polish check-polish build-polish-bw check-polish-bw

generate:
	python3 tools/gen_numeros.py

build:
	$(LATEX) $(MAIN).tex

build-bw:
	$(LATEX) $(BW).tex

build-english:
	$(LATEX) $(EN).tex

build-english-bw:
	$(LATEX) $(EN_BW).tex

build-polish:
	$(LATEX) $(PL).tex

build-polish-bw:
	$(LATEX) $(PL_BW).tex

check:
	python3 tools/checklog.py $(MAIN).log
	python3 tools/check_pages.py $(MAIN).aux
	python3 tools/gen_numeros.py --check

check-bw:
	python3 tools/checklog.py $(BW).log
	python3 tools/check_pages.py $(BW).aux

check-english:
	python3 tools/checklog.py $(EN).log
	python3 tools/check_pages.py $(EN).aux

check-english-bw:
	python3 tools/checklog.py $(EN_BW).log
	python3 tools/check_pages.py $(EN_BW).aux

check-polish:
	python3 tools/checklog.py $(PL).log
	python3 tools/check_pages.py $(PL).aux

check-polish-bw:
	python3 tools/checklog.py $(PL_BW).log
	python3 tools/check_pages.py $(PL_BW).aux

clean:
	latexmk -C $(MAIN).tex
	latexmk -C $(BW).tex
	latexmk -C $(EN).tex
	latexmk -C $(EN_BW).tex
	latexmk -C $(PL).tex
	latexmk -C $(PL_BW).tex
	rm -f content/generated-days.tex content/generated-clave.tex
	rm -f content/english/generated-days.tex content/english/generated-clave.tex
	rm -f content/polish/generated-days.tex content/polish/generated-clave.tex

watch:
	$(LATEX) -pvc $(MAIN).tex
