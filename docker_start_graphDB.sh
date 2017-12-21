docker run -d --network=dockernet -p 8012:8012 --name gindexer graphen.ai/indexer:0.8
echo "Starting elasticsearch, it takes 30 seconds"
sleep 30
docker run -d --network=dockernet -p 8010:5000 --rm -e "GRAPHDB_DATA=/opt/graphen.ai/graphdb-rest/database" -e "GRAPHDB_PLUGINS=/opt/graphen.ai/graphdb-rest/lib/plugins" -e "GRAPHDB_FILE=/opt/graphen.ai/graphdb-rest/tmp" -e "INDEXER_HOST=gindexer" -e "INDEXER_PORT=8012" --name grest graphen.ai/graphdb-rest-ui:2.7-slim
