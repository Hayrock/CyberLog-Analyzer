PT := python
NAME_VENV := Infra_VENV
VENV := ${NAME_VENV}/bin/activate
PIP := $(NAME_VENV)/bin/pip

LOG_INFO = echo -e "\033[1;34m[INFO]\033[0m"
LOG_OK = echo -e "\033[1;32m[OK]\033[0m"
LOG_ERR = echo -e "\033[1;31m[ERR]\033[0m"

MAKEFLAGS += --no-print-directory

PHONY := help install run all debug test lint clean fclean re

help:
	@echo "make install: Install Virtual Environnement on computer."
	@echo "make run: Run program in Virtual Environnement."
	@echo "make all: Install and run progra in Virtual Environnement."
	@echo "make debug: Launch program in debug mode"
	@echo "make test: Execute test 'Pytest'."
	@echo "make lint: Run Flake8, Flake8-docstring (pep257), MyPy --strict, Pyright and Pylint."
	@echo "make re: Rebuild all."
	@echo "make clean: Clean all cache."
	@echo "make fclean: Renitialise project as beginning."

install:
	@${LOG_INFO} "Initializing Virtual Environment..."
	@${PT} -m venv ${NAME_VENV}
	@if [ -f "${NAME_VENV}/bin/activate" ]; then \
		${LOG_OK} "Virtual Environment was created!"; \
		echo ""; \
	else \
		${LOG_ERR} "Virtual Environment cannot be created."; \
		exit 1; \
	fi

	@${LOG_INFO} "Upgrading pip..."
	@${PIP} install --upgrade pip

	@${LOG_INFO} "Installing requirements..."
	@if [ -f "requirements.txt" ]; then \
		${PIP} install -r requirements.txt && ${LOG_OK} "All requirements installed!"; \
	else \
		${LOG_ERR} "requirements.txt not found!"; \
		exit 1; \
	fi

run: install
	@if [ -f "${NAME_VENV}/bin/activate" ]; then \
		${LOG_INFO} "Launching program with Virtual Environnement."; \
		. ${VENV} && ${PIP} install -r requirements.txt; \
		echo ""; \
		echo "==== RUNNING ===="; \
		echo "You're actually in $$(${NAME_VENV}/bin/python -c 'import sys; print(sys.prefix)')"; \
		echo ""; \
		read -p "Press [Enter] to launch program..." dummy && \
		clear && \
		sudo ${NAME_VENV}/bin/python agent/monitor.py; \
	else \
		${LOG_INFO} "Do you want launch program without Virtual Environnement ? [y/N]"; \
		while true; do \
			read -p ">>> " ANSWER; \
			echo ""; \
			if [ "$$ANSWER" = "y" ]; then \
				${LOG_INFO} "Launching program without Virtual Environnement."; \
				echo ""; \
				echo "==== RUNNING ===="; \
				echo "You're actually in $$(${NAME_VENV}/bin/python -c 'import sys; print(sys.prefix)')"; \
				echo ""; \
				read -p "Press [Enter] to launch program..." dummy && \
				clear && \
				sudo ${NAME_VENV}/bin/python agent/monitor.py; \
				break; \
			elif [ "$$ANSWER" = "N" ]; then \
				${LOG_INFO} "Re-running installation..."; \
				$(MAKE) install && $(MAKE) run; \
				break; \
			else \
				${LOG_ERR} "Unrecognize answer."; \
			fi \
		done \
	fi

all: install run

debug: install
	${python}

test:

lint: install
	@set -e; \
	if [ -f "${NAME_VENV}/bin/activate" ]; then \
		. ${VENV} && pip install -r requirements.txt; \
		${LOG_INFO} "Launching program with Virtual Environnement."; \
		echo ""; \
		read -p "Press [Enter] to launch lint..." dummy && \
		clear; \
		echo "==== RUNNING ===="; \
		echo "You're actually in $$(${NAME_VENV}/bin/python -c 'import sys; print(sys.prefix)')"; \
		echo ""; \
		${LOG_INFO} "Running Flake8 and Flake8-docstring (pep257)."; \
		flake8 agent/*.py; \
		flake8 --docstring-convention pep257 agent/*.py; \
		${LOG_OK} "Flake8 and Flake8-docstring (pep257) pass. "; \
		echo ""; \
		${LOG_INFO} "Running MyPy --strict."; \
		mypy --strict agent/*.py; \
		echo ""; \
		${LOG_INFO} "Running Pyright."; \
		pyright agent/*.py; \
		echo ""; \
		${LOG_INFO} "Running Pylint."; \
		pylint agent/*.py; \
		echo ""; \
		${LOG_OK} "Black --check. "; \
		black --check --diff agent/*.py; \
		echo ""; \
		${LOG_OK} "All test passed."; \
	else \
		$(LOG_ERR) "Cannot launch 'make lint' wihtout Virtual Environnement please do command 'make install'."; \
	fi

clean:
	@${LOG_INFO} "Cleanning all cache files."
	@sudo find . \( -type d -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -rf {} +
	@${LOG_OK} "All cache was clear."
	@echo ""

fclean: clean
	@${LOG_INFO} "Erase all file and put back project as in origine."
	@sudo rm -rf agent/app_logs.log ${NAME_VENV}
	@${LOG_OK} "Project was renitialize."
	@echo ""

re:
	@${LOG_INFO} "Rebuild project from scratch."
	@$(MAKE) fclean
	@$(MAKE) all
	@${LOG_OK} "Building was finish."
