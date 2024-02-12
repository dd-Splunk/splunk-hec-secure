# .SILENT:
SHELL := /bin/bash
.PHONY: dc up token logs down clean

# Check with version of compose to use
ifneq ($(shell docker compose version 2>/dev/null),)
  DC=docker compose
else
  DC=docker-compose
endif


configs = .env

dc:
	@echo DC is $(DC)

.env :
	echo "Create $@ from template"
	envsubst < tpl$@ | op inject -f > $@

up: .env
	date +"Now time is %FT%T%z"
	$(DC) up -d
	date +"Now time is %FT%T%z"

token: .env
	echo "Create Splunk $@ for VS Code"
	./scripts/create-splunk-token.sh

logs:

	$(DC) logs -f

down:
	$(DC) down

clean:
	$(DC) down -v
	rm -rf .env .vscode/settings.json
