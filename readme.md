
## Présentation
Pixel War est une application collaborative en temps réel avec une grille partagée 50x50 :
- Frontend React
- Backend FastAPI
- Redis pour la persistance

Le projet est orienté DevOps : conteneurisation, orchestration Kubernetes, sécurité, CI/CD et observabilité.

## Choix techniques (résumé)
- Environnement local sans cloud provider : choix assumé pour valider toute la chaîne DevOps de manière reproductible sur machine de dev.
- Backend en 2 pods : améliore la résilience (continuité de service si un pod tombe).
- Redis StatefulSet + stockage persistant : l'état de la grille survit aux redémarrages.
- Sécurité K8s : Secret, NetworkPolicies, conteneurs non-root, capabilities minimales.
- CI/CD : lint/tests, build, scan sécurité Trivy, push images, déploiement K8s conditionnel.

## État actuel implémenté
- Docker Compose local opérationnel
- Kubernetes opérationnel (namespace, deployments, services, ingress)
- Sécurité K8s mise en place :
	- Secrets
	- NetworkPolicies
	- SecurityContext non-root
- Observabilité : Prometheus + Grafana (dashboard Pixel War)
- CI/CD GitHub Actions : lint/tests, build, scan Trivy, push GHCR, job de déploiement K8s test

## Démarrage rapide en local (Docker Compose)
Depuis `pixel-war/` :
```bash
docker compose up --build
```

Accès :
- Frontend : http://localhost:8080
- Backend : http://localhost:8000

## Lancer le projet sur sa machine 
1. Local rapide : Docker Compose (commande ci-dessus).
2. Kubernetes local (kind) : suivre [pixel-war/k8s/README.md](pixel-war/k8s/README.md).
3. IaC (Terraform/Ansible) : suivre [pixel-war/infra/README.md](pixel-war/infra/README.md).

## Déploiement Kubernetes (kind)
La procédure complète (incluant tests de validation et observabilité) est documentée dans :
- `pixel-war/k8s/README.md`

## CI/CD
Workflow GitHub Actions :
- `.github/workflows/ci-cd.yml`

Secrets CI attendus :
- `REDIS_PASSWORD` : mot de passe Redis injecté au déploiement

### Ajouter les GitHub Secrets
1. Ouvrir le repo GitHub -> `Settings` -> `Secrets and variables` -> `Actions`.
2. Cliquer `New repository secret` et ajouter :
	 - `REDIS_PASSWORD`

Notes importantes :
- Le job `deploy-k8s-test` s'exécute sur push vers `main` et doit tourner sur un self-hosted runner local Windows avec les labels `self-hosted`, `Windows`, `X64`, `k8s-local`.
- Le workflow installe automatiquement le contrôleur Ingress NGINX s'il n'est pas déjà présent sur le cluster.
- Si aucun runner local compatible n'est online, le job de déploiement reste en attente.
- Le job `iac-apply` ne se lance pas automatiquement : il faut un lancement manuel (`workflow_dispatch`) avec `apply_iac=true`.
- Projet local-first : le déploiement cible un cluster kind local (pas de cloud provider obligatoire).

## Observabilité
Manifests Prometheus + Grafana :
- `pixel-war/k8s/observability/06-observability.yaml`

Dashboard Grafana inclus :
- Pixel modifies (total)
- API up targets
- Pixel updates / min

## Accès local (port-forward)
Après un déploiement Kubernetes local, utiliser ces commandes pour accéder à l'application et aux métriques.

### 1) Pixel War (Ingress)
Dans un terminal dédié :
```powershell
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80
```
Puis ouvrir :
- http://pixelwar.local:8080

Sous Windows, vérifier le fichier hosts :
`C:\Windows\System32\drivers\etc\hosts`

Entrée attendue :
`127.0.0.1 pixelwar.local`

### 2) Prometheus (métriques brutes)
Dans un second terminal :
```powershell
kubectl -n monitoring port-forward svc/prometheus 9090:9090
```
Puis ouvrir :
- http://127.0.0.1:9090

### 3) Grafana (dashboard)
Dans un troisième terminal :
```powershell
kubectl -n monitoring port-forward svc/grafana 3000:3000
```
Puis ouvrir :
- http://127.0.0.1:3000

Identifiants par défaut Grafana (si non modifiés) :
- user : admin
- password : admin

## Prochaines étapes
- Terraform + Ansible (provisioning/configuration infra)

l'application est disponible sur http://pixelwar.local:8080 si le hosts Windows contient 127.0.0.1 pixelwar.local après la pipeline.


## Documentation détaillée
- Déploiement K8s, tests et observabilité : [pixel-war/k8s/README.md](pixel-war/k8s/README.md)
- IaC Terraform/Ansible : [pixel-war/infra/README.md](pixel-war/infra/README.md)

## Auteurs
- Yvan Youmbi
- Frédéric Onana

Module DevOps – ISIMA 2026.
