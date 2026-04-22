# Jenkins on Kubernetes

This folder contains a simple Jenkins server deployment for an internal Kubernetes cluster.

## Files

- `namespace.yaml` creates the `jenkins` namespace
- `serviceaccount-rbac.yaml` gives Jenkins access to create and clean up Kubernetes agent pods
- `pvc.yaml` stores Jenkins state in `/var/jenkins_home`
- `deployment.yaml` runs the Jenkins controller
- `service.yaml` exposes Jenkins inside the cluster
- `ingress.yaml` is an optional ingress example
- `jobs/gitleaks-multirepo-pipeline.groovy` is an optional Job DSL script that creates the pipeline job

## Apply Order

```bash
kubectl apply -f k8s/jenkins/namespace.yaml
kubectl apply -f k8s/jenkins/serviceaccount-rbac.yaml
kubectl apply -f k8s/jenkins/pvc.yaml
kubectl apply -f k8s/jenkins/deployment.yaml
kubectl apply -f k8s/jenkins/service.yaml
kubectl apply -f k8s/jenkins/ingress.yaml
```

## Jenkins Plugins

Install these plugins in Jenkins before creating the job:

- Kubernetes
- Pipeline
- Git
- GitHub
- Job DSL (optional)

## Pipeline Job

Create a Pipeline job named `gitleaks-multirepo-scan` and point it to this repository's `Jenkinsfile`.

If you prefer to create the job automatically, load `jobs/gitleaks-multirepo-pipeline.groovy` from a Jenkins seed job.

The job supports:

- full-history scan for original and duplicate repositories
- single-branch scan for original and duplicate repositories
- tracked file comparison between two repos
- new, missing, and modified file comparison
- optional text diff preview for modified files
- remote branch comparison
- scanning only the original repo
- scanning only the duplicate repo
