# KubeVirt Diagram Redesign Spec

## Problem

The KubeVirt section currently contains a large set of architecture-oriented diagrams created with mixed visual approaches and varying levels of consistency. The site now has a repo-local `diagram-design` skill that defines a stricter editorial diagram system with fixed grammars for architecture, flowchart, sequence, and state diagrams.

This work should redraw the KubeVirt diagrams that communicate architecture, process flow, message flow, or state transitions so they read as one coherent visual system while preserving the repo's delivery model: static images referenced from markdown pages.

## Goals

1. Redraw KubeVirt's architecture-oriented diagrams using the `diagram-design` visual grammar.
2. Keep the docs reading experience unchanged: markdown pages continue to embed static diagram assets.
3. Make the redraw maintainable by generating the assets from scripts under `scripts/diagram-generators/`.
4. Deliver a local VitePress preview so the user can review the updated pages in context.

## Non-goals

1. Redesign every diagram in the repository outside `docs-site/kubevirt/`.
2. Replace documentation images with raw HTML diagram files as the final published asset format.
3. Redraw diagram families outside the agreed scope, such as charts or illustrations that are not architecture, flow, sequence, or state oriented.
4. Rework unrelated prose unless a diagram split or rename requires a small local markdown update.

## Scope

The agreed scope is:

- Under `docs-site/kubevirt/`, include diagrams that are architecture, flowchart, sequence, or state-machine oriented.
- Replace the current image assets and markdown references in place when possible.
- Open a local VitePress server after the redraw is complete so the user can inspect the rendered docs.

Current inventory indicates this is a large, cross-section effort, with 83 candidate diagram references across 30 markdown pages:

- `architecture/*`
- `deep-dive/*`
- `components/*`
- `advanced/*`
- `networking/*`
- `storage/*`
- `guides/*`
- `virtctl/*`
- selected `api-resources/*`

Because this is too large for a single undifferentiated pass, execution should be phased while still converging toward a full-site redraw.

Explicit exclusions for this effort:

- `docs-site/kubevirt/dev-guide/*`
- `docs-site/kubevirt/learning-path/*`

These sections are intentionally excluded because they are narrative or code-structure oriented and are not part of the agreed architecture/flow/sequence/state redraw scope.

## Deliverables

1. Updated static diagram assets in `docs-site/public/diagrams/kubevirt/`.
2. Generator scripts in `scripts/diagram-generators/` for the new or replaced diagram sets.
3. Markdown updates only where a renamed or split diagram requires a reference change.
4. A local VitePress preview run for final review.

## Design Principles

### 1. Follow diagram-design as a visual system

The redraw should inherit the `diagram-design` rules already reviewed:

- Use one of four explicit grammars per diagram: architecture, flowchart, sequence, or state.
- Keep information density restrained; split diagrams that exceed the skill's complexity budget.
- Use accent sparingly for 1-2 focal elements, not as a generic importance marker.
- Keep typography, arrows, legends, labels, and boundary treatments consistent across all KubeVirt pages.

For this effort, the style-guide decision is already resolved:

- Phase 1 should use the default `diagram-design` editorial style-guide tokens rather than blocking on a custom onboarding pass.
- A custom site-specific style-guide may be considered later, but it is out of scope for this planning cycle.

### 2. Preserve repo conventions

- Final published assets remain static SVG/PNG under `docs-site/public/diagrams/kubevirt/`.
- Generator code lives under `scripts/diagram-generators/`.
- No Mermaid is introduced.
- Documentation pages should continue to read naturally without forcing readers into a different navigation pattern.

### 3. Prefer reusable canonical diagrams

When the same conceptual diagram appears on multiple pages, prefer a single canonical asset instead of diverging variants. For example, a shared VMI state diagram should remain one maintained source unless two pages truly need different detail levels.

## Phased Execution Model

### Phase 1 - Core architecture language

Prioritize the pages that define the mental model of the project and establish the reusable visual language:

- `docs-site/kubevirt/architecture/overview.md`
- `docs-site/kubevirt/architecture/deep-dive.md`
- `docs-site/kubevirt/architecture/lifecycle.md`
- `docs-site/kubevirt/deep-dive/migration-internals.md`
- `docs-site/kubevirt/deep-dive/upgrade-strategy.md`
- `docs-site/kubevirt/api-resources/migration.md`
- `docs-site/kubevirt/api-resources/vm-vmi.md`

Expected outputs in this phase:

- KubeVirt high-level architecture overview
- VM creation / lifecycle flow
- controller and informer flow
- webhook and migration call flows
- upgrade flow and related state/sequence diagrams

This phase should produce the base language that later sections reuse.

### Phase 2 - Component and subsystem pages

Apply the same grammar to component-level and subsystem-level pages, including:

