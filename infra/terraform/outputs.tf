output "cluster_name" {
  value       = var.cluster_name
  description = "Kind cluster name"
}

output "next_steps" {
  value = <<-EOT
    1) Build and load local images:
       docker compose build
       kind load docker-image pixelwar-backend:local --name ${var.cluster_name}
       kind load docker-image pixelwar-frontend:local --name ${var.cluster_name}

    2) Access app:
       kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8090:80
       Open http://pixelwar.local:8090/
  EOT
}
