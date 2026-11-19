# Assignment 2: CI/CD for ACEest Fitness & Gym, step by step (Steps 2 to 10)

Where each command runs is shown in square brackets:
**[LAPTOP]** your own computer, **[LAB]** the Prayogshala terminal, **[BROWSER]** a web page.
Replace `<user>` with your Docker Hub username. Repo: `https://github.com/2025tm93234/aceest-fitness-gym.git`.

Release tags (Step 1 recap): one codebase builds 8 images; `APP_VERSION` picks the feature set.

| Docker tag(s) | Adds (cumulative) | Tests |
|---|---|---|
| `1.0` | health, programs | 31 |
| `1.1` | clients | 44 |
| `1.1.2` | reports | 48 |
| `2.0.1`, `2.1.2` | progress | 60 |
| `2.2.1` | bmi | 71 |
| `2.2.4`, `3.0.1` | metrics, workouts, dashboard | 94 |
| `3.1.2` | auth, membership, program_generator | 117 |
| `3.2.4`, `latest` | analytics | 120 |

Order of work: **Step 2** (PR 1 and PR 2 only) > **3** > **4** > **5** (merge PR 3, run pipeline) > **6** > **7** > **8** > **9**.

---

## Step 2. Clone, apply the files, pull requests, merge [LAPTOP]

### 2.1 Prerequisites
- Git installed (`git --version`), logged in to GitHub (Git Credential Manager, a personal access token, or `gh auth login`).
- Optional but recommended: Python 3.9+ to run the tests locally.
- On Windows use **Git Bash** for every command below.

### 2.2 Clone and unpack
```bash
mkdir -p ~/work && cd ~/work
git clone https://github.com/2025tm93234/aceest-fitness-gym.git
cd aceest-fitness-gym
git config core.autocrlf input          # keeps Linux line endings (scripts must run in the lab)
git status                              # expect: On branch main, nothing to commit
```
Extract `aceest-fitness-gym-assignment2.zip` into a folder named `a2pkg` **next to** the repo
(right-click > Extract All, or `unzip -q aceest-fitness-gym-assignment2.zip -d ../a2pkg`). Then:
```bash
PKG=../a2pkg/aceest-fitness-gym
ls "$PKG"                               # expect: Dockerfile Jenkinsfile aceest k8s scripts tests ...
cp_files() { for f in "$@"; do mkdir -p "$(dirname "$f")"; cp "$PKG/$f" "$f"; done; }
```
Optional baseline: `python -m venv .venv && source .venv/bin/activate` (Windows Git Bash: `source .venv/Scripts/activate`),
`pip install -r requirements.txt`, `python -m pytest -q` (expect 103 passed).

### 2.3 PR 1: release catalogue (`feature/release-catalogue`)
```bash
git checkout -b feature/release-catalogue
cp_files aceest/versions.py aceest/meta.py aceest/__init__.py tests/conftest.py tests/test_versions.py
git status --short                      # 3 new files, 2 modified
python -m flake8 aceest app.py tests/ && python -m pytest -q      # expect: 119 passed
git add -A
git commit -m "feat: add release catalogue and /version endpoint"
git push -u origin feature/release-catalogue
```
On GitHub: **Compare & pull request** > base `main` < compare `feature/release-catalogue` > **Create pull request**.
Wait for the checks (Build & Lint, Docker Image Assembly, Automated Testing) to turn green, then
**Merge pull request > Confirm merge**. Back on the laptop:
```bash
git checkout main && git pull
```

### 2.4 PR 2: Kubernetes, scripts and docs (`infra/kubernetes`)
```bash
git checkout -b infra/kubernetes
cp_files .gitattributes README.md lab-setup.sh docs/ASSIGNMENT2.md \
  k8s/00-namespace.yaml k8s/10-rolling.yaml k8s/20-bluegreen.yaml k8s/30-canary.yaml \
  k8s/40-shadow.yaml k8s/50-abtest.yaml \
  scripts/lib.sh scripts/k8s.sh scripts/probe.sh scripts/expose.sh scripts/tunnel.sh scripts/deploy_rolling.sh
git add -A
git update-index --chmod=+x scripts/*.sh lab-setup.sh     # needed on Windows; harmless elsewhere
git ls-files -s scripts lab-setup.sh | head -3            # expect mode 100755
git commit -m "infra: add Kubernetes manifests, strategy scripts and runbook"
git push -u origin infra/kubernetes
```
Create the PR, wait for green checks, **Merge pull request**, then `git checkout main && git pull`.

