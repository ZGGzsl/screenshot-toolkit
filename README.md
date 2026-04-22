# screenshot-toolkit 📸

> 零依赖、开箱即用的截图工具包，AI Agent 专用

支持 3 种截图方式，覆盖 Windows / macOS / Linux 全平台：

| 方式 | 文件 | 依赖 | 适用场景 |
|------|------|------|----------|
| PowerShell | `ps/screen_capture.ps1` | 无 | Windows 桌面截图（最快） |
| Python | `py/screen_capture.py` | Pillow | 全平台桌面截图 |
| Browser API | `js/browser_screenshot.js` | Playwright | 网页截图（含完整渲染） |

## 快速使用

### Windows PowerShell（推荐）
```powershell
# 截取全屏 → screenshot.png
.\ps\screen_capture.ps1

# 指定分辨率
.\ps\screen_capture.ps1 -Width 1920 -Height 1080

# 指定输出路径
.\ps\screen_capture.ps1 -Output "D:\screenshots\test.png"
```

### Python
```python
# 全平台桌面截图
python py/screen_capture.py

# 指定输出
python py/screen_capture.py --output screenshot.png
```

### Playwright 网页截图
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    page.screenshot(path="webpage.png", full_page=True)
    browser.close()
```

## 为什么做这个？

AI Agent（如 OpenClaw、Claude Desktop）经常需要"看看屏幕"：
- 调试 GUI 自动化时检查当前界面状态
- 验证脚本执行后的视觉结果
- 抓取网页内容生成报告
- 远程监控任务进度

但市面上没有一款工具是**为 Agent 设计**的——要么太重（需安装 Electron 应用），要么太复杂（配置繁琐）。

这个工具包的哲学：
1. **零配置** — 复制即用，不需要安装任何东西（PowerShell 版）
2. **极简输出** — 只返回图片路径，方便 Agent 后续处理
3. **多语言** — PowerShell / Python / JS 三种调用方式，适配不同 Agent 运行时
4. **全平台** — Windows / macOS / Linux 都能跑

## 参数说明

### PowerShell 版
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-Width` | 屏幕宽度 | 截图宽度（像素） |
| `-Height` | 屏幕高度 | 截图高度（像素） |
| `-Output` | `screenshot.png` | 输出文件路径 |
| `-Monitor` | `0` | 显示器编号（多屏时） |

### Python 版
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--output` | `screenshot.png` | 输出文件路径 |
| `--monitor` | `0` | 显示器编号 |
| `--region` | None | 指定区域 x,y,w,d |
| `--format` | `png` | 输出格式 (png/jpg/webp) |

## License

MIT © [ZGGzsl](https://github.com/ZGGzsl)
