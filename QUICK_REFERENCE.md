# Quick Reference Guide

## File Overview

### Application Code
```
api/           → Flask REST API (port 5000)
web/           → Nginx static site (port 80)
worker/        → Python background worker
```

### CI/CD Pipeline
```
.github/workflows/build-and-push.yml → GitHub Actions workflow
```

### Documentation
```
AWS_ARCHITECTURE.drawio     → Visual diagram (open with draw.io)
ARCHITECTURE_DETAILED.md    → Complete technical documentation
GITHUB_ACTIONS_SETUP.md     → Step-by-step setup guide
README.md                   → Quick start guide
QUICK_REFERENCE.md          → This file
```

---

## Quick Commands

### Push Code to Trigger Build
```bash
# Make changes to api/, web/, or worker/
git add .
git commit -m "feature: description"

# Push to trigger GitHub Actions
git push origin dev     # Deploy to dev environment
git push origin stg     # Deploy to staging
git push origin master  # Deploy to production
```

### Check Build Status
1. Go to GitHub repository
2. Click **Actions** tab
3. View workflow runs and logs

### View Images in ECR
```bash
# List images in app-api repository
aws ecr describe-images \
  --repository-name app-api \
  --region us-east-1

# Same for app-web and app-worker
```

### Deploy to EKS (Example)
```bash
# Create deployment using dev image
kubectl set image deployment/api \
  api=ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/app-api:dev

# Verify
kubectl get pods
kubectl logs pod-name
```

---

## Branch Strategy

```
dev branch      → Development builds (replicas: 1-2)
                  Image tags: :dev, :sha-xxx, :timestamp

stg branch      → Staging builds (replicas: 2)
                  Image tags: :stg, :sha-xxx, :timestamp

master branch   → Production builds (replicas: 3)
                  Image tags: :master, :latest, :sha-xxx
```

---

## Image Tags Explained

Each build creates 4 image tags:

| Tag | Example | Purpose |
|-----|---------|---------|
| Branch | `app-api:dev` | Branch-specific (dev/stg/master) |
| Commit | `app-api:sha-a1b2c3` | Exact code version |
| Timestamp | `app-api:20240127-143022` | When built |
| Latest | `app-api:latest` | Latest (master only) |

---

## GitHub Actions Jobs

```
1. setup
   └─ Creates build matrix (api, web, worker)

2. build-and-push (parallel for 3 services)
   ├─ api
   │  ├─ Checkout code
   │  ├─ Configure AWS
   │  ├─ Build Docker image
   │  ├─ Scan for vulnerabilities
   │  └─ Push to ECR
   ├─ web
   │  └─ (same steps)
   └─ worker
      └─ (same steps)

3. test-deployment
   └─ Display ECR repositories & image info

4. notify
   └─ Send build status
```

---

## Environment Setup (First Time)

### 1. Create GitHub Secrets

Go to GitHub repository → Settings → Secrets and variables → Actions

Add:
```
AWS_ACCESS_KEY_ID       → Your IAM access key
AWS_SECRET_ACCESS_KEY   → Your IAM secret key
```

### 2. Create Git Branches

```bash
git checkout -b dev
git push -u origin dev

git checkout -b stg
git push -u origin stg

git checkout -b master
git push -u origin master
```

### 3. Push Code

```bash
git add .
git commit -m "Initial commit"
git push origin dev
```

**Result:** GitHub Actions triggers automatically!

---

## Viewing Architecture Diagram

1. Download this repository
2. Open `AWS_ARCHITECTURE.drawio` with [draw.io](https://draw.io)
3. Or import to draw.io:
   - Go to draw.io
   - File → Open → Select `AWS_ARCHITECTURE.drawio`
4. Export to PNG/PDF/SVG as needed

---

## Common Tasks

### Check Build Logs
1. Go to GitHub repository
2. Click **Actions** tab
3. Click on workflow run
4. Click on job (build-and-push)
5. Click on service (api, web, worker)
6. View logs

### Rollback Deployment
```bash
# View previous versions
kubectl rollout history deployment/api

# Rollback to previous version
kubectl rollout undo deployment/api

# Rollback to specific revision
kubectl rollout undo deployment/api --to-revision=2
```

### Update Specific Service
```bash
# Use different image tag
kubectl set image deployment/api \
  api=ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/app-api:sha-abc123

# Use latest from master
kubectl set image deployment/api \
  api=ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/app-api:latest
```

### Scale Replicas
```bash
# Scale API deployment to 5 replicas
kubectl scale deployment api --replicas=5

# Auto-scaling
kubectl autoscale deployment api --min=2 --max=10
```

---

## Troubleshooting

### Build Failed: "Access Denied to ECR"
**Cause:** GitHub Secrets not configured correctly
```bash
Solution:
1. Check GitHub Secrets are set
2. Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
3. Check IAM user has ECR permissions
```

### Build Failed: "Dockerfile not found"
**Cause:** File path incorrect
```bash
Solution:
1. Verify Dockerfile exists in:
   - api/Dockerfile
   - web/Dockerfile
   - worker/Dockerfile
2. Check spelling and case
```

### Images Not in ECR
**Cause:** Repository not created
```bash
Solution:
1. Check repository exists:
   aws ecr describe-repositories --region us-east-1
2. Check ECR images:
   aws ecr describe-images --repository-name app-api
3. Check workflow logs for errors
```

### Pod Not Starting
**Cause:** Image not found or wrong tag
```bash
Solution:
1. Verify image exists in ECR
2. Check image URL in deployment manifest
3. Verify pod has ECR pull credentials
4. Check pod logs: kubectl logs pod-name
```

---

## Key Concepts

### Microservices
Three independent services that work together:
- **API** - Handles REST requests
- **Web** - Serves frontend
- **Worker** - Processes background jobs

### Docker Images
Packaged applications with all dependencies:
- Built in GitHub Actions
- Stored in AWS ECR
- Deployed to EKS pods

### Environments
```
Development (dev)   → Testing new features
Staging (stg)       → Pre-production testing
Production (master) → Customer-facing
```

### CI/CD Pipeline
Automated process:
```
Code → Build → Test → Push → Ready to Deploy
```

---

## Performance Tips

### Faster Builds
- Use layer caching (Docker)
- Minimize image size
- Use build matrix (parallel)

### Efficient Deployments
- Use smaller image tags (`:latest` vs full URL)
- Enable auto-scaling
- Set resource requests & limits

### Cost Optimization
- Use t3 instances (burstable)
- Auto-scale down when idle
- Clean up old ECR images (lifecycle policy)

---

## Security Checklist

- ✅ GitHub Secrets configured
- ✅ AWS IAM user minimal permissions
- ✅ No credentials in code
- ✅ No credentials in git history
- ✅ ECR image scanning enabled
- ✅ Private subnets for EKS nodes
- ✅ Security groups configured
- ✅ Pod security policies (optional)

---

## Further Reading

- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [EKS Documentation](https://docs.aws.amazon.com/eks/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

## Support

For issues or questions:
1. Check `ARCHITECTURE_DETAILED.md` for technical details
2. Review `GITHUB_ACTIONS_SETUP.md` for setup help
3. Check GitHub Actions logs for build errors
4. Review pod logs: `kubectl logs pod-name`
