docker load -i graphen.ai-indexer-0.8.tar
docker load -i gpostgres-alpine.tar
docker load -i graphen.ai-graphdb-rest-ui-2.7-slim.tar
docker network create --driver bridge dockernet
docker network inspect dockernet
