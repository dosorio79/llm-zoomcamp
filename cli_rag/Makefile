POSTGRES_IMAGE ?= cli-rag-postgres
POSTGRES_CONTAINER ?= cli-rag-postgres
POSTGRES_VOLUME ?= cli-rag-postgres-data
POSTGRES_PORT ?= 5432
POSTGRES_DB ?= cli_rag
POSTGRES_USER ?= postgres
POSTGRES_PASSWORD ?= postgres

.PHONY: run test model-download ingest db-build db-start db-stop db-reset db-logs schema-setup schema-reset

run:
	uv run python main.py

test:
	uv run python -m unittest discover -s tests

model-download:
	uv run python -m src.embed.download

ingest:
	uv run python -m src.ingestion

db-build:
	docker build -f Dockerfile.postgres -t $(POSTGRES_IMAGE) .

db-start:
	@docker start $(POSTGRES_CONTAINER) >/dev/null 2>&1 || \
		docker run --detach \
			--name $(POSTGRES_CONTAINER) \
			--publish $(POSTGRES_PORT):5432 \
			--env POSTGRES_DB=$(POSTGRES_DB) \
			--env POSTGRES_USER=$(POSTGRES_USER) \
			--env POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
			--volume $(POSTGRES_VOLUME):/var/lib/postgresql/data \
			$(POSTGRES_IMAGE)

db-stop:
	@docker stop $(POSTGRES_CONTAINER) >/dev/null 2>&1 || true

db-reset:
	@docker rm --force $(POSTGRES_CONTAINER) >/dev/null 2>&1 || true
	@docker volume rm $(POSTGRES_VOLUME) >/dev/null 2>&1 || true

db-logs:
	docker logs --follow $(POSTGRES_CONTAINER)

schema-setup:
	uv run python -m src.db.schema setup

schema-reset:
	uv run python -m src.db.schema reset
