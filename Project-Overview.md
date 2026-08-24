# E-Commerce Pipeline Overview

This document explains the complete infrastructure-to-deployment flow for an e-commerce application built with a product catalog, login experience, and order processing service.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Repository                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Branches: dev | stg | master                          │   │
│  │  Services: product/ | login/ | order/                 │   │
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
                    │ • app-product:dev/... │
                    │ • app-login:dev/...   │
                    │ • app-order:dev/...   │
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
              ┌──────────────────────────────────────┐
              │  Kubernetes (EKS) Deployments         │
              │                                        │
              │  • Product Pods (catalog API, port 5000) │
              │  • Login Pods (storefront, port 80)      │
              │  • Order Pods (background order worker)  │
              │                                        │
              │  Services + Ingress Controllers         │
              └──────────────────────────────────────┘
```

## 📁 File Structure

```
code-repo/
├── product/
│   ├── Dockerfile       # Multi-stage build
│   ├── main.py          # Product catalog API
│   └── requirements.txt # Python dependencies
├── login/
│   ├── Dockerfile       # Nginx storefront
│   ├── index.html       # Login/storefront page
│   └── nginx.conf       # Nginx configuration
├── order/
│   ├── Dockerfile       # Python worker
│   ├── worker.py        # Order processing
│   └── requirements.txt # Python dependencies
├── .github/workflows/
│   └── build-and-push.yml
├── .gitignore
├── README.md
└── Project-Overview.md
```

## 🔄 Workflow - Step by Step

### Step 1: Infrastructure Setup
```bash
cd infra-repo
terraform init
terraform plan
terraform apply
```

**Output:**
- ✅ AWS VPC with public/private subnets
- ✅ AWS EKS cluster
- ✅ AWS ECR repositories for product/login/order

### Step 2: Push code to GitHub
```bash
cd code-repo
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 3: Build and push images
The workflow builds three services in parallel:
- product
- login
- order

**Example output:**
```
lwplabs-product:latest, lwplabs-product:main, lwplabs-product:sha-abc123
lwplabs-login:latest, lwplabs-login:main, lwplabs-login:sha-abc123
lwplabs-order:latest, lwplabs-order:main, lwplabs-order:sha-abc123
```

### Step 4: Deploy to EKS
```bash
aws eks update-kubeconfig --name lwplabs-cluster --region us-east-1
kubectl apply -f product-deployment.yaml
kubectl apply -f login-deployment.yaml
kubectl apply -f order-deployment.yaml
```

## 📊 Example E-Commerce Flow

- Customer visits the login/storefront page
- Product API serves catalog and availability data
- Order worker processes cart checkout and shipping jobs
- Ingress routes traffic by hostname/path to the correct service

## 📋 Checklist - Getting Started

- [ ] Run `terraform apply` in infra-repo/
- [ ] Push code to GitHub
- [ ] Verify images in ECR
- [ ] Deploy the product/login/order manifests to EKS
- [ ] Validate the storefront and product endpoints

## 🔧 Troubleshooting

### GitHub Actions workflow failed
1. Check the Actions tab
2. Verify AWS credentials are set
3. Confirm Dockerfile paths are correct

### Images not pushing to ECR
```bash
aws sts get-caller-identity
aws ecr describe-repositories --repository-names lwplabs-product --region us-east-1
```

## 🎯 Next Steps

1. ✅ Set up infrastructure with Terraform
2. ✅ Push code to GitHub
3. ✅ Verify images in ECR
4. 📋 Create Kubernetes deployment manifests
5. 📋 Deploy product/login/order services to EKS
6. 📋 Add monitoring and payment flows
7. 📋 Configure ingress for storefront access

