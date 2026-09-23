LATEX = latexmk -lualatex -interaction=nonstopmode -file-line-error
MAIN  = main
BW    = main-bw

.PHONY: all all-formats generate build build-bw check check-bw clean watch

# "Aprendo los números": main.tex en color y main-bw.tex en blanco y
# negro, con el mismo body.tex y el mismo contenido generado -- lo único
# que cambia es \bookcolor, fijado antes de \input{preamble} (ver
# preamble.tex). `all` es el cuaderno en color; `all-formats` compila y
# comprueba los dos PDF, y es lo que corre el CI.
all: generate build check

all-formats: generate build check build-bw check-bw

generate:
	python3 tools/gen_numeros.py

build:
	$(LATEX) $(MAIN).tex

build-bw:
	$(LATEX) $(BW).tex

check:
	python3 tools/checklog.py $(MAIN).log
	python3 tools/check_pages.py $(MAIN).aux
	python3 tools/gen_numeros.py --check

check-bw:
	python3 tools/checklog.py $(BW).log
	python3 tools/check_pages.py $(BW).aux

clean:
	latexmk -C $(MAIN).tex
	latexmk -C $(BW).tex
	rm -f content/generated-days.tex content/generated-clave.tex

watch:
	$(LATEX) -pvc $(MAIN).tex
