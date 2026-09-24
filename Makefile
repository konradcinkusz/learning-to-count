LATEX = latexmk -lualatex -interaction=nonstopmode -file-line-error
MAIN  = main
BW    = main-bw
EN    = english
EN_BW = english-bw

.PHONY: all all-formats english generate build build-bw build-english \
        build-english-bw check check-bw check-english check-english-bw clean watch

# "Aprendo los números": main.tex en color y main-bw.tex en blanco y
# negro, con el mismo body.tex y el mismo contenido generado -- lo único
# que cambia es \bookcolor, fijado antes de \input{preamble} (ver
# preamble.tex). "First Numbers", el mismo cuaderno en inglés, página a
# página: english.tex y english-bw.tex, con \booklang{english} (ver
# tools/idiomas.py). `all` es el cuaderno en color; `english`, el de
# inglés; `all-formats` compila y comprueba los cuatro PDF, y es lo que
# corre el CI.
all: generate build check

english: generate build-english check-english

all-formats: generate build check build-bw check-bw \
             build-english check-english build-english-bw check-english-bw

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

clean:
	latexmk -C $(MAIN).tex
	latexmk -C $(BW).tex
	latexmk -C $(EN).tex
	latexmk -C $(EN_BW).tex
	rm -f content/generated-days.tex content/generated-clave.tex
	rm -f content/english/generated-days.tex content/english/generated-clave.tex

watch:
	$(LATEX) -pvc $(MAIN).tex
