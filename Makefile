
# Colours
RED				=	\033[0;31m
GREEN			=	\033[0;32m
YELLOW			=	\033[0;33m
BLUE			=	\033[0;34m
PURPLE			=	\033[0;35m
CYAN			=	\033[0;36m
WHITE			=	\033[0;37m
RESET			=	\033[0m


all:		env install
			@printf "$(BLUE)==> $(CYAN)Project ready to launch ✅\n\n$(RESET)"

env:
			@python3 -m venv .venv
			@printf "$(BLUE)==> $(CYAN)Python env created ✅\n\n$(RESET)"

install:
			@. .venv/bin/activate && pip install -r requirements.txt

.PHONY:		all env install