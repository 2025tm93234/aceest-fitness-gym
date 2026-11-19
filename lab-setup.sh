#!/usr/bin/env bash
# Rebuild the Prayogshala platform after a lab reset. Run as root:  sudo bash lab-setup.sh
# Idempotent: it only does what is missing.
#   - jenkins user gets Docker access
#   - minikube + kubectl installed (into /usr/bin so sudo and Jenkins can find them)
#   - Minikube cluster started AS the jenkins user (so pipelines can run kubectl), ingress enabled
#   - SonarQube container started
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "run as root: sudo bash $0"; exit 1; }
MINIKUBE_CPUS="${MINIKUBE_CPUS:-2}"
MINIKUBE_MEMORY="${MINIKUBE_MEMORY:-2200}"

echo "== 1/5 Docker access for jenkins"
if ! id -nG jenkins | tr ' ' '\n' | grep -qx docker; then
  usermod -aG docker jenkins
  systemctl restart jenkins
  echo "added jenkins to the docker group and restarted Jenkins"
fi
sudo -u jenkins -H docker ps >/dev/null && echo "jenkins can use Docker"

echo "== 2/5 minikube + kubectl"
if ! command -v minikube >/dev/null; then
  curl -fsSL -o /usr/bin/minikube https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
  chmod +x /usr/bin/minikube
fi
if ! command -v kubectl >/dev/null; then
  curl -fsSL -o /usr/bin/kubectl "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x /usr/bin/kubectl
fi
minikube version --short; kubectl version --client | head -1

echo "== 3/5 Minikube cluster (as jenkins)"
if ! sudo -u jenkins -H minikube status >/dev/null 2>&1; then
  sudo -u jenkins -H minikube start --driver=docker --cpus="$MINIKUBE_CPUS" --memory="$MINIKUBE_MEMORY"
fi
sudo -u jenkins -H minikube addons enable ingress >/dev/null
sudo -u jenkins -H kubectl get nodes

echo "== 4/5 SonarQube"
if docker ps -a --format '{{.Names}}' | grep -qx sonarqube; then
  docker start sonarqube >/dev/null
else
  docker run -d --name sonarqube --restart unless-stopped -p 9000:9000 \
    -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
    -e SONAR_WEB_JAVAOPTS="-Xmx512m" -e SONAR_CE_JAVAOPTS="-Xmx512m" \
    -e SONAR_SEARCH_JAVAOPTS="-Xms512m -Xmx512m" \
    -v sonar_data:/opt/sonarqube/data -v sonar_logs:/opt/sonarqube/logs \
    -v sonar_ext:/opt/sonarqube/extensions sonarqube:community >/dev/null
fi

echo "== 5/5 status"
docker ps --format 'table {{.Names}}\t{{.Status}}'
sudo -u jenkins -H kubectl -n ingress-nginx get pods
free -h | head -2
echo "SonarQube takes about 2 minutes to answer on http://localhost:9000"
