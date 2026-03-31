import{_ as a,o as n,c as i,ag as p}from"./chunks/framework.DU5ARZ07.js";const E=JSON.parse('{"title":"VM 生命週期流程","description":"","frontmatter":{},"headers":[],"relativePath":"architecture/lifecycle.md","filePath":"architecture/lifecycle.md","lastUpdated":null}'),l={name:"architecture/lifecycle.md"};function t(e,s,h,k,r,d){return n(),i("div",null,[...s[0]||(s[0]=[p(`<h1 id="vm-生命週期流程" tabindex="-1">VM 生命週期流程 <a class="header-anchor" href="#vm-生命週期流程" aria-label="Permalink to &quot;VM 生命週期流程&quot;">​</a></h1><p>本頁詳細說明 VirtualMachine (VM) 與 VirtualMachineInstance (VMI) 的完整生命週期，包含建立、執行、遷移、停止的每個步驟。</p><h2 id="vm-與-vmi-的關係" tabindex="-1">VM 與 VMI 的關係 <a class="header-anchor" href="#vm-與-vmi-的關係" aria-label="Permalink to &quot;VM 與 VMI 的關係&quot;">​</a></h2><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>VirtualMachine (VM)</span></span>
<span class="line"><span>├── 持久存在，即使 VM 停止，此物件仍在</span></span>
<span class="line"><span>├── 包含 RunStrategy 控制 VM 的執行策略</span></span>
<span class="line"><span>├── 包含 DataVolumeTemplates 管理磁碟</span></span>
<span class="line"><span>└── 當 running=true 或 RunStrategy=Always 時</span></span>
<span class="line"><span>    └── 建立 VirtualMachineInstance (VMI)</span></span>
<span class="line"><span>            ├── 暫態物件，代表「正在執行的 VM」</span></span>
<span class="line"><span>            ├── 包含 spec.nodeName（被調度到哪個節點）</span></span>
<span class="line"><span>            └── 關機後被刪除（VM 物件仍保留）</span></span></code></pre></div><h3 id="runstrategy-策略" tabindex="-1">RunStrategy 策略 <a class="header-anchor" href="#runstrategy-策略" aria-label="Permalink to &quot;RunStrategy 策略&quot;">​</a></h3><table tabindex="0"><thead><tr><th>策略</th><th>說明</th></tr></thead><tbody><tr><td><code>Always</code></td><td>如果 VMI 停止就自動重啟</td></tr><tr><td><code>Halted</code></td><td>不自動啟動，等待手動操作</td></tr><tr><td><code>Manual</code></td><td>由使用者手動控制 start/stop</td></tr><tr><td><code>RerunOnFailure</code></td><td>僅在 VMI 失敗時重啟，正常關機後不重啟</td></tr><tr><td><code>Once</code></td><td>只啟動一次，停止後不再重啟</td></tr><tr><td><code>WaitAsReceiver</code></td><td>等待作為 Migration 目標接收方</td></tr></tbody></table><h2 id="vmi-狀態轉換圖" tabindex="-1">VMI 狀態轉換圖 <a class="header-anchor" href="#vmi-狀態轉換圖" aria-label="Permalink to &quot;VMI 狀態轉換圖&quot;">​</a></h2><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>                   kubectl apply VM</span></span>
<span class="line"><span>                        │</span></span>
<span class="line"><span>                        ▼</span></span>
<span class="line"><span>                   ┌─────────┐</span></span>
<span class="line"><span>                   │ Pending  │  ← virt-controller 建立 Pod，等待調度</span></span>
<span class="line"><span>                   └────┬────┘</span></span>
<span class="line"><span>                        │ Pod 被調度到節點</span></span>
<span class="line"><span>                        ▼</span></span>
<span class="line"><span>                 ┌────────────┐</span></span>
<span class="line"><span>                 │ Scheduling  │  ← virt-handler 開始處理</span></span>
<span class="line"><span>                 └─────┬──────┘</span></span>
<span class="line"><span>                       │ 節點準備完成</span></span>
<span class="line"><span>                       ▼</span></span>
<span class="line"><span>                 ┌───────────┐</span></span>
<span class="line"><span>                 │ Scheduled  │  ← libvirt domain 定義完成</span></span>
<span class="line"><span>                 └─────┬─────┘</span></span>
<span class="line"><span>                       │ QEMU 啟動</span></span>
<span class="line"><span>                       ▼</span></span>
<span class="line"><span>                 ┌─────────┐</span></span>
<span class="line"><span>                 │ Running  │  ← VM 正常執行</span></span>
<span class="line"><span>                 └────┬────┘</span></span>
<span class="line"><span>                      │</span></span>
<span class="line"><span>          ┌───────────┼───────────┐</span></span>
<span class="line"><span>          ▼           ▼           ▼</span></span>
<span class="line"><span>    ┌──────────┐ ┌─────────┐ ┌──────────┐</span></span>
<span class="line"><span>    │ Migrating│ │ Paused  │ │Succeeded │</span></span>
<span class="line"><span>    └────┬─────┘ └────┬────┘ └──────────┘</span></span>
<span class="line"><span>         │            │</span></span>
<span class="line"><span>         ▼            ▼</span></span>
<span class="line"><span>      Running      Running</span></span>
<span class="line"><span>   (新節點上)    (unpause 後)</span></span>
<span class="line"><span>                             ┌──────────┐</span></span>
<span class="line"><span>                             │  Failed  │</span></span>
<span class="line"><span>                             └──────────┘</span></span></code></pre></div><h2 id="vm-可列印狀態-printablestatus" tabindex="-1">VM 可列印狀態 (PrintableStatus) <a class="header-anchor" href="#vm-可列印狀態-printablestatus" aria-label="Permalink to &quot;VM 可列印狀態 (PrintableStatus)&quot;">​</a></h2><p>使用者可透過 <code>kubectl get vm</code> 看到以下狀態：</p><table tabindex="0"><thead><tr><th>狀態</th><th>說明</th></tr></thead><tbody><tr><td><code>Stopped</code></td><td>VM 已停止，VMI 不存在</td></tr><tr><td><code>Provisioning</code></td><td>等待 DataVolume 準備完成</td></tr><tr><td><code>Starting</code></td><td>VM 正在啟動中</td></tr><tr><td><code>Running</code></td><td>VM 正在執行</td></tr><tr><td><code>Paused</code></td><td>VM 已暫停</td></tr><tr><td><code>Stopping</code></td><td>VM 正在停止中</td></tr><tr><td><code>Terminating</code></td><td>VM 正在終止</td></tr><tr><td><code>CrashLoopBackOff</code></td><td>VM 持續崩潰，進入回退等待</td></tr><tr><td><code>Migrating</code></td><td>VM 正在 Live Migration</td></tr><tr><td><code>WaitingForVolumeBinding</code></td><td>等待 PVC 綁定</td></tr><tr><td><code>DataVolumeError</code></td><td>DataVolume 發生錯誤</td></tr><tr><td><code>ErrorUnschedulable</code></td><td>找不到合適的節點</td></tr><tr><td><code>ErrImagePull</code> / <code>ImagePullBackOff</code></td><td>映像檔拉取失敗</td></tr></tbody></table><h2 id="詳細建立流程" tabindex="-1">詳細建立流程 <a class="header-anchor" href="#詳細建立流程" aria-label="Permalink to &quot;詳細建立流程&quot;">​</a></h2><h3 id="步驟-1-使用者提交-vm-定義" tabindex="-1">步驟 1：使用者提交 VM 定義 <a class="header-anchor" href="#步驟-1-使用者提交-vm-定義" aria-label="Permalink to &quot;步驟 1：使用者提交 VM 定義&quot;">​</a></h3><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">apiVersion</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">kubevirt.io/v1</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">kind</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">VirtualMachine</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">metadata</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  name</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">my-vm</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  namespace</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">default</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">spec</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  runStrategy</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">Always</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  template</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">    spec</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">      domain</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">        cpu</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">          cores</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;">2</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">        memory</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">          guest</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">4Gi</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">        devices</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">          disks</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">          - </span><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">name</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">rootdisk</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">            disk</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">              bus</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">virtio</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">          interfaces</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">          - </span><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">name</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">default</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">            masquerade</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: {}</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">      networks</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">      - </span><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">name</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">default</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">        pod</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: {}</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">      volumes</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">      - </span><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">name</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">rootdisk</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">        containerDisk</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">          image</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">quay.io/kubevirt/fedora-cloud-container-disk-demo:latest</span></span></code></pre></div><h3 id="步驟-2-virt-api-處理" tabindex="-1">步驟 2：virt-api 處理 <a class="header-anchor" href="#步驟-2-virt-api-處理" aria-label="Permalink to &quot;步驟 2：virt-api 處理&quot;">​</a></h3><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>POST /apis/kubevirt.io/v1/namespaces/default/virtualmachines</span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>Mutating Webhook (virt-api)</span></span>
<span class="line"><span>  ● 補齊預設值 (terminationGracePeriodSeconds: 180)</span></span>
<span class="line"><span>  ● 設定預設網路介面模型</span></span>
<span class="line"><span>  ● 加入必要的 annotations</span></span>
<span class="line"><span></span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>Validating Webhook (virt-api)</span></span>
<span class="line"><span>  ● 驗證 CPU/Memory 設定</span></span>
<span class="line"><span>  ● 驗證磁碟與 Volume 對應</span></span>
<span class="line"><span>  ● 驗證網路設定</span></span>
<span class="line"><span>  ● 檢查 Instancetype 衝突</span></span>
<span class="line"><span></span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>寫入 VirtualMachine CR 到 etcd</span></span></code></pre></div><h3 id="步驟-3-virt-controller-vm-控制器" tabindex="-1">步驟 3：virt-controller (VM 控制器) <a class="header-anchor" href="#步驟-3-virt-controller-vm-控制器" aria-label="Permalink to &quot;步驟 3：virt-controller (VM 控制器)&quot;">​</a></h3><div class="language-go vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">go</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">// pkg/virt-controller/watch/vm/vm.go</span></span>
<span class="line"><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">func</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;"> (</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">c </span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">*</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">Controller</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) </span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">sync</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">(</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">vm</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> *</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">v1</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">.</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">VirtualMachine</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) {</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 1. 計算期望狀態 (running=true → 需要 VMI)</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 2. 取得目前的 VMI</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 3. 若 VMI 不存在 → 建立 VMI</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 4. 若 VM 停止 → 刪除 VMI</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 5. 處理 DataVolumeTemplates</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 6. 更新 VM status</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">}</span></span></code></pre></div><h3 id="步驟-4-virt-controller-vmi-控制器" tabindex="-1">步驟 4：virt-controller (VMI 控制器) <a class="header-anchor" href="#步驟-4-virt-controller-vmi-控制器" aria-label="Permalink to &quot;步驟 4：virt-controller (VMI 控制器)&quot;">​</a></h3><div class="language-go vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">go</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">// pkg/virt-controller/watch/vmi/vmi.go</span></span>
<span class="line"><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">func</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;"> (</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">c </span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">*</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">Controller</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) </span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">sync</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">(</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">vmi</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> *</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">v1</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">.</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">VirtualMachineInstance</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) {</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 1. 若 Pod 不存在 → 建立 virt-launcher Pod</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 2. Pod 調度後 → 更新 VMI.spec.nodeName</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 3. 監控 Pod 健康狀態</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 4. 更新 VMI 狀態 (phase, conditions)</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">}</span></span></code></pre></div><p><strong>建立的 virt-launcher Pod 包含：</strong></p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">apiVersion</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">v1</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">kind</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">Pod</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">metadata</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  name</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">virt-launcher-my-vm-xxxxx</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  labels</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">    kubevirt.io</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">virt-launcher</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">    kubevirt.io/created-by</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">&lt;VMI-UID&gt;</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">spec</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  containers</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">  - </span><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">name</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">compute</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">    image</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;">virt-launcher:latest</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    # privileged 容器，用於 libvirt/QEMU 管理</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">    securityContext</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">      privileged</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">: </span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;">true</span></span>
<span class="line"><span style="--shiki-light:#22863A;--shiki-dark:#85E89D;">  volumes</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">:</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">  # 掛載 PVC、ConfigMap、Secret 等</span></span></code></pre></div><h3 id="步驟-5-virt-handler-節點代理" tabindex="-1">步驟 5：virt-handler (節點代理) <a class="header-anchor" href="#步驟-5-virt-handler-節點代理" aria-label="Permalink to &quot;步驟 5：virt-handler (節點代理)&quot;">​</a></h3><div class="language-go vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">go</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">// pkg/virt-handler/controller.go</span></span>
<span class="line"><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">func</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;"> (</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">d </span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">*</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">VirtualMachineController</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) </span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">execute</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">(</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">key</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> string</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) </span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">error</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;"> {</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 1. 取得 VMI (spec.nodeName == 本節點)</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 2. 取得目前 libvirt domain 狀態</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 3. 比較期望狀態 vs 實際狀態</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 4. 呼叫 virt-launcher 執行同步</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    //    - 設定網路 (virt-handler 在 launcher netns 執行 CNI)</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    //    - 掛載儲存</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    //    - 同步 domain 定義</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">}</span></span></code></pre></div><p><strong>兩階段網路配置：</strong></p><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>Phase 1 (Privileged — virt-handler 執行):</span></span>
<span class="line"><span>  ● 在 virt-launcher Pod 的 network namespace 執行</span></span>
<span class="line"><span>  ● 收集 CNI 分配的 IP、MAC、路由資訊</span></span>
<span class="line"><span>  ● 建立 bridge/veth pair 基礎設施</span></span>
<span class="line"><span>  ● 快取網路配置到 /var/run/kubevirt-private/vif-cache-xxx.json</span></span>
<span class="line"><span></span></span>
<span class="line"><span>Phase 2 (Unprivileged — virt-launcher 執行):</span></span>
<span class="line"><span>  ● 讀取快取的網路配置</span></span>
<span class="line"><span>  ● 產生 libvirt domain XML 的網路部分</span></span>
<span class="line"><span>  ● 啟動 DHCP server (如需要)</span></span></code></pre></div><h3 id="步驟-6-virt-launcher" tabindex="-1">步驟 6：virt-launcher <a class="header-anchor" href="#步驟-6-virt-launcher" aria-label="Permalink to &quot;步驟 6：virt-launcher&quot;">​</a></h3><div class="language-go vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">go</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">// pkg/virt-launcher/virtwrap/manager.go</span></span>
<span class="line"><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">func</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;"> (</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">l </span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">*</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">LibvirtDomainManager</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) </span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">SyncVMI</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">(</span><span style="--shiki-light:#E36209;--shiki-dark:#FFAB70;">vmi</span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;"> *</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">v1</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">.</span><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">VirtualMachineInstance</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">, </span><span style="--shiki-light:#D73A49;--shiki-dark:#F97583;">...</span><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">) {</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 1. 將 VMI spec 轉換為 libvirt domain XML</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    //    (pkg/virt-launcher/virtwrap/converter/)</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 2. 透過 libvirt API 定義 domain</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 3. 啟動 domain (libvirt virDomainCreate)</span></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;">    // 4. QEMU 程序啟動，VM 開始執行</span></span>
<span class="line"><span style="--shiki-light:#24292E;--shiki-dark:#E1E4E8;">}</span></span></code></pre></div><h2 id="刪除-停止流程" tabindex="-1">刪除/停止流程 <a class="header-anchor" href="#刪除-停止流程" aria-label="Permalink to &quot;刪除/停止流程&quot;">​</a></h2><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>kubectl delete vm my-vm</span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>1. [virt-controller]</span></span>
<span class="line"><span>   ├── 設定 VMI 的 DeletionTimestamp</span></span>
<span class="line"><span>   └── 等待 VMI 終止</span></span>
<span class="line"><span></span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>2. [virt-handler]</span></span>
<span class="line"><span>   ├── 偵測到 VMI 刪除</span></span>
<span class="line"><span>   ├── 呼叫 virt-launcher 發送 ACPI 關機訊號</span></span>
<span class="line"><span>   └── 等待 QEMU 程序退出 (grace period: 180秒)</span></span>
<span class="line"><span></span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>3. [virt-launcher]</span></span>
<span class="line"><span>   ├── 收到關機訊號後轉發給 QEMU</span></span>
<span class="line"><span>   ├── 等待 VM 優雅關機</span></span>
<span class="line"><span>   └── 若超時 → 強制終止 QEMU</span></span>
<span class="line"><span></span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>4. [Kubernetes]</span></span>
<span class="line"><span>   ├── 刪除 virt-launcher Pod</span></span>
<span class="line"><span>   └── 清理 PVC、ConfigMap 等資源</span></span>
<span class="line"><span></span></span>
<span class="line"><span>        │</span></span>
<span class="line"><span>        ▼</span></span>
<span class="line"><span>5. [virt-controller]</span></span>
<span class="line"><span>   └── 更新 VM status (Stopped)</span></span>
<span class="line"><span>       (如果 RunStrategy=Always → 自動重新建立 VMI)</span></span></code></pre></div><h2 id="狀態更新流程" tabindex="-1">狀態更新流程 <a class="header-anchor" href="#狀態更新流程" aria-label="Permalink to &quot;狀態更新流程&quot;">​</a></h2><div class="language- vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang"></span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span>QEMU 域事件</span></span>
<span class="line"><span>    │</span></span>
<span class="line"><span>    ▼</span></span>
<span class="line"><span>virt-launcher (監聽 libvirt 事件)</span></span>
<span class="line"><span>    │ domain 狀態改變</span></span>
<span class="line"><span>    ▼</span></span>
<span class="line"><span>virt-handler (接收 launcher 通知)</span></span>
<span class="line"><span>    │ 更新 VMI status</span></span>
<span class="line"><span>    ▼</span></span>
<span class="line"><span>Kubernetes API Server</span></span>
<span class="line"><span>    │ VMI.Status 更新</span></span>
<span class="line"><span>    ▼</span></span>
<span class="line"><span>virt-controller (watch VMI 改變)</span></span>
<span class="line"><span>    │ 更新 VM status</span></span>
<span class="line"><span>    ▼</span></span>
<span class="line"><span>使用者可透過 kubectl get vm 看到最新狀態</span></span></code></pre></div><h2 id="常用狀態查詢指令" tabindex="-1">常用狀態查詢指令 <a class="header-anchor" href="#常用狀態查詢指令" aria-label="Permalink to &quot;常用狀態查詢指令&quot;">​</a></h2><div class="language-bash vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">bash</span><pre class="shiki shiki-themes github-light github-dark vp-code" tabindex="0"><code><span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;"># 查看 VM 狀態</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">kubectl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> get</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> vm</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">kubectl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> describe</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> vm</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> my-vm</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;"># 查看 VMI 詳細狀態</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">kubectl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> get</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> vmi</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">kubectl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> describe</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> vmi</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> my-vm</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;"># 查看 virt-launcher Pod</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">kubectl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> get</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> pod</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -l</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> kubevirt.io=virt-launcher</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;"># 查看 VM 事件</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">kubectl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> get</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> events</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> --field-selector</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> involvedObject.name=my-vm</span></span>
<span class="line"></span>
<span class="line"><span style="--shiki-light:#6A737D;--shiki-dark:#6A737D;"># 查看 virt-handler 日誌 (在目標節點上)</span></span>
<span class="line"><span style="--shiki-light:#6F42C1;--shiki-dark:#B392F0;">kubectl</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> logs</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -n</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> kubevirt</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> -l</span><span style="--shiki-light:#032F62;--shiki-dark:#9ECBFF;"> kubevirt.io=virt-handler</span><span style="--shiki-light:#005CC5;--shiki-dark:#79B8FF;"> --tail=100</span></span></code></pre></div>`,34)])])}const g=a(l,[["render",t]]);export{E as __pageData,g as default};
