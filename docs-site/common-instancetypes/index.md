---
layout: doc
---

# Common Instancetypes 原始碼分析

## 專案簡介

**Common Instancetypes** 提供一組標準化的 VirtualMachineInstancetype 與 VirtualMachinePreference 定義，類似 AWS EC2 Instance Types 的概念，讓使用者能快速建立具有一致資源配置的虛擬機器。

- **GitHub**: [kubevirt/common-instancetypes](https://github.com/kubevirt/common-instancetypes)
- **License**: Apache 2.0
- **格式**: YAML (Kustomize)

## 文件導覽

| 文件 | 說明 |
|------|------|
| [系統架構](./architecture) | 專案結構、Kustomize 建置系統、版本管理、部署方式 |
| [核心功能分析](./core-features) | 7 大系列 43 種 Instancetype、18+ OS Preference、元件化設計 |
| [資源類型目錄](./resource-catalog) | CRD 型別定義、Label 規範、驗證測試架構 |
| [外部整合](./integration) | KubeVirt 整合、VirtualMachine 引用方式、Label 查詢 |
