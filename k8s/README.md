# Pixel War – Déploiement Kubernetes

## Prérequis
- `kubectl` configuré sur un cluster accessible
- `kind` (recommandé pour environnement local)
- Ingress NGINX installé. Pour un cluster local kind (ou sans LB) :
  ```bash
  kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
  kubectl wait --namespace ingress-nginx --for=condition=available deploy/ingress-nginx-controller --timeout=120s
  kubectl get svc -n ingress-nginx
  ```
  (le service `ingress-nginx-controller` doit être présent en port 80)

Note CI/CD : le job `deploy-k8s-test` installe automatiquement ce contrôleur s'il est absent.

## Préparer les images locales (workflow validé)
Depuis `pixel-war/` :
```bash
docker compose build
kind load docker-image pixelwar-backend:local --name pixelwar
kind load docker-image pixelwar-frontend:local --name pixelwar
```

## Déploiement
```bash
cd pixel-war/k8s
kubectl apply -f 00-namespace.yaml
kubectl apply -f 00-secrets.yaml
kubectl apply -f 01-redis-headless.yaml
kubectl apply -f 01-redis-statefulset.yaml
kubectl apply -f 02-backend-deployment-service.yaml
kubectl apply -f 03-frontend-deployment-service.yaml
kubectl apply -f 04-ingress.yaml
kubectl apply -f 05-networkpolicies.yaml
kubectl apply -f observability/06-observability.yaml
```

## Accès via ingress (port-forward)
```bash
# choisir un port libre local, ex : 8090 (changez si occupé)
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8090:80
# ajouter dans /etc/hosts (Linux/macOS) ou hosts (Windows) :
127.0.0.1 pixelwar.local
# test API
curl -H "Host: pixelwar.local" http://127.0.0.1:8090/api/grid
```
Ouvrir dans le navigateur : `http://pixelwar.local:8090/`

Sous Windows, le port-forward est généralement nécessaire pour exposer Ingress depuis kind vers le navigateur local.

PowerShell (Windows) :
```powershell
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8090/api/grid" -Headers @{ Host = "pixelwar.local" }
```

Fichier hosts Windows :
`C:\Windows\System32\drivers\etc\hosts`

## Tests de validation
1. Pods Ready
```bash
kubectl get pods -n pixelwar
```
Attendu : `pixelwar-backend`, `pixelwar-frontend`, `redis` en `READY 1/1`.

2. API via ingress
```bash
curl -H "Host: pixelwar.local" http://127.0.0.1:8090/api/grid
```
Attendu : HTTP 200 et JSON avec la clé `grid`.

3. Frontend via ingress
- Ouvrir `http://pixelwar.local:8090/`
- Cliquer un pixel et vérifier la mise à jour.

4. Observabilité
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
kubectl port-forward -n monitoring svc/grafana 3000:3000
```
- Prometheus : `http://127.0.0.1:9090` (target `pixelwar-backend` UP)
- Grafana : `http://127.0.0.1:3000` (admin/admin), dashboard `Pixel War Overview`

⚠️ L'entrée hosts est obligatoire : sans `127.0.0.1 pixelwar.local` la résolution du nom échoue et l'app ne répond pas. Vous pouvez ajouter aussi `127.0.0.1 pixelwar` si vous souhaitez utiliser `http://pixelwar:8090/` en plus.

## Nettoyage
```bash
kubectl delete -f observability/06-observability.yaml
kubectl delete -f 04-ingress.yaml
kubectl delete -f 05-networkpolicies.yaml
kubectl delete -f 03-frontend-deployment-service.yaml
kubectl delete -f 02-backend-deployment-service.yaml
kubectl delete -f 01-redis-statefulset.yaml
kubectl delete -f 01-redis-headless.yaml
kubectl delete -f 00-secrets.yaml
kubectl delete -f 00-namespace.yaml
```

## Repartir de zéro (fresh)
```bash
kubectl delete -f observability/06-observability.yaml
kubectl delete -f 04-ingress.yaml
kubectl delete -f 05-networkpolicies.yaml
kubectl delete -f 03-frontend-deployment-service.yaml
kubectl delete -f 02-backend-deployment-service.yaml
kubectl delete -f 01-redis-statefulset.yaml
kubectl delete -f 01-redis-headless.yaml
kubectl delete -f 00-secrets.yaml
kubectl delete -f 00-namespace.yaml

# redeployer ensuite avec la section Déploiement ci-dessus
```

## Secrets
- Le mot de passe Redis est défini dans 00-secrets.yaml (valeur par défaut: CHANGE_ME).
- Pour un usage réel, remplacement de la valeur par un placeholder en Git et crée le secret au runtime avec `kubectl create secret ...`.

## Notes
- Les manifests applicatifs utilisent `pixelwar-frontend:local` et `pixelwar-backend:local`.
- En CI/CD, les images déployées sont injectées dynamiquement avec `kubectl set image`.

