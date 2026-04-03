locals {
  root_dir    = abspath("${path.module}/../..")
  kind_config = abspath("${path.module}/${var.kind_config_path}")
}

resource "null_resource" "kind_cluster" {
  triggers = {
    cluster_name = var.cluster_name
    kind_config  = local.kind_config
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = <<-EOT
      $name = "${var.cluster_name}"
      $exists = kind get clusters | Select-String -SimpleMatch $name
      if (-not $exists) {
        kind create cluster --name $name --config "${local.kind_config}"
      }
    EOT
  }

  provisioner "local-exec" {
    when        = destroy
    interpreter = ["PowerShell", "-Command"]
    command     = "kind delete cluster --name ${self.triggers.cluster_name}"
  }
}

resource "null_resource" "ingress_nginx" {
  depends_on = [null_resource.kind_cluster]

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = <<-EOT
      kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
      kubectl wait --namespace ingress-nginx --for=condition=available deploy/ingress-nginx-controller --timeout=180s
    EOT
  }
}

resource "null_resource" "deploy_k8s" {
  count      = var.deploy_manifests ? 1 : 0
  depends_on = [null_resource.ingress_nginx]

  triggers = {
    cluster_name = var.cluster_name
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = <<-EOT
      Set-Location "${local.root_dir}"

      kubectl apply -f k8s/00-namespace.yaml
      kubectl create secret generic pixelwar-secrets -n pixelwar --from-literal=redis_password="${var.redis_password}" --dry-run=client -o yaml | kubectl apply -f -
      kubectl apply -f k8s/01-redis-headless.yaml
      kubectl apply -f k8s/01-redis-statefulset.yaml
      kubectl apply -f k8s/02-backend-deployment-service.yaml
      kubectl apply -f k8s/03-frontend-deployment-service.yaml
      kubectl apply -f k8s/04-ingress.yaml
      kubectl apply -f k8s/05-networkpolicies.yaml
      kubectl apply -f k8s/observability/06-observability.yaml
    EOT
  }
}
