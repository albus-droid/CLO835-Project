Project Plan 

---

## ✅ Phase 1: Enhance the Flask Application (Day 1–2)

* [x] Fork/clone the [starter repo](https://github.com/ladunuthala/clo835_summer2023_assignment1)
* [x] Modify HTML to:

  * Use background image (remove background color)
  * Display your name via env var from ConfigMap
* [x] Use Python + `boto3` to:

  * Fetch image from private S3 using boto3
  * Store it locally and serve from there
* [x] Log image URL to stdout
* [x] Flask app should:

  * Use port `81`
  * Get MySQL credentials from environment variables (`K8s Secrets`)
  * Load image location from a ConfigMap

---

## ✅ Phase 2: Dockerize and Test Locally (Day 2–3)

* [x] Create a `Dockerfile`
* [x] Add port 81 exposure
* [x] Copy app + requirements
* [x] Use `CMD` or `ENTRYPOINT` to run the app
* [x] Test it locally using:

  ```bash
  docker build -t clo835-final .
  docker run -p 81:81 --env ... clo835-final
  ```

---

## ✅ Phase 3: GitHub + ECR Integration (Day 3–4)

* [x] Push code to a GitHub repo
* [x] Set up GitHub Actions (`.github/workflows/main.yml`)

  * Build + test app
  * Push image to Amazon ECR
* [x] Store ECR credentials as GitHub Secrets

---

## ✅ Phase 4: EKS Cluster Setup (Day 4)

* [x] Use `eksctl`:

  ```bash
  eksctl create cluster --name clo835-final --nodes=2
  ```
* [x] Create namespace:

  ```bash
  kubectl create namespace final
  ```

---

## ✅ Phase 5: K8s Manifests + S3 Access (Day 5–6)

* [x] Create:

  * `configmap.yaml` – with S3 image URL + your name
  * `secret.yaml` – with DB credentials
  * `pvc.yaml` – 2Gi, ReadWriteOnce
  * `serviceaccount.yaml` – named `clo835` with IRSA access to S3
  * `role.yaml` + `rolebinding.yaml` – allow namespace read/create
* [x] Use `aws iam create-role` and `eksctl create iamserviceaccount` for IRSA

---

## ✅ Phase 6: App & DB Deployment (Day 6–7)

* [ ] MySQL:

  * Deployment with PVC
  * Service (ClusterIP)
* [ ] Flask App:

  * Deployment from ECR image
  * Service (LoadBalancer for public access)
  * Use envs from `ConfigMap` and `Secret`

---

## ✅ Bonus (optional but high impact)

* [ ] HPA + metrics-server

  * Deploy `metrics-server`
  * Add `resources` to app
  * Add `HorizontalPodAutoscaler` manifest
* [ ] Flux CD + Helm for deployment automation

---

## ✅ Final Checks & Submission (Day 8–9)

* [ ] Record:

  * Local Docker test
  * EKS deployment
  * LoadBalancer URL in browser
  * Replace background image + update configmap → see new image
  * (Bonus) HPA in action
* [ ] Push all code and manifests to GitHub
* [ ] Add README and meaningful commit messages
* [ ] Write a short report (issues faced, fixes, and reflections)
* [ ] Submit GitHub + video links on Blackboard

---

Let me know your current progress (e.g. app modified? Dockerfile ready? GitHub set up?) and I’ll help you next with whatever step you’re on.
