(*) Note:
$ kubectl config set-context --current --namespace=n8n

Verify
$ kubectl get pods
$ kubectl get svc
$ kubectl logs deployment/n8n

Redeploy
$ kubectl rollout restart deployment n8n

-------------------------------------------------------------------------------------
1. Namespace
$ kubectl apply -f namespace.yaml

2. PersistentVolumeClaim
$ kubectl apply -f pvc.yaml

3. Secret (encryption key + basic auth)
$ kubectl create secret generic n8n-secret \
  --namespace n8n \
  --from-literal=N8N_ENCRYPTION_KEY=$(openssl rand -hex 24) \
  --from-literal=N8N_BASIC_AUTH_USER=admin \
  --from-literal=N8N_BASIC_AUTH_PASSWORD=admin1234

4. Deployment
$ kubectl apply -f deployment.yaml

5. Service
$ kubectl apply -f service.yaml

6. Ingress: Docker Desktop ships with nginx ingress controller available. First enable it
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml
$ kubectl apply -f ingress.yaml

-----------------------
Add **n8n.localhost** to **/etc/hosts**:
127.0.0.1  n8n.localhost

Then open http://n8n.localhost