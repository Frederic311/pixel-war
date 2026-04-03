# IaC - Terraform and Ansible

This folder provides a local IaC workflow for the Pixel War project.

## Structure
- `terraform/`: local provisioning workflow (kind cluster + manifests)
- `ansible/`: local configuration/deployment playbook

## Terraform usage (Windows/PowerShell)
```powershell
cd pixel-war/infra/terraform
terraform init
terraform plan -var "redis_password=YOUR_STRONG_PASSWORD"
terraform apply -var "redis_password=YOUR_STRONG_PASSWORD"
```

Terraform creates/updates:
- kind cluster (`pixelwar` by default)
- ingress-nginx
- app manifests
- observability manifests
- redis secret from variable `redis_password`

## Ansible usage (Linux/WSL/macOS shell)
```bash
cd pixel-war/infra/ansible
ansible-playbook playbook.yml -e "redis_password=YOUR_STRONG_PASSWORD"
```

Ansible does:
- CLI checks (`kubectl`, `kind`, `docker`)
- cluster creation
- ingress install
- local image build/load
- app + observability deployment
- rollout checks

## Notes
- This IaC setup is local-first (kind), without a cloud provider.
- Uses Terraform as the main IaC entry point.
- Keeps Ansible as an alternative local deploy/configuration orchestrator.
