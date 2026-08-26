# LWPlabs - E-Commerce Microservices Example

This project demonstrates an e-commerce platform built as three microservices: product catalog, login, and order processing. It is designed to show how to build, push, and deploy a containerized AWS EKS application using GitHub Actions and Terraform.

---

## 📋 Quick Navigation

- [Quick Architecture](#quick-architecture) - Visual diagram
- [Services Overview](#services-overview) - Product, Login, Order services
- [Development Workflow](#development-workflow) - Push → Build → Deploy
- [Why Ingress?](#why-nginx-ingress-not-3-loadbalancers) - Cost & architecture comparison
- [Branch Strategy](#branch-strategy) - dev/stg/master
- [Setup Requirements](#setup-requirements) - Prerequisites & secrets
- [Deployment Guide](#deployment-guide) - How to deploy
- [Troubleshooting](#troubleshooting) - Common issues
- [Kubernetes Health Checks](#kubernetes-health-checks) - Liveness & Readiness Probes
- [Image Tags & Versioning](#image-tags--versioning) - Tag strategy
- [AWS Architecture](#aws-architecture) - Full infrastructure
- [Common Commands](#common-commands) - kubectl snippets
- [Monitoring & Logs](#monitoring--logs) - View logs and metrics

---

## Quick Architecture

```
┌────────────────────────────────────────────────────┐
│  Internet Customer Traffic                          │
└────────────────┬─────────────────────────────────┘
                 ▼
┌────────────────────────────────────────────────────┐
│  AWS LoadBalancer (Ingress Controller)              │
│  ✅ ONE LoadBalancer = $16/month                   │
│  Public access for the storefront and APIs         │
└────────────────┬─────────────────────────────────┘
                 ▼
┌────────────────────────────────────────────────────┐
│  Nginx Ingress Controller                          │
│  Routes requests by host/path to the right service │
└─┬──────────────────────┬──────────────────────┬──┘
  │ shop.lwplabs.com     │ product.lwplabs.com │ order.lwplabs.com
  ▼                      ▼                     ▼
┌───────────────┐    ┌───────────────┐   ┌──────────────────┐
│ Login Service │    │ Product Service│   │ Order Service    │
│(ClusterIP)    │    │(ClusterIP)     │   │(ClusterIP)       │
│ Port 80       │    │ Port 5000      │   │ Internal only    │
└───────────────┘    └───────────────┘   └──────────────────┘
     ↓                   ↓                     ↓
┌───────────────┐    ┌───────────────┐   ┌──────────────────┐
│ Login Pods    │    │ Product Pods  │   │ Order Worker Pods │
│ (Nginx)       │    │ (Flask API)   │   │ (Python)          │
└───────────────┘    └───────────────┘   └──────────────────┘
```

**Flow:**
1. Customer visits the storefront
2. Ingress routes traffic to the correct service
3. Product APIs return catalog data
4. Login handles authentication
5. Order workers process checkout events

---

## Services Overview

| Service | Language | Port | Access | Purpose |
|---------|----------|------|--------|---------|
| **Login** | Nginx | 80 | Public (via Ingress) | Customer sign-in and storefront |
| **Product** | Python/Flask | 5000 | Public (via Ingress) | Product catalog and inventory API |
| **Order** | Python | - | Internal only | Checkout and order processing |

---

## Development Workflow

### 1. Push Code to GitHub
```bash
git add .
git commit -m "feature: update storefront"

# Deploy to dev environment
git push origin dev

# Deploy to staging
git push origin stg

# Deploy to production
git push origin master
```

### 2. GitHub Actions Automatically:
1. ✅ Builds Docker images for all 3 services
2. ✅ Scans for vulnerabilities
3. ✅ Pushes to AWS ECR with environment-specific tags
4. ✅ Deploys to EKS cluster

### 3. Access Your Services

Once deployed, get the LoadBalancer IP:
```bash
kubectl get ingress -n default
```

Update `/etc/hosts` or DNS:
```
YOUR_LOAD_BALANCER_IP  shop.lwplabs.example.com
YOUR_LOAD_BALANCER_IP  product.lwplabs.example.com
```

Then access:
- **Storefront/Login**: http://shop.lwplabs.example.com
- **Product API**: http://product.lwplabs.example.com/products
- **Order API/Health**: http://product.lwplabs.example.com/orders/health

---

## Why Nginx Ingress (Not 3 LoadBalancers)?

### ❌ Bad Approach: Three LoadBalancer Services

```
❌ login service type: LoadBalancer → Creates AWS LoadBalancer #1 ($16/month)
❌ product service type: LoadBalancer → Creates AWS LoadBalancer #2 ($16/month)
❌ order service type: LoadBalancer → Creates AWS LoadBalancer #3 ($16/month)

Total Cost: $48/month just for load balancers
Total IPs: 3 different public IPs
```

### ✅ Good Approach: Nginx Ingress + ClusterIP

```
✅ Nginx Ingress Controller → Creates AWS LoadBalancer #1 ($16/month)
✅ login service type: ClusterIP → No LoadBalancer
✅ product service type: ClusterIP → No LoadBalancer
✅ order service type: ClusterIP → No LoadBalancer

Total Cost: $16/month (saves $32/month!)
Total IPs: 1 public IP (simple)
Ingress: Smart routing by host and path
```

---

## Branch Strategy

| Branch | Environment | Replicas | Image Tag |
|--------|-------------|----------|-----------|
| `dev` | Development | 1 | `:dev` |
| `stg` | Staging | 2 | `:stg` |
| `master` | Production | 3 | `:latest` |

---

## Project Structure

```
code-repo/
├── product/                     # Flask product catalog API
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── login/                       # Nginx storefront/login UI
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── order/                       # Python order processing worker
│   ├── Dockerfile
│   ├── worker.py
│   └── requirements.txt
├── deployments/                 # Kubernetes manifests
│   ├── product-deployment.yaml
│   ├── login-deployment.yaml
│   ├── order-deployment.yaml
│   ├── ingress.yaml
│   ├── namespaces.yaml
│   └── DEPLOYMENT_GUIDE.md
├── .github/workflows/           # CI/CD
│   ├── build-and-push.yml
│   └── deploy-to-eks.yml
└── README.md                    # This file
```

---

## Setup Requirements

### Prerequisites
1. ✅ AWS Account with ECR and EKS
2. ✅ GitHub repository with Actions enabled
3. ✅ AWS credentials configured

### GitHub Secrets (Required)
Add these in GitHub repository settings:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION (e.g., us-east-1)
```

### Local Tools
```bash
# Configure kubectl
aws eks update-kubeconfig --name lwplabs-cluster --region us-east-1

# Verify connection
kubectl get nodes
```

---

## Deployment Guide

### Manual Deployment (if needed)
```bash
# Create namespace
kubectl create namespace default

# Deploy all services
kubectl apply -f deployments/product-deployment.yaml
kubectl apply -f deployments/login-deployment.yaml
kubectl apply -f deployments/order-deployment.yaml

# Deploy Ingress (routes traffic to services)
kubectl apply -f deployments/ingress.yaml

# Verify
kubectl get pods
kubectl get ingress
```

### View Deployment Status
```bash
# Check pods
kubectl get pods -n default -w

# Check services
kubectl get svc -n default

# Check Ingress
kubectl describe ingress lwplabs-ingress -n default

# View logs
kubectl logs deployment/product -n default
kubectl logs deployment/login -n default
kubectl logs deployment/order -n default
```

### Troubleshooting

**Issue: Pods in ImagePullBackOff**
```bash
# Solution: ECR credentials secret is automatically created by GitHub Actions
# If deploying manually, create it:
ECR_LOGIN=$(aws ecr get-login-password --region us-east-1)
kubectl create secret docker-registry ecr-secret \
  --docker-server=447733314827.dkr.ecr.us-east-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password="$ECR_LOGIN" \
  --namespace=default
```

**Issue: Ingress not getting LoadBalancer IP**
```bash
# Install Nginx Ingress Controller (one-time setup)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

**Issue: Can't reach services via Ingress**
```bash
# Verify Ingress rules are correct
kubectl describe ingress lwplabs-ingress -n default

# Check if backend services are running
kubectl get svc -n default
```

**Issue: Untagged/Orphaned Images in ECR (Wasting Storage)**

Root cause: Docker Buildx (`docker/build-push-action`) generates provenance/SBOM
attestation manifests by default, which get pushed as extra untagged images
alongside the real tagged one. Fixed in the workflow with `provenance: false`
and `sbom: false` on the build step - now only 1 tagged image is pushed per build.

Clean up old untagged images already in ECR:
```bash
# View untagged images
aws ecr describe-images \
  --repository-name lwplabs-product \
  --region us-east-1 \
  --query 'imageDetails[?imageTags==null]'

# Delete untagged images
aws ecr batch-delete-image \
  --repository-name lwplabs-product \
  --region us-east-1 \
  --image-ids imageTag=null
```

**Better: Enable ECR Lifecycle Policy** (Auto-cleanup)
Update `infra-repo/main.tf`:
```hcl
module "ecr" {
  # ... existing config ...
  enable_default_lifecycle_policy = true
  default_lifecycle_policy_days   = 7   # Delete untagged after 7 days
  default_lifecycle_policy_count  = 3   # Keep last 3 tagged versions
}
```

[⬆ Back to Top](#-quick-navigation)

---

## Kubernetes Health Checks

Kubernetes uses **Liveness** and **Readiness** probes to keep your applications running smoothly:

### Understanding the Difference

| Aspect | Readiness Probe | Liveness Probe |
|--------|-----------------|-----------------|
| **Purpose** | Is pod ready to accept traffic? | Is pod still alive? |
| **When fails** | Removes from load balancer (don't restart) | Kills and restarts pod |
| **Check timing** | Earlier/faster (pod startup) | Later/slower (stable state) |
| **Use case** | Pod loading config/cache | Pod frozen/stuck/unresponsive |

### Real-World Scenario

```
Pod Startup Timeline:
│
├─ T=0s      Pod starts
│
├─ T=5s      readinessProbe first check
│            └─ Nginx starting up...
│            └─ ❌ FAIL → Remove from LB (no user traffic yet)
│
├─ T=15s     readinessProbe success (after 2 failures)
│            └─ Nginx ready! ✅ Add to LB (users can now reach it)
│
├─ T=30s     livenessProbe first check starts
│            └─ ✅ PASS → Still responding? Good!
│
├─ T=60s+    Normal operation
│            └─ readiness: Check every 10s (quick feedback)
│            └─ liveness: Check every 30s (ensure still alive)
│
├─ T=120s    BAD: Application freezes (memory leak/bug)
│            └─ readiness: ❌ FAIL → Remove from LB
│            └─ liveness: ❌ FAIL (after 3x) → KILL & RESTART
│            └─ Fresh pod comes up
```

### Configuration in Your Deployment

**Current setup** (login-deployment.yaml):

```yaml
# READINESS PROBE: Is the pod ready to accept user traffic?
# Used by load balancer to decide if requests should be sent to this pod
# If fails → pod is removed from load balancer (traffic diverted to other pods)
readinessProbe:
  httpGet:
    path: /                    # Simple health check - can serve static HTML?
    port: 80
  initialDelaySeconds: 5       # Quick check after startup (allows fast traffic routing)
  periodSeconds: 10            # Check every 10 seconds
  timeoutSeconds: 3
  failureThreshold: 2          # After 2 failures (20 sec), remove from LB

# LIVENESS PROBE: Is the pod still alive and responsive?
# Used by Kubernetes to decide if pod should be restarted
# If fails → pod is killed and restarted
livenessProbe:
  httpGet:
    path: /                    # Still responding to requests?
    port: 80
  initialDelaySeconds: 30      # Longer delay before first check (let app stabilize)
  periodSeconds: 30            # Check every 30 seconds (less aggressive)
  timeoutSeconds: 5
  failureThreshold: 3          # After 3 failures (90 sec), restart pod
```

### Advanced: Custom Health Check Endpoints

For more sophisticated checks, implement custom health endpoints in your apps:

**Example: Product API with health checks**
```python
# product/main.py
@app.route('/health/ready', methods=['GET'])
def readiness():
    """Readiness probe - dependencies available?"""
    try:
        # Check if database is available
        # Check if cache is ready
        # Check if config loaded
        return {"status": "ready"}, 200
    except Exception as e:
        return {"status": "not ready", "error": str(e)}, 503

@app.route('/health/live', methods=['GET'])
def liveness():
    """Liveness probe - still running?"""
    try:
        # Just check if app is responding
        # Don't check external dependencies
        return {"status": "alive"}, 200
    except Exception as e:
        return {"status": "dead", "error": str(e)}, 500
```

Then update deployment:
```yaml
readinessProbe:
  httpGet:
    path: /health/ready      # More thorough check
    port: 5000
  initialDelaySeconds: 5

livenessProbe:
  httpGet:
    path: /health/live       # Quick check
    port: 5000
  initialDelaySeconds: 30
```

### Monitoring Probe Results

```bash
# View probe events
kubectl describe pod <pod-name> -n default

# Output will show:
# Ready     True
# ContainersReady   True
# PodScheduled      True
# Events:
#   Type    Reason     Age   Message
#   ----    ------     ---   -------
#   Normal  Started    2m    Started container
#   Warning Unhealthy  1m    Readiness probe failed
#   Normal  Pulled     30s   Container image pulled

# View pod status
kubectl get pods -n default -o wide

# Watch pod restarts
kubectl get pods -n default --watch
```

### Common Probe Mistakes to Avoid

❌ **Mistake 1:** Making readiness probe too strict
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 5000
  failureThreshold: 1      # ❌ Removes immediately if any check fails
  periodSeconds: 5         # Too frequent - can cause flapping
```
✅ **Fix:** Allow some failures during startup
```yaml
failureThreshold: 2        # Allow 2 failures (20 sec with 10s interval)
periodSeconds: 10          # Check every 10 seconds
```

❌ **Mistake 2:** Checking external dependencies in liveness
```yaml
livenessProbe:
  httpGet:
    path: /health/database-check   # ❌ Checks DB connection
    port: 5000
```
✅ **Fix:** Liveness should just check if app is running
```yaml
livenessProbe:
  httpGet:
    path: /                        # Simple check - app responding?
    port: 5000
```

❌ **Mistake 3:** Same timeout for both probes
```yaml
readinessProbe:
  timeoutSeconds: 1        # ❌ Too short - network latency
livenessProbe:
  timeoutSeconds: 1        # ❌ Too short
```
✅ **Fix:** Give liveness longer timeout (checking for hangs)
```yaml
readinessProbe:
  timeoutSeconds: 3        # Quick (startup phase)
livenessProbe:
  timeoutSeconds: 5        # Longer (checking for freezes)
```

[⬆ Back to Top](#-quick-navigation)

---

## AWS Architecture

```
GitHub Repository (dev/stg/master)
         ↓ (Push code)
GitHub Actions CI/CD Pipeline
         ↓ (Build images)
AWS ECR (Container Registry)
         ↓ (Pull images)
AWS EKS Cluster (Kubernetes)
  ├── AWS LoadBalancer (Created by Ingress Controller)
  │   └── 1 Public LoadBalancer = $16/month
  ├── Nginx Ingress Controller (Pod)
  │   └── Routes traffic based on hostnames/paths
  ├── Services (All ClusterIP - Internal)
  │   ├── login (Port 80)
  │   ├── product (Port 5000)
  │   └── order (Internal only)
  └── Pods (Running containers)
```

**How it Works:**
1. Nginx Ingress Controller creates a **LoadBalancer Service** in AWS
2. This creates **ONE AWS LoadBalancer** with a public IP
3. Your three services (login, product, order) are **ClusterIP** (no LoadBalancers for them)
4. Traffic: Internet → AWS LoadBalancer → Nginx Ingress → Routes to correct service

**Infrastructure (Terraform-managed):**
- **VPC**: 10.20.0.0/16 with public & private subnets
- **EKS Cluster**: Kubernetes 1.34
- **Node Group**: 2 t3.medium instances (min: 1, max: 4)
- **ECR**: 3 repositories (product, login, order) with image scanning
- **LoadBalancer**: 1 AWS LoadBalancer (created by Ingress Controller)

---

## Image Tags & Versioning

Each build creates **2-3 tags** (NO untagged images):

```
For dev/stg branches:
├── :dev (or :stg)     ← Deploy to environment
└── :sha-a1b2c3d       ← Specific commit for rollback

For master branch (Production):
├── :master            ← Deploy this
├── :latest            ← Always overwrites (newest production)
└── :sha-a1b2c3d       ← Rollback to specific commit if needed
```

**Important:** The workflow now **prevents empty tags** - only tagged images are pushed to ECR. This avoids orphaned/untagged images that waste storage.

**Why Multiple Tags for Master?**
- `:master` - Explicit branch tag (clear intent)
- `:latest` - Always overwrites with newest build (standard convention)
- `:sha-abc` - Specific commit versions (for rollback safety)

**Example Deployments:**
```bash
# Deploy development
kubectl set image deployment/product product=lwplabs-product:dev

# Deploy staging
kubectl set image deployment/product product=lwplabs-product:stg

# Deploy production (latest)
kubectl set image deployment/product product=lwplabs-product:latest

# Rollback to specific commit (if latest has issues)
kubectl set image deployment/product product=lwplabs-product:sha-a1b2c3d
```

**Why `:latest` Gets Overwritten:**
- Each master branch push creates new `:latest` tag
- Old `:sha-*` tags remain for easy rollback
- Clear indicator of "current production version"

---

## Common Commands

```bash
# View all pods in namespace
kubectl get pods -n default -o wide

# View pod logs
kubectl logs -f deployment/product -n default

# Scale deployment
kubectl scale deployment product --replicas=3 -n default

# Rollback to previous version
kubectl rollout undo deployment/product -n default

# Get service details
kubectl get svc -n default
kubectl describe svc product -n default

# Port forward for local testing
kubectl port-forward svc/product 5000:5000 -n default

# Execute commands in pod
kubectl exec -it pod-name -- /bin/sh

# Delete pod (will be recreated)
kubectl delete pod pod-name -n default

# View events
kubectl get events -n default --sort-by='.lastTimestamp'
```

[⬆ Back to Top](#-quick-navigation)

---

## Monitoring & Logs

### CloudWatch (AWS)
- Pod logs automatically sent to CloudWatch
- View in AWS Console → CloudWatch → Log Groups

### kubectl Logs
```bash
# View current logs
kubectl logs deployment/product -n default

# Follow logs (tail)
kubectl logs -f deployment/product -n default

# View last 100 lines
kubectl logs deployment/product -n default --tail=100

# View all pod logs for a service
kubectl logs -l app=product -n default
```

### Pod Metrics
```bash
# View CPU/Memory usage
kubectl top nodes
kubectl top pods -n default
```

[⬆ Back to Top](#-quick-navigation)

---

## Next Steps

1. **Configure DNS**: Point your domain to LoadBalancer IP
2. **Setup HTTPS**: Add SSL certificate to Ingress
3. **Enable Auto-scaling**: Configure HPA for automatic scaling
4. **Setup Monitoring**: Configure Prometheus & Grafana
5. **Add Health Checks**: Implement readiness/liveness probes

---

## Support & Documentation

- 🔗 [Kubernetes Ingress Docs](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- 🔗 [EKS Documentation](https://docs.aws.amazon.com/eks/)
- 🔗 [ECR Documentation](https://docs.aws.amazon.com/ecr/)
- 🔗 [GitHub Actions](https://docs.github.com/en/actions)

---

**Last Updated:** 2026-08-06  
**Version:** 1.0

[⬆ Back to Top](#lwplabs---multi-service-microservices-application)
