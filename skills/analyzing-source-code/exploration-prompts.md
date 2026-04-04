# Exploration Prompt Templates

These are the 5 parallel exploration prompts used to analyze a source code repository. Adapt based on project type.

## Agent 1: Project Structure

```
Explore the {project-name} repository at {repo-path} and provide a comprehensive analysis:

1. **Project Overview**: Read README.md, go.mod (or equivalent), Makefile, build files.
   Document: purpose, language, version, license, key dependencies.

2. **Directory Structure**: List ALL top-level directories and purposes.
   Go 2 levels deep for important directories (cmd/, pkg/, api/, controllers/).

3. **Core Components**: What are the main binaries/packages?
   Read cmd/ directory entries. What does each binary do?

4. **Build System**: How is the project built?
   Read Makefile targets, CI/CD files (.github/workflows/), Dockerfile.

5. **CRD Registration**: Where are CRDs registered?
   Look for register.go, types.go, scheme registration.

Be thorough — read actual source files, show file paths for everything.
```

## Agent 2: Controllers & Reconciliation

```
Explore the controllers in {repo-path}:

1. **Controller Registration**: Where/how are controllers registered?
   Read main.go or cmd/*/main.go for SetupWithManager calls.

2. **Reconciliation Logic**: For each controller, read the Reconcile() function.
   Document: what resource it watches, reconcile flow, requeue logic.

3. **State Machine**: What states/phases does the resource go through?
   Look for Phase/Status enums and transitions.

4. **Error Handling**: How are errors reported?
   Look for event recording, status condition updates.

5. **Worker Configuration**: Any concurrency settings, rate limiting, or predicates?

Show file paths and code snippets for key logic.
```

## Agent 3: API Types & CRD Definitions

```
Explore the API types in {repo-path}:

1. **CRD Types**: Read ALL type definition files.
   Look in api/*, pkg/apis/*, staging/*/types.go.
   Document every Spec and Status field.

2. **Enums & Constants**: Document all phase enums, condition types, annotation keys.

3. **Webhook Definitions**: Read *_webhook.go files.
   Document validation rules (create/update/delete).

4. **DeepCopy & Defaults**: Any defaulting webhooks or custom defaults?

5. **API Versioning**: What API groups/versions are used?
   Document conversion between versions if applicable.

Show the actual Go struct definitions with all fields.
```

## Agent 4: Core Features & Key Functionality

```
Explore the core functionality in {repo-path}:

1. **Primary Feature**: What is the main thing this project does?
   Read the core business logic packages.

2. **Data Processing**: Any data pipelines, format conversions, transformations?
   Read processing logic with actual code.

3. **Configuration**: How is the project configured?
   Look for ConfigMap, CR spec fields, environment variables, flags.

4. **Key Algorithms**: Any interesting algorithms or decision logic?
   Read strategy selection, priority logic, fallback mechanisms.

5. **Metrics & Monitoring**: What Prometheus metrics are exposed?
   Look for metric registration and recording.

Show file paths and code snippets for all key logic.
```

## Agent 5: External Integrations

```
Explore external integrations in {repo-path}:

1. **Kubernetes Integration**: What K8s resources does it interact with?
   Read RBAC rules (config/rbac/role.yaml) for the full permission list.

2. **Ecosystem Integration**: References to other projects?
   Search go.mod for kubevirt, medik8s, prometheus, etc.

3. **Authentication & Authorization**: JWT, RBAC, ServiceAccount usage?
   Read auth-related packages and webhook configurations.

4. **Storage/Network Integration**: CSI, CNI, volume plugins?
   Look for storage class, provisioner, network references.

5. **CI/CD & Deployment**: Read .github/workflows/, bundle/, config/.
   Document deployment methods (OLM, Kustomize, Helm).

Show file paths and dependency references.
```

## Adapting for Non-Operator Projects

### Project Type Classification (Phase 2.5)

After all 5 agents complete, classify the project before writing:

| Check | If True → Type |
|-------|----------------|
| Has `Reconcile()` + ≥5 components or ≥10 CRDs | **大型平台** → `controllers-api.md` + optional extras |
| Has `Reconcile()` + <5 components | **Controller Operator** → `controllers-api.md` |
| No controller, core output is PrometheusRule/Alerts/Dashboards | **監控型** → `metrics-alerts.md` |
| No controller, core output is YAML resource definitions | **資源定義型** → `resource-catalog.md` |
| No controller, provides CLI/SDK/library | **工具/函式庫** → `cli-reference.md` |

### YAML/Kustomize Projects (e.g., common-instancetypes)
- Replace "Controllers" agent with "YAML Definitions" agent
- Focus on: Kustomize structure, YAML schema, validation scripts
- Replace "API Types" with "Resource Specifications"
- **Output page**: `resource-catalog.md` (not controllers-api.md)

### Monitoring/Tools Projects (e.g., monitoring)
- Replace "Controllers" agent with "Tool Implementations" agent
- Focus on: CLI tools, linters, generators, dashboards
- Replace "Core Features" with "Metrics & Alerts & Runbooks"
- **Output page**: `metrics-alerts.md` (not controllers-api.md)

### Library Projects
- Replace "Controllers" agent with "Public API" agent
- Focus on: exported functions, interfaces, usage patterns
- Replace "Core Features" with "Library Capabilities"
- **Output page**: `cli-reference.md` (not controllers-api.md)
