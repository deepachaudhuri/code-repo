# GitHub Actions CI/CD Setup Guide

## Branch Strategy

```
dev    → Development environment
stg    → Staging environment  
master → Production environment
```

Each branch automatically builds and deploys with environment-specific tags.

---

## Prerequisites

1. GitHub account and repository created
2. AWS IAM user with ECR permissions
3. AWS credentials configured

## Step 1: Create GitHub Repository

```bash
# Initialize git repository
git init

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/app.git

# Add all files
git add .

# Make initial commit
git commit -m "feat: Initial commit - Multi-service microservices application"

# Create dev branch (for development)
git branch -M dev
git push -u origin dev

# Create stg branch (for staging/testing)
git checkout -b stg
git push -u origin stg

# Create master branch (for production)
git checkout -b master
git push -u origin master
```

**Note:** Typically you would:
- Develop on `dev` branch
- Test on `stg` branch
- Deploy to prod from `master` branch

## Step 2: Add GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Create the following secrets:

### AWS Credentials

```
AWS_ACCESS_KEY_ID
    Value: Your IAM user access key
    
AWS_SECRET_ACCESS_KEY
    Value: Your IAM user secret key
```

### Example IAM Policy (Minimum Permissions)

Create an IAM user with this policy for secure access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:CreateRepository",
        "ecr:GetAuthorizationToken",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:DescribeRepositories",
        "ecr:ListImages",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

## Step 3: Trigger Workflow

The workflow automatically triggers on:
- ✅ Push to `main` or `develop` branches
- ✅ Changes to `api/`, `web/`, `worker/`, or workflow file
- ✅ Pull requests to `main` or `develop`

To manually trigger:

1. Go to **Actions** tab
2. Select **Build and Push to ECR**
3. Click **Run workflow**

## Step 4: Monitor Builds

1. Go to **Actions** tab
2. Click on workflow run
3. Monitor build progress:
   - ✅ setup
   - ✅ build-and-push (api, web, worker in parallel)
   - ✅ test-deployment
   - ✅ notify

## Step 5: Verify ECR Images

After successful build, images are available in ECR:

```bash
# List images in each repository
aws ecr describe-images \
  --repository-name app-api \
  --region us-east-1

aws ecr describe-images \
  --repository-name app-web \
  --region us-east-1

aws ecr describe-images \
  --repository-name app-worker \
  --region us-east-1
```

## Troubleshooting

### Build Failed: "Access Denied"

```
Error: User is not authorized to perform: ecr:GetAuthorizationToken
```

**Solution:** Verify IAM credentials in GitHub Secrets and IAM policy permissions.

### Build Failed: "No such file or directory"

```
Error: open Dockerfile: no such file or directory
```

**Solution:** Ensure Dockerfile is in the correct service directory (api/, web/, worker/).

### Images Not Appearing in ECR

```
aws ecr describe-repositories --region us-east-1
```

**Solution:** Repository might be in different AWS region. Check workflow logs for region used.

## Workflow Details

### Trigger Events

| Event | Trigger |
|-------|---------|
| `push` | Push to main/develop branches |
| `pull_request` | PR to main/develop branches |
| `Manual` | Run workflow button in Actions tab |

### Jobs

1. **setup** - Configure build matrix
2. **build-and-push** - Build and push each service (parallelized)
3. **test-deployment** - Display deployment info
4. **notify** - Send build status

### Image Tags

Each image is tagged with:
- `latest` - Latest stable (from master only)
- `<branch-name>` - Branch-specific (dev, stg, master)
- `sha-<commit-sha>` - Commit hash for traceability
- `<timestamp>` - Build timestamp (YYYYMMDD-HHMMSS)

### Example Image Names

**Development:**
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/app-api:dev
123456789012.dkr.ecr.us-east-1.amazonaws.com/app-api:sha-abc1234
```

**Staging:**
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/app-api:stg
123456789012.dkr.ecr.us-east-1.amazonaws.com/app-api:sha-abc1234
```

**Production:**
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/app-api:master
123456789012.dkr.ecr.us-east-1.amazonaws.com/app-api:latest
123456789012.dkr.ecr.us-east-1.amazonaws.com/app-api:sha-abc1234
```

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Add AWS credentials to GitHub Secrets
3. ✅ Create branches: dev, stg, master
4. ✅ Push code to trigger workflow
5. ✅ Verify images in ECR with environment tags
6. 📋 Create Kubernetes manifests
7. 📋 Deploy to EKS cluster

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [AWS Actions](https://github.com/aws-actions)
