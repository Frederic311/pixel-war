# ---- Build stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Installer dépendances système minimales
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Mettre à jour les outils Python pour éviter les vulnérabilités connues
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copier requirements
COPY requirements.txt .

# Installer dépendances dans un dossier isolé
RUN pip install --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim

WORKDIR /app

# Mettre à jour les outils Python dans l'image finale aussi (scan Trivy)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copier les dépendances installées
COPY --from=builder /install /usr/local

# Copier le code
COPY . .

# Créer un user non-root
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]