# OpenCode Server Kubernetes Deployment

Kubernetes manifests for deploying OpenCode server with custom agents.

## Files

| File | Description |
|------|-------------|
| `opencode-deployment.yaml` | Deployment for OpenCode server |
| `opencode-service.yaml` | ClusterIP service for internal access |
| `secrets.yaml` | API keys for LLM providers |

## Architecture

OpenCode and the Telegram webhook share a persistent volume:

```
┌─────────────────┐     ┌─────────────────┐
│ telegram-webhook│     │  opencode-server│
│                 │     │                 │
│  Creates        │     │  Works on       │
│  projects in    │     │  projects in    │
│  /data/projects │     │  /data/projects │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────┴──────┐
              │ swe-agents- │
              │    data     │
              │    (PVC)    │
              └─────────────┘
```

Both pods use `podAffinity` with label `storage-group: swe-agents-shared` to run on the same node.

## Custom Agents

The Docker image includes these custom agents (defined in `.config/`):

| Agent | Description |
|-------|-------------|
| `pm-break-down-agent` | Primary PM agent that coordinates work |
| `research-agent` | Research and analysis subagent |
| `backend-agent` | Python backend expert |
| `frontend-agent` | Multi-platform frontend expert |
| `qa-agent` | QA and Playwright automation |
| `cloud-agent` | DevOps and infrastructure |

## Deployment

### 1. Create Namespace and Shared PVC

```bash
kubectl create namespace swe-agents
kubectl apply -f ../../tg-webhook/kubernetes/pvc.yaml
```

### 2. Configure Secrets

Edit `secrets.yaml` with your API keys, then apply:

```bash
kubectl apply -f secrets.yaml
```

### 3. Deploy

```bash
kubectl apply -f opencode-deployment.yaml
kubectl apply -f opencode-service.yaml
```

### 4. Verify

```bash
# Check pods are on same node
kubectl get pods -n swe-agents -o wide -l storage-group=swe-agents-shared

# Check logs
kubectl logs -f deployment/opencode-server -n swe-agents

# Test health endpoint
kubectl port-forward svc/opencode-server 4000:4000 -n swe-agents
curl http://localhost:4000/global/health
```

## Building the Docker Image

```bash
cd opencode
docker build -t ritouu/opencode:latest .
docker push ritouu/opencode:latest
```

## Troubleshooting

### Pods on different nodes

```bash
# Delete pods to reschedule together
kubectl delete pods -n swe-agents -l storage-group=swe-agents-shared
```

### Check agent configuration

```bash
kubectl exec -it deployment/opencode-server -n swe-agents -- cat /root/.config/opencode/opencode.json
```