### 2.5 PR 3: SonarQube, Docker Hub and the new pipeline (`ci/sonarqube-dockerhub`)
```bash
git checkout -b ci/sonarqube-dockerhub
cp_files Dockerfile .dockerignore .gitignore .coveragerc sonar-project.properties Jenkinsfile \
  .github/workflows/main.yml tests/test_release_script.py \
  scripts/build_push_all.sh scripts/smoke_test.sh scripts/sonar_quality_gate.sh
git add -A
git update-index --chmod=+x scripts/*.sh
python -m flake8 aceest app.py tests/ && python -m pytest -q      # expect: 120 passed
git commit -m "ci: SonarQube, Docker Hub publishing and per-release pipeline"
git push -u origin ci/sonarqube-dockerhub
```
Open the PR and wait for green checks. This one also runs **"Every release (inside container)"**, 8 parallel
jobs (about 5 to 8 minutes); all must be green.

> **Do not merge PR 3 yet.** Once it is merged, Jenkins picks up the new Jenkinsfile, which needs the
> credentials from Step 4. Do Steps 3 and 4 first.

### 2.6 Confirm the files match the package
```bash
git checkout main && git pull
diff -rq --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache --exclude=.coverage . "$PKG"
```
After PR 3 is merged this prints nothing. Before that it lists only the PR 3 files. Do not merge PR 3 until Step 5.

---

## Step 3. Lab: pull the code and check the platform [LAB]

Open a terminal on Prayogshala as your normal user.
```bash
cd ~/workspace/aceest-fitness-gym
git checkout main && git pull           # brings PR 1 + PR 2 (lab-setup.sh, k8s/, scripts/)
sudo bash lab-setup.sh                  # idempotent: only does what is missing
```
Expected end of output: `docker ps` lists `sonarqube`, the ingress controller shows `1/1 Running`, `free -h` is printed.

| Check | Command | Expected |
|---|---|---|
| Jenkins has Docker | `sudo -u jenkins -H docker ps` | table including `sonarqube` |
| Cluster | `sudo -u jenkins -H kubectl get nodes` | `minikube   Ready` |
| Ingress | `sudo -u jenkins -H kubectl -n ingress-nginx get pods` | controller `1/1 Running` |
| SonarQube | `curl -s localhost:9000/api/system/status` | `"status":"UP"` (allow about 2 minutes) |
| Memory | `free -h` | about 2.5 GiB or more `available` |

After any lab reset, run `sudo bash lab-setup.sh` again.

---

## Step 4. SonarQube, Docker Hub and Jenkins credentials [BROWSER in the lab]

Never paste tokens into chats, documents or screenshots.

### 4.1 SonarQube login and token
1. Open `http://localhost:9000`, log in with `admin` / `admin`, set a new password when asked.
2. Click the avatar > **My Account** > **Security** > **Generate Tokens**: Name `jenkins`, Type **User Token**,
   Expires `30 days`, **Generate**, then copy the token (shown once).

### 4.2 Docker Hub token and repository
1. `https://hub.docker.com` > **Account settings** > **Personal access tokens** > **Generate new token**
   (name `jenkins`, permissions **Read & Write**). Copy it.
2. **Repositories** > **Create repository**: name `aceest-fitness`, visibility **Public**.

### 4.3 Jenkins credentials
`http://localhost:8080` > **Manage Jenkins** > **Credentials** > **System** > **Global credentials (unrestricted)** > **Add Credentials**:

| Kind | Fields | ID (exact) |
|---|---|---|
| Secret text | Secret = the SonarQube token | `sonar-token` |
| Username with password | Username = `<user>`, Password = the Docker Hub token | `dockerhub-creds` |

### 4.4 Plugins and job
- **Manage Jenkins > Plugins > Installed plugins**: confirm **JUnit** (and Pipeline) are present; install JUnit if missing.
- Open job `aceest-fitness-build` > **Configure**: Pipeline = **Pipeline script from SCM**, SCM **Git**,
  repository `https://github.com/2025tm93234/aceest-fitness-gym.git` (your repository), branch `*/main`, Script Path `Jenkinsfile`;
  Triggers: **Poll SCM** `H/5 * * * *`. **Save**. (Screenshots: Fig 3.)

---

## Step 5. Run the pipeline [LAPTOP then BROWSER]

### 5.1 Merge PR 3
On GitHub merge PR 3 (`ci/sonarqube-dockerhub`). Jenkins starts a build within 5 minutes, or click **Build Now**.
The first run takes 5 to 8 minutes (it downloads the SonarQube scanner image).

Stages you should see go green in **Stage View**: Checkout, Setup Environment, Lint, Unit Tests,
SonarQube Analysis, Quality Gate, Docker Build, Container Smoke Test, Push to Docker Hub, Deploy to Minikube.

Console lines to look for (Fig 5):
```
SonarQube quality gate: OK   (http://localhost:9000/dashboard?id=aceest-fitness-gym)
smoke test OK: 3.2.4
deployed <user>/aceest-fitness:3.2.4
```

