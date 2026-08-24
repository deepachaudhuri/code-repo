# Kubernetes Deployment Guide

This folder contains YAML manifests for deploying the e-commerce example to EKS.

## Files

| File | Purpose |
|------|---------|
| `namespaces.yaml` | Create dev, stg, prod namespaces |
| `product-deployment.yaml` | Deploy the product catalog service |
| `login-deployment.yaml` | Deploy the storefront/login service |
| `order-deployment.yaml` | Deploy the order processing worker |

## Prerequisites

1. EKS cluster running and kubectl configured
2. Images already pushed to ECR with proper tags
3. AWS region: `us-east-1`
4. GitHub Actions workflow has AWS credentials configured

```bash
aws eks update-kubeconfig --name lwplabs-cluster --region us-east-1
kubectl get nodes
```

## Deployment Steps

### Step 1: Create namespaces
```bash
kubectl apply -f namespaces.yaml
```

### Step 2: Deploy to development
```bash
kubectl apply -f product-deployment.yaml -n dev
kubectl apply -f login-deployment.yaml -n dev
kubectl apply -f order-deployment.yaml -n dev
```

### Step 3: Deploy to staging
```bash
kubectl apply -f product-deployment.yaml -n stg
kubectl apply -f login-deployment.yaml -n stg
kubectl apply -f order-deployment.yaml -n stg
```

### Step 4: Deploy to production
```bash
kubectl apply -f product-deployment.yaml
kubectl apply -f login-deployment.yaml
kubectl apply -f order-deployment.yaml
```

## Accessing services

### Product catalog
```bash
kubectl port-forward -n dev svc/product 5000:5000
curl http://localhost:5000/products
```

### Login storefront
```bash
kubectl port-forward -n dev svc/login 80:80
curl http://localhost:80
```

### Order worker logs
```bash
kubectl logs -f deployment/order -n dev
```

---

## Monitoring

```bash
kubectl get pods -n dev
kubectl get svc -n dev
kubectl describe ingress lwplabs-ingress -n default
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
# Update Product service to a new image
kubectl set image deployment/product \
  product=447733314827.dkr.ecr.us-east-1.amazonaws.com/lwplabs-product:sha-abc123 \
  -n dev

# Verify rollout
kubectl rollout status deployment/product -n dev
```

### Scale Replicas Manually
```bash
# Scale Product service to 5 replicas
kubectl scale deployment product --replicas=5 -n dev

# View status
kubectl get deployment product -n dev
```

### Rollback Deployment
```bash
# View rollout history
kubectl rollout history deployment/product -n dev

# Rollback to previous version
kubectl rollout undo deployment/product -n dev

# Rollback to specific revision
kubectl rollout undo deployment/product --to-revision=2 -n dev
```

---

## Deleting Deployments

### Delete Services
```bash
# Delete all from dev
kubectl delete -f product-deployment.yaml -n dev
kubectl delete -f login-deployment.yaml -n dev
kubectl delete -f order-deployment.yaml -n dev

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
replicas: 2  # Product & Login; 1 for Order
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
replicas: 3  # Product & Login; 2 for Order
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
kubectl set image deployment/product \
  product=447733314827.dkr.ecr.us-east-1.amazonaws.com/lwplabs-product:dev \
  -n dev

# Staging (on stg branch push)
kubectl set image deployment/product \
  product=447733314827.dkr.ecr.us-east-1.amazonaws.com/lwplabs-product:stg \
  -n stg

# Production (on master branch push)
kubectl set image deployment/product \
  product=447733314827.dkr.ecr.us-east-1.amazonaws.com/lwplabs-product:latest
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
kubectl port-forward -n dev svc/product 5000:5000

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
1. Check pod logs: `kubectl logs -f deployment/product -n dev`
2. Check pod events: `kubectl describe pod <pod-name> -n dev`
3. Check resource usage: `kubectl top pods -n dev`
4. Check image exists in ECR
5. Verify EKS cluster health: `kubectl cluster-info`
