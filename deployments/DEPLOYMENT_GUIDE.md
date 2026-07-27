# Kubernetes Deployment Guide

This folder contains YAML manifests for deploying the three microservices to EKS.

## Files

| File | Purpose |
|------|---------|
| `namespaces.yaml` | Create dev, stg, prod namespaces |
| `api-deployment.yaml` | Deploy Flask API service |
| `web-deployment.yaml` | Deploy Nginx web service |
| `worker-deployment.yaml` | Deploy Python worker service |

## Prerequisites

1. EKS cluster running and kubectl configured
2. Images already pushed to ECR with proper tags
3. AWS account ID: `447733314827`
4. Region: `us-east-1`

```bash
# Update kubeconfig
aws eks update-kubeconfig --name lwplabs-cluster --region us-east-1

# Verify kubectl access
kubectl get nodes
```

---

## Deployment Steps

### Step 1: Create Namespaces

```bash
kubectl apply -f namespaces.yaml
```

**Output:**
```
namespace/dev created
namespace/stg created
namespace/prod created
```

**Verify:**
```bash
kubectl get namespaces
```

---

### Step 2: Deploy to Development (dev branch)

Update image tags to `dev` and replicas to 1:

```bash
# Edit api-deployment.yaml
# Change: replicas: 1 (keep as is)
# Change: image tag from :dev to :dev
# Change: namespace from default to dev

kubectl apply -f api-deployment.yaml -n dev
kubectl apply -f web-deployment.yaml -n dev
kubectl apply -f worker-deployment.yaml -n dev
```

**Verify pods are running:**
```bash
kubectl get pods -n dev
kubectl get svc -n dev
```

**Expected output:**
```
NAME                    READY   STATUS    RESTARTS
api-xxxxxxxxxx-xxxxx    1/1     Running   0
web-xxxxxxxxxx-xxxxx    1/1     Running   0
worker-xxxxxxxxxx-xxxxx 1/1     Running   0
```

---

### Step 3: Deploy to Staging (stg branch)

Update image tags to `stg` and replicas to 2:

**Before deploying**, edit the YAML files:

```bash
# For each file, change:
# 1. namespace: stg
# 2. image tag: :stg
# 3. replicas: 2 (api and web), 1 (worker)

kubectl apply -f api-deployment.yaml -n stg
kubectl apply -f web-deployment.yaml -n stg
kubectl apply -f worker-deployment.yaml -n stg
```

**Verify:**
```bash
kubectl get pods -n stg
kubectl get svc -n stg
```

---

### Step 4: Deploy to Production (master branch)

Update image tags to `latest` (or `master`) and replicas to 3:

**Before deploying**, edit the YAML files:

```bash
# For each file, change:
# 1. namespace: prod (or default)
# 2. image tag: :latest (or :master)
# 3. replicas: 3 (api and web), 2 (worker)

kubectl apply -f api-deployment.yaml
kubectl apply -f web-deployment.yaml
kubectl apply -f worker-deployment.yaml
```

**Verify:**
```bash
kubectl get pods
kubectl get svc
```

---

## Quick Deploy Commands

### Deploy All Services to Dev
```bash
kubectl apply -f namespaces.yaml
kubectl apply -f api-deployment.yaml -n dev
kubectl apply -f web-deployment.yaml -n dev
kubectl apply -f worker-deployment.yaml -n dev
```

### Deploy All Services to Staging
```bash
kubectl apply -f api-deployment.yaml -n stg
kubectl apply -f web-deployment.yaml -n stg
kubectl apply -f worker-deployment.yaml -n stg
```

### Deploy All Services to Production
```bash
kubectl apply -f api-deployment.yaml
kubectl apply -f web-deployment.yaml
kubectl apply -f worker-deployment.yaml
```

---

## Accessing Services

### Get External IPs/Load Balancer URLs

```bash
# Dev environment
kubectl get svc -n dev
NAME      TYPE           CLUSTER-IP      EXTERNAL-IP
api       LoadBalancer   10.100.xxx.xxx  a1b2c3d4-xxxx.us-east-1.elb.amazonaws.com
web       LoadBalancer   10.100.xxx.xxx  a1b2c3d5-xxxx.us-east-1.elb.amazonaws.com
```

### Access Web Service
```bash
# Get the LoadBalancer URL
kubectl get svc web -n dev -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Open in browser
# http://a1b2c3d5-xxxx.us-east-1.elb.amazonaws.com
```

### Access API Service
```bash
# Port-forward for local testing
kubectl port-forward -n dev svc/api 5000:5000

# In another terminal
curl http://localhost:5000/health
curl http://localhost:5000/api/info
```

---

## Monitoring & Troubleshooting

