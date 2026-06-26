CONTAINER_NAME ?= pgvector
POSTGRES_USER ?= user
POSTGRES_PASSWORD ?= pswd
POSTGRES_DB ?= faq
POSTGRES_PORT ?= 5432
PGVECTOR_IMAGE ?= pgvector/pgvector:pg17
PGVECTOR_VOLUME ?= pgvector_data

.PHONY: run start stop restart logs shell init clean

run:
	docker run -it \
		--name $(CONTAINER_NAME) \
		-e POSTGRES_USER=$(POSTGRES_USER) \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_DB=$(POSTGRES_DB) \
		-v $(PGVECTOR_VOLUME):/var/lib/postgresql/data \
		-p $(POSTGRES_PORT):5432 \
		$(PGVECTOR_IMAGE)

start:
	docker start $(CONTAINER_NAME)

stop:
	docker stop $(CONTAINER_NAME)

restart: stop start

logs:
	docker logs -f $(CONTAINER_NAME)

shell:
	docker exec -it $(CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

init:
	docker exec -it $(CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "CREATE EXTENSION IF NOT EXISTS vector;"

clean:
	docker rm -f $(CONTAINER_NAME)
