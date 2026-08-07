# LWPlabs - Multi-Service Microservices Application

Build, push, and deploy three microservices to AWS EKS with Kubernetes Ingress routing.

---

## 📋 Quick Navigation

- [Quick Architecture](#quick-architecture) - Visual diagram
- [Services Overview](#services-overview) - Web, API, Worker services
- [Development Workflow](#development-workflow) - Push → Build → Deploy
- [Why Nginx Ingress?](#why-nginx-ingress-not-3-loadbalancers) - Cost & architecture comparison
- [Branch Strategy](#branch-strategy) - dev/stg/master
- [Setup Requirements](#setup-requirements) - Prerequisites & secrets
- [Deployment Guide](#deployment-guide) - How to deploy
- [Troubleshooting](#troubleshooting) - Common issues
- [AWS Architecture](#aws-architecture) - Full infrastructure
- [Common Commands](#common-commands) - kubectl snippets
- [Monitoring & Logs](#monitoring--logs) - Debugging

---

## Quick Architecture

```
┌────────────────────────────────────────────────────┐
│  Internet Client Requests                          │
└────────────────┬─────────────────────────────────┘
                 ▼
┌────────────────────────────────────────────────────┐
│  AWS LoadBalancer (Created by Ingress Controller)  │
│  ✅ ONE LoadBalancer = $16/month                   │
│  Exposes: Public IP / DNS                          │
└────────────────┬─────────────────────────────────┘
                 ▼
┌────────────────────────────────────────────────────┐
│  Nginx Ingress Controller (Pod in Kubernetes)      │
│  Smart router: Reads Ingress rules & routes traffic│
└─┬──────────────────────┬──────────────────────┬──┘
  │ Host: lwplabs.com    │ Host: api.lwplabs.com│  (Internal only)
  ▼                      ▼                       ▼
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│ Web Service │    │ API Service │    │ Worker Service   │
│(ClusterIP)  │    │(ClusterIP)  │    │ (ClusterIP only) │
│NO LB needed │    │NO LB needed │    │  NO LB needed    │
│ Port 80     │    │ Port 5000   │    │  Internal only   │
└─────────────┘    └─────────────┘    └──────────────────┘
     ↓                   ↓                      ↓
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│ Web Pods    │    │ API Pods    │    │ Worker Pods      │
│ (Nginx)     │    │ (Flask)     │    │ (Python)         │
└─────────────┘    └─────────────┘    └──────────────────┘
```

**Traffic Flow Explained:**
1. Client requests → **AWS LoadBalancer** (public IP)
2. LoadBalancer → **Nginx Ingress Controller** (pod inside cluster)
3. Ingress Controller reads hostname/path → **routes to correct service**
4. Service → **Pod** runs your application

**Key Points:**
- 🌐 **Single LoadBalancer**: Nginx Ingress Controller creates ONE AWS LoadBalancer (not three)
- 🔄 **Smart Routing**: Ingress reads rules → routes to correct internal service
- 💰 **Cost Efficient**: $16/month for 1 LB (vs $144/month for 3 separate LBs)
- 📦 **Three Services**: Web, API, Worker all are ClusterIP (internal only, no LoadBalancers)

---

## Services Overview

| Service | Language | Port | Access | Purpose |
|---------|----------|------|--------|---------|
| **Web** | Nginx | 80 | Public (via Ingress) | Static frontend |
| **API** | Python/Flask | 5000 | Public (via Ingress) | REST API backend |
| **Worker** | Python | - | Internal only | Async tasks |

[⬆ Back to Top](#-quick-navigation)

---

## Development Workflow

### 1. Push Code to GitHub
```bash
git add .
git commit -m "feature: description"

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
YOUR_LOAD_BALANCER_IP  lwplabs.example.com
YOUR_LOAD_BALANCER_IP  api.lwplabs.example.com
```

Then access:
- **Frontend**: http://lwplabs.example.com
- **API**: http://api.lwplabs.example.com
- **API Health**: http://api.lwplabs.example.com/health

[⬆ Back to Top](#-quick-navigation)

---

## Why Nginx Ingress (Not 3 LoadBalancers)?

### ❌ Bad Approach: Three LoadBalancer Services

```
❌ web service type: LoadBalancer → Creates AWS LoadBalancer #1 ($16/month)
❌ api service type: LoadBalancer → Creates AWS LoadBalancer #2 ($16/month)
❌ worker service type: LoadBalancer → Creates AWS LoadBalancer #3 ($16/month)

Total Cost: $48/month just for LoadBalancers
Total IPs: 3 different public IPs (confusing)
```

### ✅ Good Approach: Nginx Ingress + ClusterIP

```
✅ Nginx Ingress Controller → Creates AWS LoadBalancer #1 ($16/month)
✅ web service type: ClusterIP → No LoadBalancer
✅ api service type: ClusterIP → No LoadBalancer
✅ worker service type: ClusterIP → No LoadBalancer

Total Cost: $16/month (saves $32/month!)
Total IPs: 1 public IP (simple)
Ingress: Smart routing based on hostname/path
```

---

## LoadBalancer vs Ingress Comparison

| Aspect | Multiple LoadBalancers | Nginx Ingress |
|--------|------------------------|--------------:|
| **Public IPs** | 3 (one per service) | 1 (Ingress Controller) |
| **AWS Cost** | $48/month | $16/month |
| **Routing** | External DNS (manual) | Kubernetes native (automatic) |
| **SSL/TLS** | Per service | Centralized |
| **Domains** | 3 separate IPs | 1 IP, multiple hostnames |
| **Scalability** | Hard to add services | Easy - just add Ingress rule |
| **Complexity** | High (3 LBs to manage) | Low (1 Ingress to manage) |

[⬆ Back to Top](#-quick-navigation)

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
├── api/                          # Flask REST API
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── web/                          # Nginx frontend
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── worker/                       # Python background jobs
│   ├── Dockerfile
│   ├── worker.py
│   └── requirements.txt
├── deployments/                  # Kubernetes manifests
│   ├── api-deployment.yaml
│   ├── web-deployment.yaml
│   ├── worker-deployment.yaml
│   ├── ingress.yaml              # Nginx Ingress config
│   ├── namespaces.yaml
│   └── DEPLOYMENT_GUIDE.md
├── .github/workflows/            # CI/CD
│   ├── build-and-push.yml        # Build & push images
│   └── deploy-to-eks.yml         # Deploy to EKS
└── README.md                     # This file
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

[⬆ Back to Top](#-quick-navigation)

---

## Deployment Guide

### Manual Deployment (if needed)
```bash
# Create namespace
kubectl create namespace default

# Deploy all services
kubectl apply -f deployments/api-deployment.yaml
kubectl apply -f deployments/web-deployment.yaml
kubectl apply -f deployments/worker-deployment.yaml

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
kubectl logs deployment/api -n default
kubectl logs deployment/web -n default
kubectl logs deployment/worker -n default
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
```bash
# View untagged images
aws ecr describe-images \
  --repository-name lwplabs-api \
  --region us-east-1 \
  --query 'imageDetails[?imageTags==null]'

# Delete untagged images
aws ecr batch-delete-image \
  --repository-name lwplabs-api \
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
  │   ├── web (Port 80)
  │   ├── api (Port 5000)
  │   └── worker (Internal only)
  └── Pods (Running containers)
```

**How it Works:**
1. Nginx Ingress Controller creates a **LoadBalancer Service** in AWS
2. This creates **ONE AWS LoadBalancer** with a public IP
3. Your three services (web, api, worker) are **ClusterIP** (no LoadBalancers for them)
4. Traffic: Internet → AWS LoadBalancer → Nginx Ingress → Routes to correct service

**Infrastructure (Terraform-managed):**
- **VPC**: 10.20.0.0/16 with public & private subnets
- **EKS Cluster**: Kubernetes 1.34
- **Node Group**: 2 t3.medium instances (min: 1, max: 4)
- **ECR**: 3 repositories (api, web, worker) with image scanning
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
kubectl set image deployment/api api=lwplabs-api:dev

# Deploy staging
kubectl set image deployment/api api=lwplabs-api:stg

# Deploy production (latest)
kubectl set image deployment/api api=lwplabs-api:latest

# Rollback to specific commit (if latest has issues)
kubectl set image deployment/api api=lwplabs-api:sha-a1b2c3d
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
kubectl logs -f deployment/api -n default

# Scale deployment
kubectl scale deployment api --replicas=3 -n default

# Rollback to previous version
kubectl rollout undo deployment/api -n default

# Get service details
kubectl get svc -n default
kubectl describe svc api -n default

# Port forward for local testing
kubectl port-forward svc/api 5000:5000 -n default

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
kubectl logs deployment/api -n default

# Follow logs (tail)
kubectl logs -f deployment/api -n default

# View last 100 lines
kubectl logs deployment/api -n default --tail=100

# View all pod logs for a service
kubectl logs -l app=api -n default
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