### Check Pod Logs
```bash
# API logs
kubectl logs -f deployment/api -n dev

# Web logs
kubectl logs -f deployment/web -n dev

# Worker logs
kubectl logs -f deployment/worker -n dev
```

### Check Pod Events
```bash
kubectl describe pod <pod-name> -n dev
```

### Check Resource Usage
```bash
kubectl top nodes
kubectl top pods -n dev
```

### Check HPA Status
```bash
kubectl get hpa -n dev
kubectl describe hpa api -n dev
```

---

## Updating Deployments

### Update Image Tag
```bash
# Update API to new image
kubectl set image deployment/api \
  api=447733314827.dkr.ecr.us-east-1.amazonaws.com/app-api:sha-abc123 \
  -n dev

# Verify rollout
kubectl rollout status deployment/api -n dev
```

### Scale Replicas Manually
```bash
# Scale API to 5 replicas
kubectl scale deployment api --replicas=5 -n dev

# View status
kubectl get deployment api -n dev
```

### Rollback Deployment
```bash
# View rollout history
kubectl rollout history deployment/api -n dev

# Rollback to previous version
kubectl rollout undo deployment/api -n dev

# Rollback to specific revision
kubectl rollout undo deployment/api --to-revision=2 -n dev
```

---

## Deleting Deployments

### Delete Services
```bash
# Delete all from dev
kubectl delete -f api-deployment.yaml -n dev
kubectl delete -f web-deployment.yaml -n dev
kubectl delete -f worker-deployment.yaml -n dev

# OR delete entire namespace
kubectl delete namespace dev
```

### Delete Everything
```bash
kubectl delete namespace dev stg prod
```

---

## Environment Customization

### For Development
```yaml
replicas: 1
resources:
  requests:
    cpu: "100m"
    memory: "64Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

### For Staging
```yaml
replicas: 2  # API & Web; 1 for Worker
resources:
  requests:
    cpu: "200m"
    memory: "128Mi"
  limits:
    cpu: "1000m"
    memory: "512Mi"
```

### For Production
```yaml
replicas: 3  # API & Web; 2 for Worker
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "2000m"
    memory: "1Gi"
```

---

## Security Considerations

1. **Image Pull Secrets** (if ECR is private):
   ```bash
   kubectl create secret docker-registry ecr-secret \
     --docker-server=447733314827.dkr.ecr.us-east-1.amazonaws.com \
     --docker-username=AWS \
     --docker-password=$(aws ecr get-login-password --region us-east-1)
   ```

2. **Pod Security Policy** (optional):
   ```bash
   # Restrict pod privileges
   kubectl label namespace dev pod-security.kubernetes.io/enforce=restricted
   ```

3. **Network Policies** (optional):
   ```bash
   # Restrict inter-pod communication
   kubectl apply -f network-policy.yaml
   ```

---

## CI/CD Integration

For automated deployments based on branch pushes:

```bash
# Development (on dev branch push)
kubectl set image deployment/api \
  api=447733314827.dkr.ecr.us-east-1.amazonaws.com/app-api:dev \
  -n dev

# Staging (on stg branch push)
kubectl set image deployment/api \
  api=447733314827.dkr.ecr.us-east-1.amazonaws.com/app-api:stg \
  -n stg

# Production (on master branch push)
kubectl set image deployment/api \
  api=447733314827.dkr.ecr.us-east-1.amazonaws.com/app-api:latest
```

---

## Next Steps

1. ✅ Create namespaces
2. ✅ Deploy to dev/stg/prod
3. ✅ Test services (port-forward, LoadBalancer)
4. 📋 Set up Ingress Controller for routing
5. 📋 Configure auto-scaling policies
6. 📋 Set up monitoring dashboards (CloudWatch)
7. 📋 Configure backup & disaster recovery

---

## Useful Commands

```bash
# Check all resources in namespace
kubectl get all -n dev

# Port-forward to service
kubectl port-forward -n dev svc/api 5000:5000

# Get pods with labels
kubectl get pods -n dev --show-labels

# Watch deployment status
kubectl get deployment -n dev --watch

# Get events
kubectl get events -n dev --sort-by='.lastTimestamp'

# Exec into pod
kubectl exec -it <pod-name> -n dev -- /bin/sh

# Copy file from pod
kubectl cp dev/<pod-name>:/path/to/file ./local-file
```

---

## Support

For issues:
1. Check pod logs: `kubectl logs -f deployment/api -n dev`
2. Check pod events: `kubectl describe pod <pod-name> -n dev`
3. Check resource usage: `kubectl top pods -n dev`
4. Check image exists in ECR
5. Verify EKS cluster health: `kubectl cluster-info`
