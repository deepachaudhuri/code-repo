# GitHub Actions Setup Guide

## Prerequisites

1. GitHub account and repository created
2. AWS IAM user with ECR permissions
3. AWS credentials configured

## Step 1: Create GitHub Repository

```bash
# Navigate to code-repo
cd code-repo

# Initialize git repository
git init

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/lwplabs.git

# Create main branch
git branch -M main

# Add all files
git add .

# Make initial commit
git commit -m "feat: Initial commit - Application source code with 3 services"

# Push to GitHub
git push -u origin main
```

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
        "ecr:ListImages"
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
2. Click on the workflow run
3. Monitor build progress for each service:
   - ✅ api
   - ✅ web
   - ✅ worker

## Step 5: Verify ECR Images

After successful build, images are available in ECR:

```bash
# List images in each repository
aws ecr describe-images \
  --repository-name lwplabs-api \
  --region us-east-1

aws ecr describe-images \
  --repository-name lwplabs-web \
  --region us-east-1

aws ecr describe-images \
  --repository-name lwplabs-worker \
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
- `latest` - Latest version
- `<branch-name>` - Branch name (e.g., main, develop)
- `sha-<commit-sha>` - Commit SHA for traceability
- `<timestamp>` - Build timestamp for versioning

### Example Image Names

```
123456789012.dkr.ecr.us-east-1.amazonaws.com/lwplabs-api:latest
123456789012.dkr.ecr.us-east-1.amazonaws.com/lwplabs-api:main
123456789012.dkr.ecr.us-east-1.amazonaws.com/lwplabs-api:sha-abc1234
123456789012.dkr.ecr.us-east-1.amazonaws.com/lwplabs-api:20240127-143022
```

## Next Steps

1. ✅ Set up GitHub repository
2. ✅ Add AWS credentials to GitHub Secrets
3. ✅ Push code to trigger workflow
4. ✅ Verify images in ECR
5. 📋 Create Kubernetes manifests to deploy to EKS
6. 📋 Set up deployment pipeline (optional)

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [AWS Actions](https://github.com/aws-actions)