### 5.2 SonarQube result
Open `http://localhost:9000/dashboard?id=aceest-fitness-gym`: expect **Passed** and coverage near 99% (Fig 6, 7).
If the gate fails on **Security Hotspots**: project > **Security Hotspots** > open each > **Review** > **Safe**
with a short comment, then run **Build Now** again.

### 5.3 Publish every release to Docker Hub
Job > **Build with Parameters**: `APP_VERSION` `3.2.4`, `PUSH_IMAGE` on, `DEPLOY` on, **`BUILD_ALL_VERSIONS` on** > **Build**.
About 8 to 10 minutes. Then open `https://hub.docker.com/r/<user>/aceest-fitness/tags`: expect
`1.0 1.1 1.1.2 2.0.1 2.1.2 2.2.1 2.2.4 3.0.1 3.1.2 3.2.4 latest` (plus `build-N` tags) (Fig 8).
Verify in the lab:
```bash
docker images <user>/aceest-fitness                                   # Fig 9
for v in 1.0 2.2.1 3.2.4; do docker run --rm <user>/aceest-fitness:$v printenv APP_VERSION; done
```
Expected output: `1.0`, `2.2.1`, `3.2.4`.

### 5.4 Several green builds on recent commits
The assignment wants successful runs on recent commits. Make 2 or 3 small pull requests, merging each:
```bash
git checkout main && git pull
git checkout -b docs/pipeline-notes-1
echo "" >> README.md && echo "Pipeline: lint, test, SonarQube, Docker Hub, Kubernetes." >> README.md
git commit -am "docs: describe pipeline stages" && git push -u origin docs/pipeline-notes-1
```
Merge the PR; Jenkins builds within 5 minutes. Repeat with a different small edit twice more.
Capture **Stage View** with at least 3 green builds (Fig 4).

---

## Step 6. Deployment strategies [LAB]

### 6.1 Variables
```bash
sudo ls /var/lib/jenkins/workspace/                     # note the job folder name
export WS=/var/lib/jenkins/workspace/aceest-fitness-build   # adjust if the name differs (may end in @2)
export IMAGE_REPO=<user>/aceest-fitness
J="sudo -u jenkins -H env IMAGE_REPO=$IMAGE_REPO"
BASE=http://localhost:8088
cd /tmp
P=~/workspace/aceest-fitness-gym/scripts                 # your clone (git pull first): probe.sh needs no cluster access
```
Everything that talks to Kubernetes runs through `$J` (the `jenkins` user owns the cluster).

### 6.2 Create everything
```bash
$J bash $WS/scripts/k8s.sh apply all                    # stable=3.1.2, new=3.2.4
$J kubectl -n aceest get pods -w                        # Ctrl+C when all are Running (1 to 3 minutes)
$J bash $WS/scripts/expose.sh start                     # ingress on port 8088
free -h | head -2                                       # keep 'available' above about 1 GiB
```
If memory runs short: `$J bash $WS/scripts/k8s.sh delete <strategy>` for the ones already captured.
If pods show `ImagePullBackOff`, Step 5.3 was not completed.

### 6.3 Demos (take a screenshot of each)

| Strategy | Commands | Expected |
|---|---|---|
| **Rolling update** (Fig 11) | Terminal A: `while true; do curl -s -o /dev/null -w "%{http_code} " $BASE/rolling/health; sleep 0.3; done` <br> Terminal B: `curl -s $BASE/rolling/version` then `$J bash $WS/scripts/k8s.sh rolling-update 3.2.4` then `curl -s $BASE/rolling/version` | Terminal A prints only `200`s during the update; version changes `3.1.2` to `3.2.4`; rollout history lists revisions |
| **Rollback** (Fig 12) | `$J bash $WS/scripts/k8s.sh rollback` then `curl -s $BASE/rolling/version` | Image back to `<user>/aceest-fitness:3.1.2` |
| **Blue-green** (Fig 13) | `bash $P/probe.sh $BASE/bluegreen/version 5`; `$J bash $WS/scripts/k8s.sh bluegreen-switch green`; probe again; switch back with `blue` | `release 3.1.2 answered 5`, then `release 3.2.4 answered 5` |
| **Canary** (Fig 14) | `bash $P/probe.sh $BASE/canary/version 20`; `$J bash $WS/scripts/k8s.sh canary-weight 50`; probe again | About 16 vs 4 at weight 20, about 10 vs 10 at 50 (random, so approximate) |
| **Shadow** (Fig 15) | `curl -s -D - $BASE/shadow/version`; `$J kubectl -n aceest logs deploy/aceest-shadow --tail=5` | Response shows `X-App-Version: 3.1.2`; the shadow (3.2.4) log shows `GET /version` copies |
| **A/B** (Fig 16) | `bash $P/probe.sh $BASE/ab/version 5`; `bash $P/probe.sh $BASE/ab/version 5 "X-Experiment: B"` | `3.1.2` x5 without the header, `3.2.4` x5 with it |
| **Pipeline auto-rollback** (Fig 12b) | `$J bash $WS/scripts/deploy_rolling.sh 9.9.9` | After about 3 minutes: `!! deployment of 9.9.9 failed - rolling back ...`; `curl -s $BASE/rolling/version` still answers throughout |

