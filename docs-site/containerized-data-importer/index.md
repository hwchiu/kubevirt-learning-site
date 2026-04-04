# Containerized Data Importer (CDI)

**CDI** 是 KubeVirt 生態系中負責資料管理的核心元件，提供將虛擬機器磁碟映像匯入 Kubernetes PersistentVolumeClaim (PVC) 的能力。

## 專案資訊

- **GitHub**: [kubevirt/containerized-data-importer](https://github.com/kubevirt/containerized-data-importer)
- **功能定位**: 為 KubeVirt VM 提供磁碟映像的匯入、上傳、克隆功能

## 核心功能

- 從 HTTP/S3/Registry 等來源匯入 VM 映像至 PVC
- 支援 qcow2、raw、vmdk 等格式自動轉換
- PVC 之間的智慧克隆（host-assisted / CSI clone）
- 透過 DataVolume CRD 簡化工作流程
- Upload API 支援本地映像上傳

## 分析進度

::: warning 🚧 建置中
CDI 的原始碼分析正在進行中，後續將涵蓋以下主題：

- 系統架構總覽
- 核心元件（cdi-controller、cdi-importer、cdi-cloner、cdi-uploadserver）
- DataVolume 生命週期
- 資料傳輸機制
- 與 KubeVirt 的整合方式
:::
