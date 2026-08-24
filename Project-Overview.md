# LWPlabs - Complete Pipeline Overview

This document explains the complete infrastructure-to-deployment pipeline.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Repository                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Branches: dev (Development) | stg (Staging) | master (Prod) │
│  │  Services: api/ | web/ | worker/                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                    │
└─────────────────────────────────────────────────────────────────┘
                                ↓
                    ┌───────────────────────┐
                    │   GitHub Actions      │
                    │   CI/CD Pipeline      │
                    │                       │
                    │ • Build images        │
                    │ • Scan vulnerabilities│
                    │ • Push to ECR         │
                    │ • Tag: branch/sha/*   │
                    └───────────────────────┘
                                ↓
                    ┌───────────────────────┐
                    │   AWS ECR (Registry)  │
                    │                       │
                    │ • app-api:dev/stg/... │
                    │ • app-web:dev/stg/... │
                    │ • app-worker:dev/...  │
                    │                       │
                    │ Scanning + Encryption │
                    │ Lifecycle policies    │
                    └───────────────────────┘
                                ↓
              ┌─────────────────────────────────┐
              │  AWS Infrastructure (Terraform)  │
              │                                   │
              │  • VPC: 10.20.0.0/16            │
              │  • EKS Cluster: 1.34             │
              │  • Node Group: 2 t3.medium       │
              │  • Add-ons: EBS, EFS, CloudWatch │
              └─────────────────────────────────┘
                                ↓
              ┌──────────────────────────────────┐
              │  Kubernetes (EKS) Deployments    │
              │                                   │
              │  • API Pods (Flask, port 5000)  │
              │  • Web Pods (Nginx, port 80)    │
              │  • Worker Pods (Background jobs) │
              │                                   │
              │  Services + Ingress Controllers  │
              └──────────────────────────────────┘
```

**For detailed architecture diagram:** See [code-repo/AWS_ARCHITECTURE.drawio](code-repo/AWS_ARCHITECTURE.drawio) (open with draw.io)

## 📁 File Structure

### Terraform Configuration (infra-repo/)

```
infra-repo/
├── main.tf              # Defines VPC, EKS, and ECR modules
├── variables.tf         # Variable definitions
├── outputs.tf           # Output values
├── terraform.tfvars     # Default values
└── README.md            # Infrastructure documentation
```

### Application Code (code-repo/)

```
code-repo/
├── api/
│   ├── Dockerfile       # Multi-stage build
│   ├── main.py          # Flask API application
│   └── requirements.txt  # Python dependencies
├── web/
│   ├── Dockerfile       # Nginx-based
│   ├── index.html       # Static website
│   └── nginx.conf       # Nginx configuration
├── worker/
│   ├── Dockerfile       # Python-based
│   ├── worker.py        # Background job processor
│   └── requirements.txt  # Python dependencies
├── .github/workflows/
│   └── build-and-push.yml  # GitHub Actions workflow
├── .gitignore           # Git ignore rules
├── README.md            # Project overview
└── GITHUB_ACTIONS_SETUP.md  # Setup instructions
```

## 🔄 Workflow - Step by Step

### Step 1: Infrastructure Setup (One-time)

```bash
cd infra-repo

# Initialize Terraform
terraform init

# Plan infrastructure
terraform plan

# Apply (creates VPC, EKS, ECR)
terraform apply
```

**Output:** 
- ✅ AWS VPC with public/private subnets
- ✅ AWS EKS Kubernetes cluster
- ✅ AWS ECR repositories (lwplabs-api, lwplabs-web, lwplabs-worker)

### Step 2: Push Application Code to GitHub

```bash
cd code-repo

git init
git remote add origin https://github.com/YOUR_USERNAME/lwplabs.git
git add .
git commit -m "Initial commit"

# Add GitHub Secrets: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
git push -u origin main
```

**Triggered:**
- 🔵 GitHub Actions workflow starts

### Step 3: GitHub Actions Builds and Pushes Images

**Workflow:** `.github/workflows/build-and-push.yml`

```
Triggers on: Push to main/develop or PR

Jobs:
1. setup                 - Configure build matrix
2. build-and-push       - Build 3 services (parallel)
   ├── api              - Build Flask API, push to ECR
   ├── web              - Build Nginx site, push to ECR
   └── worker           - Build worker, push to ECR
3. test-deployment      - Display ECR info
4. notify               - Send build status
```

**Output:**
```
lwplabs-api:latest, lwplabs-api:main, lwplabs-api:sha-abc123
lwplabs-web:latest, lwplabs-web:main, lwplabs-web:sha-abc123
lwplabs-worker:latest, lwplabs-worker:main, lwplabs-worker:sha-abc123
```

**Images stored in:** ECR repositories

### Step 4: Deploy to EKS (Manual)

Create Kubernetes manifests and deploy:

```bash
# Login to EKS
aws eks update-kubeconfig --name lwplabs-cluster --region us-east-1

# Create deployments
kubectl apply -f api-deployment.yaml
kubectl apply -f web-deployment.yaml
kubectl apply -f worker-deployment.yaml

# Verify
kubectl get pods
```

## 🔐 Security Features

### ECR Module Configuration

```hcl
repositories = [
  {
    name                 = "lwplabs-api"
    image_tag_mutability = "MUTABLE"      # Allow image tag updates
    scan_on_push         = true           # Scan images for vulnerabilities
    encryption_type      = "AES256"       # Encrypt images at rest
  },
  # ... more services
]
```

### Lifecycle Policy

```hcl
enable_default_lifecycle_policy = true
default_lifecycle_policy_days   = 30  # Clean old images
default_lifecycle_policy_count  = 10  # Keep last 10 versions
```

## 📊 Image Tags Strategy

Each build creates multiple tags:

| Tag | Purpose |
|-----|---------|
| `latest` | Latest version from main |
| `main` | Branch-specific (main/develop) |
| `sha-abc123` | Commit hash for traceability |
| `20240127-143022` | Build timestamp |

**Benefits:**
- ✅ Easy rollback to previous versions
- ✅ Commit-level tracking
- ✅ CI/CD pipeline integration
- ✅ Multiple environment support

## 🚀 Usage Examples

### Deploy Specific Version

```bash
# Using commit SHA
kubectl set image deployment/api-deployment \
  api=lwplabs-api:sha-abc123 \
  --record

# Using timestamp
kubectl set image deployment/api-deployment \
  api=lwplabs-api:20240127-143022 \
  --record
```

### Rollback to Previous Version

```bash
# View rollout history
kubectl rollout history deployment/api-deployment

# Rollback to previous version
kubectl rollout undo deployment/api-deployment

# Rollback to specific revision
kubectl rollout undo deployment/api-deployment --to-revision=2
```

### Build New Version

```bash
# Make code change
echo "# New feature" >> code-repo/api/main.py

# Commit and push
git add .
git commit -m "feat: Add new feature"
git push origin main

# GitHub Actions automatically:
# 1. Builds new Docker images
# 2. Pushes to ECR with new tags
# 3. Ready for deployment
```

## 📋 Checklist - Getting Started

- [ ] **Infrastructure**
  - [ ] Run `terraform apply` in infra-repo/
  - [ ] Verify VPC, EKS, ECR created
  - [ ] Note AWS Account ID and Region

- [ ] **GitHub Setup**
  - [ ] Create GitHub repository
  - [ ] Clone code-repo/ to your repo
  - [ ] Add secrets: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
  - [ ] Push to main branch

- [ ] **First Build**
  - [ ] GitHub Actions workflow runs
  - [ ] Verify images in ECR console
  - [ ] Check image tags (latest, sha-*, timestamp)

- [ ] **Deploy to EKS**
  - [ ] Create Kubernetes manifests
  - [ ] Update image URLs from ECR
  - [ ] `kubectl apply -f deployment.yaml`
  - [ ] Verify pods running: `kubectl get pods`

## 🔧 Troubleshooting

### ECR Repositories Not Created

```bash
# Verify Terraform applied successfully
terraform show | grep ecr

# Check if repositories exist
aws ecr describe-repositories --region us-east-1
```

### GitHub Actions Workflow Failed

1. Check **Actions** tab for error logs
2. Verify GitHub Secrets are set
3. Check AWS IAM permissions
4. Verify Dockerfile paths

### Images Not Pushing to ECR

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check ECR repository exists
aws ecr describe-repositories \
  --repository-names lwplabs-api \
  --region us-east-1
```

## 📚 Related Documentation

- [Terraform ECR Module](../aws-modules/ecr/README.md)
- [GitHub Actions Setup](code-repo/GITHUB_ACTIONS_SETUP.md)
- [EKS Deployment](../aws-modules/eks/samples/README.md)
- [Terraform Guide](../terraform/README.md)

## 🎯 Next Steps

1. ✅ Set up infrastructure with Terraform
2. ✅ Push code to GitHub
3. ✅ Verify images in ECR
4. 📋 Create Kubernetes deployment manifests
5. 📋 Deploy services to EKS cluster
6. 📋 Set up monitoring and logging
7. 📋 Configure ingress for external access
