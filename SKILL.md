---
name: image-edit
description: 对图像进行编辑操作。支持四种功能：变宽高比（aspect）、擦除对象（erase）、去除背景（rmbg）、通用编辑（edit）。当用户需要修改图片宽高比、移除图片中的对象、去除背景或进行自定义编辑时使用此技能。
---

# Image Edit - 图像编辑工具

对图像进行多种编辑操作。

## Usage

使用绝对路径运行脚本（不要先 cd 到 skill 目录）：

**变宽高比：**
```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py aspect <image_path> <aspect_ratio> [--output-dir DIR] [--output-name NAME]
```

**擦除对象：**
```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py erase <image_path> <target_object> [--output-dir DIR] [--output-name NAME]
```

**去除背景：**
```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py rmbg <image_path> [--output-dir DIR] [--output-name NAME]
```

**通用编辑：**
```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py edit <image_path> <edit_prompt> [--ratio RATIO] [--output-dir DIR] [--output-name NAME]
```

**重要:** 始终从用户当前工作目录运行，以便图像保存在用户工作的位置，而不是 skill 目录中。

## Common Parameters

所有命令支持以下可选参数：
- `--output-dir` - 输出目录（默认: result/image_edit_results）
- `--output-name` - 输出文件名（可选）

## Aspect Ratio Options

支持的宽高比选项：
- `1:1` - 正方形
- `4:3` - 横向标准
- `3:4` - 纵向标准
- `16:9` - 横向宽屏
- `9:16` - 纵向宽屏（手机竖屏）
- `3:2` - 横向照片
- `2:3` - 纵向照片
- `21:9` - 超宽
- `9:21` - 超高

用户请求映射：
- "正方形"、"1:1" → `1:1`
- "横屏"、"16:9"、"宽屏" → `16:9`
- "竖屏"、"9:16"、"手机屏" → `9:16`
- "4:3"、"标准" → `4:3`

## Filename Generation

生成文件名使用格式: `yyyy-mm-dd-hh-mm-ss-name.jpg`

**格式:** `{timestamp}-{descriptive-name}.jpg`
- Timestamp: 当前日期时间，格式 `yyyy-mm-dd-hh-mm-ss`（24小时制）
- Name: 描述性小写文本，用连字符分隔
- 描述部分保持简洁（通常1-5个词）
- 使用用户提示或对话的上下文
- 如不明确，使用随机标识符（如 `x9k2`、`a7b3`）

示例：
- 擦除水印 → `2025-01-19-20-30-05-remove-watermark.jpg`
- 改为9:16比例 → `2025-01-19-20-31-12-aspect-9-16.jpg`
- 去除背景 → `2025-01-19-20-32-33-remove-bg.jpg`
- 添加雪花效果 → `2025-01-19-20-33-48-snow-effect.jpg`

## Function Details

### 1. Change Aspect Ratio (aspect)

改变图片宽高比，保持内容不变。

```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py aspect input.jpg 16:9
python ~/.claude/skills/image_skill/scripts/image_edit.py aspect input.jpg 9:16 --output-name result.jpg
```

### 2. Erase Object (erase)

从图片中移除指定对象。

```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py erase photo.jpg "watermark"
python ~/.claude/skills/image_skill/scripts/image_edit.py erase photo.jpg "person in background"
python ~/.claude/skills/image_skill/scripts/image_edit.py erase photo.jpg "logo"
```

### 3. Remove Background (rmbg)

移除图片背景，只保留主体。

```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py rmbg portrait.jpg
python ~/.claude/skills/image_skill/scripts/image_edit.py rmbg product.png --output-dir ./output
```

### 4. General Edit (edit)

使用自定义指令编辑图片。

```bash
python ~/.claude/skills/image_skill/scripts/image_edit.py edit input.jpg "change the sky to a starry night"
python ~/.claude/skills/image_skill/scripts/image_edit.py edit input.jpg "add snow effect" --ratio 16:9
```

**可选参数:**
- `--ratio` - 输出宽高比（默认: auto，保持原比例）

## Prompt Handling

**对于擦除:** 将要擦除的对象描述传给 target_object 参数（如 "watermark"、"person in background"）

**对于通用编辑:** 将编辑指令传给 edit_prompt 参数（如 "add a rainbow in the sky"、"make it look like a watercolor painting"）

编辑指令使用英文效果最佳，保留用户的创意意图。

## Output

- 保存 JPG 到指定输出目录（默认: result/image_edit_results）
- 脚本输出生成图片的完整路径
- **不要回读图片** - 只需告知用户保存路径

## Notes

1. 输入图片支持常见格式：JPG、PNG、WEBP 等
2. 编辑指令使用英文效果最佳
