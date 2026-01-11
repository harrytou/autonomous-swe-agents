# OpenCode Server Kubernetes Deployment

This directory contains Kubernetes manifests for deploying an OpenCode server instance.

**Official Documentation**: https://opencode.ai/docs/server/

## Prerequisites

- Kubernetes cluster (1.21+)
- `kubectl` configured to access your cluster
- Ingress controller installed (nginx-ingress recommended)
- Persistent volume provisioner (for workspace storage)
- At least one LLM provider API key (Anthropic, OpenAI, or Google)

## Files

| File | Description |
|------|-------------|
| `opencode-deployment.yaml` | Deployment, PVC, Secret, and ConfigMap for OpenCode server |
| `opencode-service.yaml` | Service and Ingress for exposing OpenCode server |

## Quick Start

### 1. Configure API Keys

Before deploying, update the Secret in `opencode-deployment.yaml` with your actual API keys:

```yaml
stringData:
  anthropic-api-key: "YOUR_ACTUAL_ANTHROPIC_API_KEY"
  openai-api-key: "YOUR_ACTUAL_OPENAI_API_KEY"
```

**Recommended**: Create the secret separately using kubectl:

```bash
kubectl create secret generic opencode-secrets \
  --from-literal=anthropic-api-key=YOUR_ANTHROPIC_KEY \
  --from-literal=openai-api-key=YOUR_OPENAI_KEY
```

### 2. Update Ingress Host

Edit `opencode-service.yaml` and replace `opencode.example.com` with your actual domain:

```yaml
rules:
  - host: your-domain.com
```

### 3. Deploy

```bash
# Create namespace (optional)
kubectl create namespace opencode

# Apply all manifests
kubectl apply -f opencode-deployment.yaml -n opencode
kubectl apply -f opencode-service.yaml -n opencode
```

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n opencode -l app=opencode

# Check services
kubectl get svc -n opencode -l app=opencode

# Check ingress
kubectl get ingress -n opencode

# View logs
kubectl logs -f deployment/opencode-server -n opencode
```

## Configuration Options

### Resource Limits

Adjust CPU and memory based on your workload:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Storage

The default workspace PVC is 10Gi. Modify in `opencode-deployment.yaml`:

```yaml
resources:
  requests:
    storage: 20Gi  # Increase as needed
```

### Replicas

For high availability (note: workspace PVC access mode may need to be RWX):

```yaml
spec:
  replicas: 3
```

## Accessing the Server

### Via Ingress (recommended)

Access at: `http://opencode.example.com` (or your configured domain)

### Via Port Forward (development)

```bash
kubectl port-forward svc/opencode-server 4000:4000 -n opencode
# Access at http://localhost:4000
```

### Via NodePort

Uncomment the NodePort service in `opencode-service.yaml`, then access via:
`http://<node-ip>:30400`

## OpenCode API Endpoints

Once deployed, the OpenCode server exposes these endpoints (see [OpenAPI spec](https://opencode.ai/openapi.json)):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/global/health` | GET | Health check - returns `{ healthy: true, version: string }` |
| `/global/event` | GET | Server-Sent Events (SSE) for real-time events |
| `/global/dispose` | POST | Clean up and dispose all instances |
| `/doc` | GET | OpenAPI specification |
| `/config` | GET/PATCH | Configuration management |
| `/session` | GET/POST | Session management |
| `/project` | GET | Project information |
| `/pty` | GET/POST | PTY (pseudo-terminal) sessions |
| `/pty/:id/connect` | WebSocket | Connect to PTY session |

## Integration with OpenPortal

To connect OpenPortal to your Kubernetes-deployed OpenCode:

```bash
# Create an OpenCode client pointing to the K8s service
export OPENCODE_URL=http://opencode.example.com:4000
```

## Troubleshooting

### Pod not starting

```bash
# Check pod events
kubectl describe pod -l app=opencode -n opencode

# Check logs
kubectl logs -l app=opencode -n opencode --tail=100
```

### Connection refused

1. Verify the service is running: `kubectl get svc -n opencode`
2. Check pod readiness: `kubectl get pods -n opencode`
3. Test internal connectivity: 
   ```bash
   kubectl run test --rm -it --image=busybox -- wget -qO- http://opencode-server:4000
   ```

### API key errors

Verify secrets are properly mounted:
```bash
kubectl exec -it deployment/opencode-server -n opencode -- env | grep API_KEY
```

## Security Recommendations

1. **Use Kubernetes Secrets** for API keys (done by default)
2. **Enable TLS** on Ingress with cert-manager
3. **Network Policies** to restrict access to the OpenCode service
4. **RBAC** to control who can access the namespace

Example Network Policy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: opencode-network-policy
  namespace: opencode
spec:
  podSelector:
    matchLabels:
      app: opencode
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - port: 4000
```

## Image Updates

The official OpenCode Docker image is: `ghcr.io/anomalyco/opencode`

To use a newer OpenCode version:

```bash
# Check latest release at: https://github.com/anomalyco/opencode/releases
kubectl set image deployment/opencode-server \
  opencode=ghcr.io/anomalyco/opencode:NEW_VERSION -n opencode
```

## Server Command Options

The OpenCode server supports these CLI options:

```bash
opencode serve [options]

Options:
  --port <number>      Port to listen on (default: 0 = dynamic)
  --hostname <string>  Hostname to listen on (default: 127.0.0.1)
  --mdns               Enable mDNS service discovery (sets hostname to 0.0.0.0)
  --cors <domains>     Additional domains to allow for CORS
```
