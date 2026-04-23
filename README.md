# 📸 Screenshot Toolkit for AI Agents

跨平台截图工具集，支持全屏截图、窗口截图、指定区域截图、浏览器智能截图，兼容 Windows / macOS / Linux。

---

## 🗂️ 目录结构

```
screenshot-toolkit/
├── ps/                    # PowerShell（Windows 原生）
│   ├── screen_capture.ps1       # 全屏截图（兼容性好，DPI 缩放）
│   └── native_resolution.ps1     # Win32 API 原生分辨率（绕过 DPI 缩放）
├── py/                    # Python（跨平台）
│   ├── screen_capture.py         # Pillow 全平台截图
│   ├── native_resolution.py     # win32gui + ctypes，Windows 原生像素
│   └── requirements.txt
├── js/                    # JavaScript（Node.js）
│   ├── browser_screenshot.js    # Playwright 简单截图
│   └── smart_capture.js         # CDP 智能截图（等元素就绪）
├── README.md
└── LICENSE
```

---

## ⚡ 快速上手

### PowerShell（Windows，推荐）

```powershell
# 全屏截图（自动检测分辨率）
.\screen_capture.ps1

# 指定显示器（第二块屏幕）
.\screen_capture.ps1 -Monitor 1

# 输出到自定义路径
.\screen_capture.ps1 -Output "my_screenshot.png"

# ── Win32 原生分辨率（绕过 DPI 缩放）────────────────────────
# 捕获真实物理分辨率（如 2256×1504），不受 Windows DPI 虚拟化影响
.\native_resolution.ps1

# 捕获指定窗口（模糊匹配标题）
.\native_resolution.ps1 -WindowTitle "微信"

# 捕获指定区域
.\native_resolution.ps1 -Monitor 0

# 保存到自定义路径
.\native_resolution.ps1 -Output "native.png"
```

### Python（跨平台）

```bash
pip install Pillow

# 全屏截图
python screen_capture.py

# 指定显示器
python screen_capture.py --monitor 1

# 自定义路径
python screen_capture.py --output screenshot.png

# ── Win32 原生分辨率 ───────────────────────────────────────
# 需要：pip install Pillow pywin32
python native_resolution.py                    # 主屏幕
python native_resolution.py --monitor 1        # 第二屏幕
python native_resolution.py --window "微信"    # 按窗口标题截取
python native_resolution.py --region 0 0 800 600  # 指定区域
```

### JavaScript（Node.js，浏览器截图）

```bash
npm install playwright
node browser_screenshot.js https://example.com out.png

# ── CDP 智能截图（等待元素、模拟设备）────────────────────
node smart_capture.js <url> [output.png]
  --wait-selector ".main"      # 等待 CSS 选择器出现再截图
  --wait-time 3000             # 等待毫秒数
  --full-page                  # 截取整个页面（不只是视口）
  --viewport=1920,1080         # 自定义视口尺寸
  --clip=0,0,800,600           # 裁剪区域
  --emulate="iPhone 12"       # 模拟设备（iPhone 12 / iPhone 12 Pro / Pixel 5 / iPad Pro 11）
```

---

## 📐 四种截图模式对比

| 模式 | 工具 | 分辨率 | DPI 缩放 | 适用场景 |
|------|------|--------|---------|---------|
| 全屏截图 | PowerShell / Python Pillow | 逻辑分辨率 | 受影响 | 通用场景，兼容性好 |
| **原生分辨率** | `native_resolution.ps1` / `native_resolution.py` | 真实物理像素 | **绕过** | AI 视觉、桌面 UI 自动化、需要精确像素的场景 |
| 窗口截图 | `native_resolution.ps1 -WindowTitle` | 窗口实际大小 | 绕过 | 捕获特定应用界面 |
| 浏览器截图 | `browser_screenshot.js` / `smart_capture.js` | 视口大小 | 不适用 | 网页截图、UI 设计稿 |

---

## 🎯 使用场景

### 场景 1：AI 视觉识别桌面内容
```
用 native_resolution.ps1 捕获桌面 → 输入 AI 模型 → 返回操作指令
```
**为什么用原生分辨率？** Windows 会把低 DPI 显示的内容"虚拟化"放大，
普通截图会得到放大后的图像，影响 AI 识别准确率。

### 场景 2：自动化网页截图
```bash
# 等文章正文加载完成再截图（不截半屏空白）
node smart_capture.js https://mp.weixin.qq.com/s/xxx article.png --wait-selector "#js_content"
```

### 场景 3：多显示器分屏截图
```powershell
# 左边显示器
.\native_resolution.ps1 -Monitor 0 -Output "left.png"
# 右边显示器
.\native_resolution.ps1 -Monitor 1 -Output "right.png"
```

---

## 📋 环境依赖

| 脚本 | 依赖 | 安装 |
|------|------|------|
| `screen_capture.ps1` | Windows PowerShell 5.1+ | 内置，无需安装 |
| `native_resolution.ps1` | Windows PowerShell 5.1+ | 内置，无需安装 |
| `screen_capture.py` | Python 3 + Pillow | `pip install Pillow` |
| `native_resolution.py` | Python 3 + Pillow + pywin32 | `pip install Pillow pywin32` |
| `browser_screenshot.js` | Node.js + Playwright | `npm install playwright && npx playwright install chromium` |
| `smart_capture.js` | Node.js + Playwright | 同上 |

---

## 🤝 贡献

欢迎提交 Issue 和 PR！支持的贡献形式：
- 新平台支持（Linux 特定工具、macOS 特定工具）
- 新功能（区域截图、GIF 录制、视频录制）
- Bug 修复和文档改进

---

## 📄 License

MIT License — 详见 [LICENSE](LICENSE)