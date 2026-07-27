# Application Repository - Multi-Service Microservices

This folder contains the application source code for three microservices that will be built and pushed to ECR via GitHub Actions.

## Structure

```
├── api/
│   ├── Dockerfile       # Multi-stage Python build
│   ├── main.py          # Flask REST API
│   └── requirements.txt  # Dependencies
├── web/
│   ├── Dockerfile       # Nginx-based static site
│   ├── index.html       # HTML content
│   └── nginx.conf       # Configuration
├── worker/
│   ├── Dockerfile       # Python worker process
│   ├── worker.py        # Background jobs
│   └── requirements.txt  # Dependencies
└── .github/workflows/
    └── build-and-push.yml   # CI/CD pipeline
```

## Services

### API Service
- **Language:** Python (Flask)
- **Port:** 5000
- **Purpose:** REST API backend
- **ECR Name:** `app-api`

### Web Service
- **Language:** Nginx
- **Port:** 80
- **Purpose:** Static website / frontend
- **ECR Name:** `app-web`

### Worker Service
- **Language:** Python
- **Purpose:** Background job processor
- **ECR Name:** `app-worker`

## GitHub Actions Workflow

The workflow automatically:
1. **Triggers on:** Push to `dev`, `stg`, or `master` branches
2. **Builds:** All 3 services in parallel
3. **Pushes:** Images to ECR with environment-specific tags
4. **Tags:** Each image with:
   - `latest` - Most recent build
   - `branch-name` - Branch-specific (dev, stg, master)
   - `sha-{commit}` - Commit hash for traceability
   - `{timestamp}` - Build timestamp

## Branch Strategy

| Branch | Environment | ECR Tag | Purpose |
|--------|-------------|---------|----------|
| `dev` | Development | `dev` | Feature development |
| `stg` | Staging | `stg` | Testing & QA |
| `master` | Production | `master`, `latest` | Production deployment |

## Pushing to GitHub

```bash
# Initialize git repo
git init
git remote add origin https://github.com/YOUR_USERNAME/app.git

# Add files
git add .
git commit -m "Initial commit: Application source code"

# Create and push to dev branch
git branch -M dev
git push -u origin dev

# Create stg and master branches
git checkout -b stg
git push -u origin stg

git checkout -b master
git push -u origin master
```

## Required GitHub Secrets

Add these secrets in GitHub repository settings:
- `AWS_ACCESS_KEY_ID` - IAM user access key
- `AWS_SECRET_ACCESS_KEY` - IAM user secret key
- `AWS_REGION` - AWS region (e.g., us-east-1)

## Build & Push Images

Images are automatically built and pushed on each commit:

```
Development (dev branch):
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/app-api:dev
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/app-api:sha-{GIT_SHA}

Staging (stg branch):
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/app-api:stg
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/app-api:sha-{GIT_SHA}

Production (master branch):
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/app-api:master
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/app-api:latest
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/app-api:sha-{GIT_SHA}
```
