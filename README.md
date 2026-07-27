# Code Repository - Application Source Code

This folder contains the application source code that will be built and pushed to ECR via GitHub Actions.

## Structure

```
code-repo/
├── api/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── web/
│   ├── Dockerfile
│   └── index.html
├── worker/
│   ├── Dockerfile
│   └── worker.py
└── .github/workflows/
    └── build-and-push.yml
```

## Services

### API Service (lwplabs-api)
- Python-based REST API
- Runs on port 5000
- Builds and pushes to ECR

### Web Service (lwplabs-web)
- Static website
- Runs on port 80
- Nginx-based

### Worker Service (lwplabs-worker)
- Background job processor
- Runs scheduled tasks
- Python-based

## GitHub Actions Workflow

The workflow automatically:
1. Triggers on push to main branch
2. Builds Docker images for each service
3. Pushes images to ECR with tags: `latest` and `git-sha`
4. Tags images with environment (dev/staging/prod)

## Pushing to GitHub

```bash
# Initialize git repo
git init
git remote add origin https://github.com/YOUR_USERNAME/lwplabs.git

# Add files
git add .
git commit -m "Initial commit: Application source code"

# Push to GitHub
git branch -M main
git push -u origin main
```

## Required GitHub Secrets

Add these secrets in GitHub repository settings:
- `AWS_ACCESS_KEY_ID` - IAM user access key
- `AWS_SECRET_ACCESS_KEY` - IAM user secret key
- `AWS_REGION` - AWS region (e.g., us-east-1)

## Build & Push Images

Images are automatically built and pushed on each commit to main:

```
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/lwplabs-api:latest
{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/lwplabs-api:sha-{GIT_SHA}
```
