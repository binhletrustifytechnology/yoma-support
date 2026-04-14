Postgres Deployment
$ kubectl create secret generic postgres-secret \
  --namespace n8n \
  --from-literal=POSTGRES_USER=n8n \
  --from-literal=POSTGRES_PASSWORD=n8n_pwd \
  --from-literal=POSTGRES_DB=n8n \
  --dry-run=client -o yaml | kubectl apply -f -

$ kubectl apply -f postgres.yaml

# Wait for it to be ready
$ kubectl rollout status statefulset/postgres -n n8n

Redis Deployment
$ kubectl apply -f redis.yaml

Add secret
$ kubectl create secret generic n8n-secret \
  --namespace n8n \
  --from-literal=N8N_ENCRYPTION_KEY=$(openssl rand -hex 24) \
  --from-literal=N8N_BASIC_AUTH_USER=admin \
  --from-literal=N8N_BASIC_AUTH_PASSWORD=admin1234 \
  --from-literal=QUEUE_BULL_REDIS_HOST=redis \
  --from-literal=QUEUE_BULL_REDIS_PORT=6379 \
  --from-literal=DB_POSTGRESDB_PASSWORD=n8n_pwd \
  --dry-run=client -o yaml | kubectl apply -f -

Apply in order
$ kubectl apply -f redis.yaml
$ kubectl apply -f configmap.yaml
$ kubectl apply -f deployment-main.yaml
$ kubectl apply -f deployment-worker.yaml

# Watch everything come up
$ kubectl get pods -n n8n -w

# Scaling workers
Scale up when you have heavy workflow load
$ kubectl scale deployment/n8n-worker -n n8n --replicas=4

Or use HPA (auto-scale on CPU)
$ kubectl autoscale deployment/n8n-worker -n n8n --cpu-percent=60 --min=2 --max=8

# Verify Queue Mode is active
Should show: EXECUTIONS_MODE=queue
$ kubectl exec -n n8n deploy/n8n-main -- env | grep EXECUTIONS_MODE

Check Redis has the Bull queues registered
$ kubectl exec -n n8n deploy/redis -- redis-cli keys "bull:*"

(*) NOTE:
# Check pod is running and readiness probe passes
$ kubectl get pods -n n8n -l app=postgres

# Connect directly to confirm the DB exists
$ kubectl exec -n n8n statefulset/postgres -- psql -U n8n -d n8n -c "\dt"

# Confirm n8n main connected successfully
$ kubectl logs -n n8n deploy/n8n-main | grep -i "database\|postgres\|migrat"

$ kubectl describe pod postgres-0 -n n8n
$ kubectl describe statefulset postgres
$ kubectl get pod postgres-0

$ kubectl rollout restart deployment/n8n-main -n n8n
$ kubectl rollout restart deployment/n8n-worker -n n8n

$ kubectl describe pod <POD-NAME> -n n8n
$ kubectl logs <POD-NAME> --previous


$ kubectl port-forward svc/n8n 5678:5678