Status screenshot for Fig 10: `$J kubectl get nodes` and `$J kubectl -n aceest get pods`.

---

## Step 7. Endpoint URL

1. In the lab: `curl -s ifconfig.me` gives the public IP.
2. On your phone **using mobile data**, open `http://<public-ip>:8088/rolling/version`.
   JSON means inbound access works: submit `http://<public-ip>:8088` with the paths
   `/rolling`, `/bluegreen`, `/canary`, `/shadow`, `/ab` (each plus `/version`).
3. If it does not load, use the outbound tunnel (works without any inbound port):
   ```bash
   bash ~/workspace/aceest-fitness-gym/scripts/tunnel.sh       # prints https://<random>.trycloudflare.com
   curl -s https://<random>.trycloudflare.com/rolling/version
   ```
   Keep that terminal open; the URL changes on every run. Capture Fig 17 (browser address bar and JSON).
4. The URL works only while the lab session is alive; ask your instructor whether screenshots are accepted.
5. When finished: `$J bash $WS/scripts/expose.sh stop`.

---

## Step 8. Evidence checklist (figure order)

Hide the lab dock, use a large terminal font, and include the command with its output in each shot.

| Fig | Capture |
|---|---|
| 1 | GitHub repository main page (public, tags, recent commits) |
| 2 | `git log --oneline --graph --all` and `git tag` |
| 3 | Jenkins job configuration: Poll SCM and Pipeline source |
| 4 | Jenkins Stage View: at least 3 green builds |
| 5 | Jenkins console: quality gate `OK`, smoke test, deployed |
| 6 | SonarQube project dashboard (Passed, coverage, issues) |
| 7 | SonarQube measures or report |
| 8 | Docker Hub Tags page (all versions) |
| 9 | `docker images <user>/aceest-fitness` |
| 10 | `kubectl get nodes` and `kubectl -n aceest get pods` |
| 11 to 16 | Strategy demos from Step 6.3 (rolling, rollback, blue-green, canary, shadow, A/B) |
| 17 | Endpoint URL working from outside the lab |

---

## Step 9. Report and submission package

Report, 2 to 3 pages (PDF): (1) architecture diagram: GitHub, Jenkins, Pytest, SonarQube, Docker Hub, Minikube;
(2) tools and the release table; (3) strategies and why (zero downtime, rollback); (4) challenges and fixes
(Jenkins needs the docker group, Minikube runs as `jenkins`, 2-CPU memory budget, SonarQube heap limit,
`/usr/local/bin` not on the sudo path); (5) outcomes: test counts, coverage, quality gate, image tags, endpoint URL.

Submit: project folder ZIP, GitHub link, endpoint URL, report. Create the ZIP on your laptop:
```bash
cd ~/work/aceest-fitness-gym && git checkout main && git pull
git archive --format=zip -o ../aceest-fitness-gym-submission.zip HEAD
```
Send me your screenshots and I will validate them and build the final document.

---

## Step 10. Troubleshooting

| Symptom | Fix |
|---|---|
| Jenkins `permission denied` on Docker | `sudo usermod -aG docker jenkins && sudo systemctl restart jenkins` |
| Build fails at start: credentials not found | Step 4.3 IDs must be exactly `sonar-token` and `dockerhub-creds` |
| Quality Gate stage fails | Review hotspots (Step 5.2), or open the SonarQube dashboard to see which condition failed |
| `SonarQube analysis task FAILED` | `docker logs sonarqube --tail 30`; low memory: `free -h`, stop unused strategies |
| Pods `ImagePullBackOff` | Publish the tags first (Step 5.3) and check `IMAGE_REPO` |
| `kubectl: command not found` under sudo | `sudo ls -l /usr/bin/kubectl`; reinstall via `sudo bash lab-setup.sh` |
| Scripts fail with `bad interpreter` | Windows line endings: `git config core.autocrlf input`, recommit, or `sed -i 's/\r$//' scripts/*.sh` |
| Canary split uneven | Send 50 or more requests; the split is probabilistic |
| Endpoint unreachable from phone | Use the tunnel (Step 7.3) |
| Everything gone after a lab reset | `sudo bash lab-setup.sh`, then Step 6.2 again (the Docker Hub images stay) |
