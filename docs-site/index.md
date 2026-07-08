---
layout: home

hero:
  name: "KubeVirt Ecosystem"
  text: "Source Code Deep Dives"
  tagline: In-depth analysis of architecture, core components, and implementation details across major KubeVirt ecosystem projects
  image:
    src: https://raw.githubusercontent.com/kubevirt/community/main/logo/KubeVirt_icon.png
    alt: KubeVirt
  actions:
    - theme: brand
      text: 🖥️ KubeVirt
      link: /kubevirt/architecture/overview
    - theme: alt
      text: 💾 CDI
      link: /containerized-data-importer/
    - theme: alt
      text: 📊 Monitoring
      link: /monitoring/
    - theme: alt
      text: 📋 Instancetypes
      link: /common-instancetypes/
    - theme: alt
      text: 🔧 NMO
      link: /node-maintenance-operator/
    - theme: alt
      text: 🚚 Forklift
      link: /forklift/
    - theme: alt
      text: 🌐 NetBox
      link: /netbox/
    - theme: alt
      text: 📨 Kafka
      link: /kafka/
    - theme: alt
      text: 🗄️ TiDB
      link: /tidb/
    - theme: alt
      text: 🔩 Cluster API
      link: /cluster-api/
    - theme: alt
      text: 🏗️ CAPM3
      link: /cluster-api-provider-metal3/
    - theme: alt
      text: ☁️ CAPMAAS
      link: /cluster-api-provider-maas/
    - theme: alt
      text: 🔑 etcd
      link: /etcd/
    - theme: alt
      text: 🔒 OpenShell
      link: /openshell/
    - theme: alt
      text: 🤖 NemoClaw
      link: /nemoclaw/


features:
  - icon: 🖥️
    title: KubeVirt
    details: Virtual machine management on Kubernetes, with source-level coverage of architecture, the five core components, CRDs, networking, storage, and migration.
    link: /kubevirt/architecture/overview
    linkText: Start Reading

  - icon: 💾
    title: Containerized Data Importer (CDI)
    details: Data import framework for Kubernetes persistent volumes, focused on moving VM images into PVCs from multiple source types and transfer paths.
    link: /containerized-data-importer/
    linkText: Start Reading

  - icon: 📊
    title: Monitoring
    details: Centralized monitoring for the KubeVirt ecosystem, including 75 alert runbooks, 100+ Prometheus metrics, Grafana dashboards, and linter tooling.
    link: /monitoring/
    linkText: Start Reading

  - icon: 📋
    title: Common Instancetypes
    details: Standardized VM instance types and preferences, covering 7 major series, 43 instancetypes, and 18+ OS preferences in an EC2-like model.
    link: /common-instancetypes/
    linkText: Start Reading

  - icon: 🔧
    title: Node Maintenance Operator
    details: Kubernetes node maintenance automation for cordon, drain, and uncordon workflows, optimized for KubeVirt VM workloads.
    link: /node-maintenance-operator/
    linkText: Start Reading

  - icon: 🚚
    title: Forklift
    details: VM migration platform supporting automated migrations from vSphere, oVirt, OpenStack, Hyper-V, OVA, and more into KubeVirt, including incremental sync and XCOPY acceleration.
    link: /forklift/
    linkText: Start Reading

  - icon: 🌐
    title: NetBox
    details: Network infrastructure management platform built with Python and Django, covering 115 data models, 131 REST APIs, GraphQL, plugins, and object-level RBAC.
    link: /netbox/
    linkText: Start Reading

  - icon: 📨
    title: Apache Kafka
    details: Distributed event-streaming platform implemented in Java and Scala, with KRaft consensus, Producer and Consumer APIs, Kafka Streams, and Kafka Connect.
    link: /kafka/
    linkText: Start Reading

  - icon: 🗄️
    title: TiDB
    details: Distributed HTAP SQL database in Go, with MySQL compatibility, TiKV row storage, TiFlash columnar storage, Raft replication, and horizontal scaling.
    link: /tidb/
    linkText: Start Reading

  - icon: 🔩
    title: Cluster API
    details: Kubernetes cluster lifecycle management framework with declarative APIs, a provider ecosystem, ClusterClass topologies, and multi-provider support.
    link: /cluster-api/
    linkText: Start Reading

  - icon: 🏗️
    title: Cluster API Provider Metal3
    details: Bare-metal Kubernetes provider integrating Ironic BareMetalHost, Metal3Machine and Metal3Cluster CRDs, IPAM support, and automated node remediation.
    link: /cluster-api-provider-metal3/
    linkText: Start Reading

  - icon: ☁️
    title: Cluster API Provider MAAS
    details: Canonical MAAS bare-metal provider for provisioning Machines through the MAAS API, with resource-pool filtering, DNS management, and in-memory deployment mode.
    link: /cluster-api-provider-maas/
    linkText: Start Reading

  - icon: 🔑
    title: etcd
    details: The distributed key-value store behind the Kubernetes control plane, with focused coverage of defrag, compaction, operational impact, and learner mode.
    link: /etcd/
    linkText: Start Reading

  - icon: 🔒
    title: NVIDIA OpenShell
    details: Secure sandboxed execution environment for AI agents, with declarative YAML policies, Docker/Podman/Kubernetes/MicroVM backends, L7 policy enforcement, and privacy-aware inference routing.
    link: /openshell/
    linkText: Start Reading

  - icon: 🤖
    title: NVIDIA NemoClaw
    details: Secure AI agent reference stack built on OpenShell, providing guided bootstrap flows, hardened blueprints, routed inference, network policy, and resident agent lifecycle management.
    link: /nemoclaw/
    linkText: Start Reading

