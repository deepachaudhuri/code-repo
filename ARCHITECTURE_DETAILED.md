# AWS Architecture - Complete Pipeline Explanation

## Overview

This document describes the complete AWS architecture for the multi-service microservices application with CI/CD pipeline.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Branches: dev (dev) | stg (staging) | master (production) │   │
│  │  Services: api/ | web/ | worker/                           │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Push to GitHub
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│               GitHub Actions CI/CD Pipeline                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 1. Trigger on: dev, stg, or master branch push             │   │
│  │ 2. Setup build matrix (3 services)                         │   │
│  │ 3. Build Docker images (parallel)                          │   │
│  │ 4. Scan images for vulnerabilities                         │   │
│  │ 5. Login to AWS ECR                                        │   │
│  │ 6. Create ECR repositories (if not exists)                 │   │
│  │ 7. Push images with tags                                   │   │
│  │ 8. Test deployment info                                    │   │
│  │ 9. Notify build status                                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Push Images
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS ECR (Container Registry)                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  Repository: app-api                                        │   │
│  │  ├── Tags: dev, stg, master, latest                        │   │
│  │  ├── Tags: sha-{commit}, {timestamp}                       │   │
│  │  ├── Image scanning: enabled                               │   │
│  │  └── Encryption: AES256                                    │   │
│  │                                                              │   │
│  │  Repository: app-web                                        │   │
│  │  ├── Tags: dev, stg, master, latest                        │   │
│  │  ├── Tags: sha-{commit}, {timestamp}                       │   │
│  │  ├── Image scanning: enabled                               │   │
│  │  └── Encryption: AES256                                    │   │
│  │                                                              │   │
│  │  Repository: app-worker                                     │   │
│  │  ├── Tags: dev, stg, master, latest                        │   │
│  │  ├── Tags: sha-{commit}, {timestamp}                       │   │
│  │  ├── Image scanning: enabled                               │   │
│  │  └── Encryption: AES256                                    │   │
│  │                                                              │   │
│  │  Lifecycle Policy:                                          │   │
│  │  • Keep last 10 tagged images                              │   │
│  │  • Expire untagged images after 30 days                    │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Pull Images
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│            AWS Infrastructure (Managed by Terraform)                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  VPC: lwplabs-vpc (10.20.0.0/16)                           │   │
│  │  ├── Public Subnets:                                       │   │
│  │  │   ├── 10.20.1.0/24 (us-east-1a)                       │   │
│  │  │   └── 10.20.2.0/24 (us-east-1b)                       │   │
│  │  ├── Private Subnets:                                      │   │
│  │  │   ├── 10.20.3.0/24 (us-east-1a)                       │   │
│  │  │   └── 10.20.4.0/24 (us-east-1b)                       │   │
│  │  ├── Internet Gateway (for public access)                 │   │
│  │  └── NAT Gateway (for private outbound)                   │   │
│  │                                                              │   │
│  │  EKS Cluster: lwplabs-cluster                             │   │
│  │  ├── Kubernetes Version: 1.34                             │   │
│  │  ├── Control Plane: AWS managed                           │   │
│  │  └── Node Group: primary                                  │   │
│  │      ├── Instance Type: t3.medium                         │   │
│  │      ├── Desired Size: 2                                  │   │
│  │      ├── Min Size: 1                                      │   │
│  │      ├── Max Size: 4                                      │   │
│  │      ├── Disk Size: 20 GB                                 │   │
│  │      └── Location: Private subnets                        │   │
│  │                                                              │   │
│  │  EKS Add-ons (AWS managed):                               │   │
│  │  ├── EBS CSI Driver (for persistent volumes)             │   │
│  │  ├── EFS CSI Driver (for shared storage)                 │   │
│  │  └── CloudWatch Observability (logs & metrics)           │   │
│  │                                                              │   │
│  │  ECR Repositories (3 repositories):                       │   │
│  │  ├── app-api (lifecycle policy enabled)                   │   │
│  │  ├── app-web (lifecycle policy enabled)                   │   │
│  │  └── app-worker (lifecycle policy enabled)                │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Deploy Pods
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Kubernetes Deployments (EKS)                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  API Pods (Flask REST API)                                 │   │
│  │  ├── Service: ClusterIP (internal) / LoadBalancer (ext)    │   │
│  │  ├── Port: 5000                                            │   │
│  │  ├── Replicas: 1 (dev) | 2 (stg) | 3 (prod)              │   │
│  │  ├── Resources: 100m CPU, 64Mi RAM (request)              │   │
│  │  └── Image: {ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/ │   │
│  │           app-api:{branch-tag}                             │   │
│  │                                                              │   │
│  │  Web Pods (Nginx Static Site)                             │   │
│  │  ├── Service: LoadBalancer (external access)              │   │
│  │  ├── Port: 80                                             │   │
│  │  ├── Replicas: 1 (dev) | 2 (stg) | 3 (prod)              │   │
│  │  ├── Resources: 100m CPU, 64Mi RAM (request)              │   │
│  │  └── Image: {ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/ │   │
│  │           app-web:{branch-tag}                             │   │
│  │                                                              │   │
│  │  Worker Pods (Background Jobs)                            │   │
│  │  ├── Service: ClusterIP (internal only)                   │   │
│  │  ├── Replicas: 1 (dev) | 1 (stg) | 2 (prod)              │   │
│  │  ├── Resources: 100m CPU, 64Mi RAM (request)              │   │
│  │  └── Image: {ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/ │   │
│  │           app-worker:{branch-tag}                          │   │
│  │                                                              │   │
│  │  Ingress Controller (Nginx Ingress / ALB)                 │   │
│  │  ├── Path-based routing                                   │   │
│  │  ├── TLS/SSL termination (optional)                       │   │
│  │  └── External Load Balancer access                        │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Code Push to GitHub
```bash
# Developer commits code to dev/stg/master branch
git add .
git commit -m "feature: new API endpoint"
git push origin dev  # Triggers GitHub Actions
```

**Output:** GitHub receives push notification

---

### 2. GitHub Actions Builds Images
```
Trigger: Push to dev/stg/master branch

Jobs (Parallel):
├── Job 1: Build app-api service
│   ├── Checkout code
│   ├── Configure AWS credentials
│   ├── Login to ECR
│   ├── Build Docker image
│   ├── Scan for vulnerabilities
│   ├── Push to ECR with tags
│   └── Output: Image pushed
│
├── Job 2: Build app-web service
│   ├── (same steps as Job 1)
│   └── Output: Image pushed
│
└── Job 3: Build app-worker service
    ├── (same steps as Job 1)
    └── Output: Image pushed
```

**Image Tags Created:**
```
Repository: app-api
├── app-api:dev              (branch tag)
├── app-api:sha-a1b2c3d      (commit SHA)
├── app-api:20240127-143022  (timestamp)
└── app-api:latest           (master only)

Same for: app-web, app-worker
```

**Output:** 3 services × 4 tags = 12 images in ECR

---

### 3. Images Stored in ECR
```
AWS ECR (us-east-1)

app-api (3 images from last build):
├── app-api:dev@sha256:abc...
├── app-api:sha-a1b2c3d@sha256:def...
└── app-api:20240127-143022@sha256:ghi...

app-web (3 images from last build):
├── app-web:dev@sha256:jkl...
├── app-web:sha-a1b2c3d@sha256:mno...
└── app-web:20240127-143022@sha256:pqr...

app-worker (3 images from last build):
├── app-worker:dev@sha256:stu...
├── app-worker:sha-a1b2c3d@sha256:vwx...
└── app-worker:20240127-143022@sha256:yz...
```

**Security Features:**
- ✅ Image scanning enabled
- ✅ Vulnerability detection
- ✅ AES256 encryption
- ✅ Lifecycle policy (keep 10 versions, delete old)

---

### 4. Deploy to EKS

**Development Environment (dev branch):**
```bash
kubectl apply -f api-deployment-dev.yaml
# Uses image: app-api:dev

kubectl apply -f web-deployment-dev.yaml
# Uses image: app-web:dev

kubectl apply -f worker-deployment-dev.yaml
# Uses image: app-worker:dev

# Result:
# - 1 API pod
# - 1 Web pod
# - 1 Worker pod
# - All in 'dev' namespace
```

**Staging Environment (stg branch):**
```bash
kubectl apply -f api-deployment-stg.yaml
# Uses image: app-api:stg

# Result:
# - 2 API pods (replicas)
# - 2 Web pods (replicas)
# - 1 Worker pod
# - All in 'stg' namespace
```

**Production Environment (master branch):**
```bash
kubectl apply -f api-deployment-prod.yaml
# Uses image: app-api:master or app-api:latest

# Result:
# - 3 API pods (high availability)
# - 3 Web pods (high availability)
# - 2 Worker pods
# - All in 'default' namespace
# - Load balancers active
# - Auto-scaling enabled
```

---

## Image Tag Strategy

### Why Multiple Tags?

| Tag | Purpose | Usage |
|-----|---------|-------|
| `dev` | Branch identifier | Deploy to dev namespace |
| `stg` | Branch identifier | Deploy to stg namespace |
| `master` | Production version | Deploy to production |
| `latest` | Latest stable (master only) | Quick reference for prod |
| `sha-abc123` | Commit hash | Exact code version tracking |
| `20240127-143022` | Build timestamp | When built + version history |

### Example: Deployment Using Different Tags

```bash
# Deploy development
kubectl set image deployment/api \
  api=app-api:dev

# Deploy staging
kubectl set image deployment/api \
  api=app-api:stg

# Deploy production
kubectl set image deployment/api \
  api=app-api:latest

# Rollback to specific commit
kubectl set image deployment/api \
  api=app-api:sha-a1b2c3d
```

---

## Branch Strategy & Environments

```
BRANCH         → ENVIRONMENT → REPLICAS → IMAGE TAGS
──────────────────────────────────────────────────
dev            → Development → 1-2      → :dev, :sha-*, :timestamp
stg            → Staging     → 2        → :stg, :sha-*, :timestamp
master         → Production  → 3        → :master, :latest, :sha-*
```

### Workflow Example

```
1. Developer creates feature branch from dev
   git checkout -b feature/new-api
   
2. Push to dev branch
   git push origin dev
   
3. GitHub Actions builds images tagged as `:dev`
   Images pushed to ECR
   
4. Pull request to stg branch
   Code review
   
5. Merge to stg branch
   GitHub Actions builds images tagged as `:stg`
   Deploy to staging environment
   
6. After testing, pull request to master
   Final review
   
7. Merge to master branch
   GitHub Actions builds images tagged as `:master` and `:latest`
   Deploy to production environment
   
8. If issue in production
   git revert previous commit
   Push to master
   New images built and deployed
   
OR

   kubectl rollout undo deployment/api
   (Rolls back to previous replica set)
```

---

## Infrastructure Details

### VPC Architecture
```
VPC: 10.20.0.0/16
├── Public Subnets (Availability Zones):
│   ├── us-east-1a: 10.20.1.0/24 (64 IPs)
│   └── us-east-1b: 10.20.2.0/24 (64 IPs)
├── Private Subnets (Availability Zones):
│   ├── us-east-1a: 10.20.3.0/24 (64 IPs)
│   └── us-east-1b: 10.20.4.0/24 (64 IPs)
├── Internet Gateway (for public access)
└── NAT Gateway (for private outbound)
```

### EKS Cluster
```
Cluster: lwplabs-cluster
├── Kubernetes Version: 1.34 (latest)
├── Control Plane: AWS managed (3 AZs)
├── API Endpoint: Enabled & Encrypted
└── Node Group: primary
    ├── AMI Type: Amazon Linux 2
    ├── Instance Type: t3.medium
    ├── Capacity Type: On-Demand
    ├── Desired Size: 2
    ├── Min Size: 1
    ├── Max Size: 4
    ├── Disk Size: 20 GB
    ├── Subnets: Private (us-east-1a, us-east-1b)
    └── Security Group: Auto-configured
```

### Add-ons
```
EKS Add-ons (AWS managed):
├── EBS CSI Driver (for persistent block storage)
│   └── Allows: EBS volumes in pods
│
├── EFS CSI Driver (for shared file storage)
│   └── Allows: EFS volumes across pods
│
└── CloudWatch Observability (for logging & monitoring)
    ├── Logs: Pod logs → CloudWatch Logs
    ├── Metrics: Pod metrics → CloudWatch Metrics
    └── Dashboards: Auto-created
```

---

## Security Features

### ECR Security
- ✅ Image scanning enabled
- ✅ Vulnerability detection (CVE database)
- ✅ AES256 encryption at rest
- ✅ TLS encryption in transit
- ✅ Lifecycle policies (auto-cleanup)

### EKS Security
- ✅ VPC isolation
- ✅ Private node subnets
- ✅ Security groups
- ✅ IAM roles for pods (IRSA)
- ✅ Network policies (optional)
- ✅ Pod security policies (optional)

### GitHub Actions Security
- ✅ Secrets stored encrypted
- ✅ No credentials in logs
- ✅ Limited IAM permissions
- ✅ Audit logs available

---

## Cost Estimation

### Development (dev branch)
- 2 t3.medium EC2 instances: ~$30/month
- EKS cluster: ~$10/month (but shared)
- ECR storage: ~$2/month
- **Total: ~$42/month**

### Staging (stg branch)
- Same as dev: ~$42/month
- (Separate cluster or shared with additional pods)

### Production (master branch)
- 2 t3.medium EC2 instances (min): ~$30/month
- Elastic Load Balancer: ~$16/month
- EKS cluster: ~$10/month
- ECR storage: ~$5/month
- Data transfer: ~$5/month
- **Total: ~$66/month**

**Combined (Dev + Stg + Prod):** ~$150/month

---

## Monitoring & Logging

### CloudWatch Integration
```
Logs:
├── /aws/eks/lwplabs-cluster/cluster → Control plane logs
├── /aws/containerinsights/lwplabs-cluster/application → App logs
└── /aws/containerinsights/lwplabs-cluster/dataplane → Node logs

Metrics:
├── Pod CPU & Memory usage
├── Node CPU & Memory usage
├── Network I/O
└── Container restart count
```

### Health Checks
```
Liveness Probe:
├── API: GET /health (every 30s)
├── Web: GET / (every 30s)
└── Worker: File check (every 60s)

Readiness Probe:
├── API: GET /health (every 10s)
├── Web: GET / (every 10s)
└── Worker: Process check (every 10s)
```

---

## Next Steps for Deployment

1. ✅ Push code to GitHub
2. ✅ GitHub Actions builds and pushes images
3. ✅ Verify images in ECR console
4. 📋 Create Kubernetes manifests (deployment, service, ingress)
5. 📋 Configure kubectl to access EKS cluster
6. 📋 Apply manifests to deploy pods
7. 📋 Test services (port-forward, LoadBalancer, Ingress)
8. 📋 Set up monitoring dashboards
9. 📋 Configure auto-scaling policies
10. 📋 Set up backup & disaster recovery