- `docs-site/kubevirt/components/*`
- `docs-site/kubevirt/deep-dive/vm-initialization.md`
- `docs-site/kubevirt/deep-dive/security.md`
- `docs-site/kubevirt/deep-dive/gpu-passthrough.md`
- `docs-site/kubevirt/deep-dive/qemu-kvm.md`
- `docs-site/kubevirt/deep-dive/performance-tuning.md`
- `docs-site/kubevirt/deep-dive/vm-optimization.md`
- `docs-site/kubevirt/deep-dive/windows-optimization.md`

This phase focuses on consistent component boundaries, call paths, and subsystem overviews.

### Phase 3 - Topic, operations, and guide pages

Finish the broader redraw across:

- `docs-site/kubevirt/advanced/*`
- `docs-site/kubevirt/networking/*`
- `docs-site/kubevirt/storage/*`
- `docs-site/kubevirt/guides/*`
- `docs-site/kubevirt/virtctl/*`
- `docs-site/kubevirt/api-resources/replica-pool.md`
- `docs-site/kubevirt/api-resources/snapshot-clone.md`

This phase includes operational flows, migration policies, storage flows, networking architecture, HA/DR flows, and user-facing workflow diagrams.

## Diagram Type Mapping Rules

Use the following mapping so diagrams are classified consistently:

| Content shape | Diagram grammar |
|---|---|
| System overview, trust boundary, topology, component relation | Architecture |
| Step-by-step operational process, decision path, troubleshooting path | Flowchart |
| Cross-component calls over time, API/webhook/migration exchanges | Sequence |
| Phase and lifecycle transitions | State |

If a diagram mixes two grammars, pick the dominant axis instead of hybridizing. If that still feels overloaded, split it into two assets.

## Asset and Script Structure

### Asset placement

- Output assets go to `docs-site/public/diagrams/kubevirt/`.
- Reuse current filenames when replacement is truly in-place and semantics stay aligned.
- Introduce new filenames only when a diagram is split, renamed for clarity, or normalized across multiple pages.

### Script placement

New scripts must live under `scripts/diagram-generators/` and follow existing naming conventions, for example:

- `gen_kubevirt_architecture_redraw.py`
- `gen_kubevirt_migration_redraw.py`
- `gen_kubevirt_upgrade_redraw.py`

Scripts should be grouped by coherent subject area rather than one script per individual image if batching improves maintainability.

## Rendering Strategy

The final site should still consume static images, but the redraw process may use `diagram-design`-style source composition as an intermediate step. The implementation may choose the most maintainable path that preserves the visual grammar, for example:

- generate SVG directly with code while following the `diagram-design` grammar, or
- generate intermediate HTML/SVG artifacts during authoring and export the final static assets into the repo.

The key requirement is that published docs keep using committed static assets, not runtime-generated diagrams.

## Markdown Update Rules

1. Do not rewrite markdown references unless necessary.
2. If an existing filename can be safely preserved, preserve it.
3. If a diagram must split into overview + detail, update the surrounding markdown so the diagram placement and explanatory prose still make sense.
4. Keep documentation edits tightly local to the affected pages.

## Validation and Review

Each phase should be validated with:

1. Asset existence checks for every referenced file.
2. A full `npm run build` to ensure the site still builds.
3. Spot review of the affected rendered pages, not just the image files in isolation.

At the end of the full redraw:

1. Start a local VitePress server.
2. Confirm the updated KubeVirt pages render correctly in context.
3. Provide the user with the local server entry point for review.

## Error Handling and Edge Cases

### Over-complex legacy diagrams

If a legacy diagram exceeds the `diagram-design` complexity budget, do not force it into one crowded replacement. Split it into:

- an overview diagram for the main mental model, and
- one detail diagram for the busy sub-flow.

Any split must be reflected in nearby markdown.

### Shared diagrams across pages

If multiple pages reference the same image, treat it as a shared contract. Changes to that asset must be checked against all consuming pages before finalizing.

### Filename compatibility

If a current filename is misleading but already referenced in several places, prefer a small compatibility-minded migration:

- update the image asset,
- update the necessary markdown references together,
- avoid leaving duplicate old/new assets without purpose.

### Scope control

Because the full inventory is large, implementation planning should explicitly track which pages and diagrams belong to each phase. This avoids a half-updated state where visual language diverges between adjacent sections.

## Recommended Implementation Order

1. Build the shared KubeVirt visual language and redraw Phase 1.
2. Validate Phase 1 in rendered docs.
3. Extend the same primitives and script patterns to Phase 2.
4. Finish the broader operational pages in Phase 3.
5. Run the full build and open the local preview server.

## Success Criteria

This spec is satisfied when:

1. The agreed KubeVirt diagram families have been redrawn into a consistent `diagram-design`-style visual system.
2. The site still uses static SVG/PNG assets under `docs-site/public/diagrams/kubevirt/`.
3. The redraw process is maintainable through scripts in `scripts/diagram-generators/`.
4. The KubeVirt docs build successfully.
5. The user can inspect the results through a local VitePress server.