---

## 📚 Project Overview

This site provides **source-code-level** analysis of open source projects in the KubeVirt ecosystem so engineers can understand design choices and implementation details quickly.

| Project | Description | Status |
|------|------|------|
| [KubeVirt](/kubevirt/architecture/overview) | Core platform for running virtual machines on Kubernetes | ✅ Complete analysis |
| [CDI](/containerized-data-importer/) | Data management framework for importing VM images into Kubernetes PVCs | ✅ Complete analysis |
| [Monitoring](/monitoring/) | Centralized monitoring infrastructure for the KubeVirt ecosystem | ✅ Complete analysis |
| [Common Instancetypes](/common-instancetypes/) | Standardized VM instance types and OS preferences | ✅ Complete analysis |
| [Node Maintenance Operator](/node-maintenance-operator/) | Kubernetes node maintenance automation operator | ✅ Complete analysis |
| [Forklift](/forklift/) | Automation platform for migrating VMs from multiple sources into KubeVirt | ✅ Complete analysis |
| [NetBox](/netbox/) | Network infrastructure management platform for IPAM and DCIM | ✅ Complete analysis |
| [Apache Kafka](/kafka/) | Distributed event-streaming platform | ✅ Complete analysis |
| [TiDB](/tidb/) | Distributed HTAP SQL database | ✅ Complete analysis |
| [Cluster API](/cluster-api/) | Kubernetes cluster lifecycle management framework | ✅ Complete analysis |
| [Cluster API Provider Metal3](/cluster-api-provider-metal3/) | Bare-metal Kubernetes cluster provider based on Ironic | ✅ Complete analysis |
| [Cluster API Provider MAAS](/cluster-api-provider-maas/) | Canonical MAAS bare-metal provider | ✅ Complete analysis |
| [etcd](/etcd/) | Distributed key-value store behind the Kubernetes control plane | ✅ Focused analysis |
| [NVIDIA OpenShell](/openshell/) | Secure sandboxed execution environment for AI agents | ✅ Complete analysis |
| [NVIDIA NemoClaw](/nemoclaw/) | Secure AI agent reference stack built on OpenShell | ✅ Complete analysis |


## 🔗 Source Repositories

All analysis on this site is based on the source code from the following GitHub repositories:

- **KubeVirt**: [github.com/kubevirt/kubevirt](https://github.com/kubevirt/kubevirt)
- **CDI**: [github.com/kubevirt/containerized-data-importer](https://github.com/kubevirt/containerized-data-importer)
- **Monitoring**: [github.com/kubevirt/monitoring](https://github.com/kubevirt/monitoring)
- **Common Instancetypes**: [github.com/kubevirt/common-instancetypes](https://github.com/kubevirt/common-instancetypes)
- **Node Maintenance Operator**: [github.com/medik8s/node-maintenance-operator](https://github.com/medik8s/node-maintenance-operator)
- **Forklift**: [github.com/kubev2v/forklift](https://github.com/kubev2v/forklift)
- **NetBox**: [github.com/netbox-community/netbox](https://github.com/netbox-community/netbox)
- **Apache Kafka**: [github.com/apache/kafka](https://github.com/apache/kafka)
- **TiDB**: [github.com/pingcap/tidb](https://github.com/pingcap/tidb)
- **Cluster API**: [github.com/kubernetes-sigs/cluster-api](https://github.com/kubernetes-sigs/cluster-api)
- **Cluster API Provider Metal3**: [github.com/metal3-io/cluster-api-provider-metal3](https://github.com/metal3-io/cluster-api-provider-metal3)
- **Cluster API Provider MAAS**: [github.com/spectrocloud/cluster-api-provider-maas](https://github.com/spectrocloud/cluster-api-provider-maas)
- **etcd**: [github.com/etcd-io/etcd](https://github.com/etcd-io/etcd)
- **NVIDIA OpenShell**: [github.com/NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell)
- **NVIDIA NemoClaw**: [github.com/NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw)
