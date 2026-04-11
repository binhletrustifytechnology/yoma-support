# Check queue depth in Redis
docker compose exec redis redis-cli LLEN bull:jobs:wait


# Start with 3 workers
docker compose up -d --scale n8n-worker=3

# Scale up live
docker compose up -d --scale n8n-worker=5