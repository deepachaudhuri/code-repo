# ECR ImagePullBackOff Fix - Complete Guide

## Problem: Pods Stuck in ImagePullBackOff

When deploying to EKS, pods fail with:
```
Status: Pending
Reason: ImagePullBackOff
Error: trying and failing to pull image
```

## Root Cause

EKS nodes cannot access ECR (Elastic Container Registry) to pull images. This happens when:

1. **Kubernetes is missing ECR credentials** - No docker-registry secret configured
2. **Node IAM role lacks ECR permissions** - The EC2 instances running the cluster don't have permission to access ECR

## Solution Applied

### ✅ Fix 1: Automatic Secret Creation (IMPLEMENTED)

The GitHub Actions workflow now creates ECR credentials automatically:

**Changes made to `.github/workflows/deploy-to-eks.yml`:**
- Added step: "Create ECR credentials secret"
- Creates a Kubernetes docker-registry secret with ECR credentials
- References AWS IAM user credentials from GitHub Actions secrets
- Runs before any deployment attempts

**Deployment YAML Changes:**
- Updated `imagePullSecrets` in all three deployments:
  - `product-deployment.yaml`
  - `login-deployment.yaml`
  - `order-deployment.yaml`

### How It Works

1. GitHub Actions runner (with AWS credentials) gets ECR login token
2. Creates Kubernetes secret of type `docker-registry`
3. Deployment manifests reference this secret via `imagePullSecrets`
4. Kubernetes uses the secret to authenticate with ECR when pulling images

### ✅ Fix 2: Add Node IAM Role Permissions (OPTIONAL - Long-term)

For a more permanent solution, add ECR permissions to the EKS node IAM role:

**Update `infra-repo/main.tf`:**
```hcl
module "eks" {
  source = "git::https://github.com/deepachaudhuri/aws-modules.git//eks?ref=master"

  cluster_name       = "lwplabs-cluster"
  kubernetes_version = "1.34"
  subnet_ids         = module.vpc.private_subnet_ids

  node_groups = [
    {
      name           = "primary"
      subnet_ids     = module.vpc.private_subnet_ids
      desired_size   = 2
      min_size       = 1
      max_size       = 4
      instance_types = ["t3.medium"]
      disk_size      = 20
      # Add IAM policy for ECR access
      iam_role_policies = {
        AmazonEC2ContainerRegistryPowerUser = {
          policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
        }
      }
    }
  ]

  # ... rest of config
}
```

Then apply: `terraform apply`

## Testing the Fix

1. **Monitor deployment:**
   ```bash
   kubectl get pods -n default -w
   ```

2. **Check pod status:**
   ```bash
   kubectl describe pod <pod-name> -n default
   ```
   Should show `ImagePull` events with successful pulls

3. **View deployment logs:**
   ```bash
   kubectl logs deployment/product -n default
   ```

## Expected Behavior After Fix

- Pods transition from `ImagePullBackOff` → `ContainerCreating` → `Running`
- Services get LoadBalancer IPs assigned
- Health checks pass and replicas are ready

## Verification Commands

```bash
# Check secret exists
kubectl get secret ecr-secret -n default

# Describe secret
kubectl describe secret ecr-secret -n default

# Check pod status
kubectl get pods -n default -o wide

# View detailed pod info
kubectl describe pod <pod-name> -n default

# Check recent events
kubectl get events -n default --sort-by='.lastTimestamp'
```

## GitHub Actions Secrets Required

Ensure these are configured in your GitHub repository:
- `AWS_ACCESS_KEY_ID` - IAM user with ECR access
- `AWS_SECRET_ACCESS_KEY` - Corresponding secret

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Secret not created | Check AWS credentials in GitHub secrets |
| Still ImagePullBackOff | Verify image tag exists in ECR: `aws ecr describe-images --repository-name lwplabs-product --region us-east-1` |
| Pull succeeds but pod crashes | Check container logs: `kubectl logs <pod>` |
| Different namespace issues | Ensure secret created in correct namespace matching `needs.determine-environment.outputs.namespace` |

## Files Modified

1. ✅ `code-repo/.github/workflows/deploy-to-eks.yml` - Added secret creation step
2. ✅ `code-repo/deployments/product-deployment.yaml` - Added imagePullSecrets
3. ✅ `code-repo/deployments/login-deployment.yaml` - Added imagePullSecrets
4. ✅ `code-repo/deployments/order-deployment.yaml` - Added imagePullSecrets
5. ✅ `code-repo/deployments/DEPLOYMENT_GUIDE.md` - Added ECR secret documentation
