# Macroni

[GitHub Repository → `srschreiber/macroni`](https://www.github.com/srschreiber/macroni)

**Macroni** is a domain-specific language (DSL) for GUI automation with built-in OCR, template matching, and screen interaction. Human-like randomness is baked into all operations, including cubic Bézier mouse movement and randomized playback.

Macroni features:

- Line-by-line debugging with breakpoints
- Expression evaluation via a REPL
- High-level abstractions over computer vision and input simulation
- A full interpreted language defined in EBNF
- Parsing via **Lark**
- Execution via a **tree-walking interpreter in Python**

It runs on **Linux, macOS, and Windows** with no special setup beyond Python.

---

## Installation

### 1. Install Python Dependencies

```bash
pip install macroni
```

!!! note
    PyTorch **CPU** is installed by default.  
    If you have an NVIDIA GPU with CUDA support, reinstall PyTorch manually for GPU acceleration.

#### Reinstall PyTorch with CUDA

```bash
python -m pip uninstall -y torch torchvision torchaudio
```

Then install CUDA wheels (may take some time):

```bash
python -m pip install torch torchvision torchaudio   --index-url https://download.pytorch.org/whl/cu126
```

---

### 2. System Permissions

!!! warning "macOS Required Permission"
    Go to **System Settings → Privacy & Security → Accessibility**  
    Grant permission to **Terminal / Python** so Macroni can control your computer.

---

### 3. VS Code Extension

For syntax highlighting and language support, install:

**Macroni Language Support** (VS Code extension)

---

## Usage

### Interactive REPL

Start an interactive Read-Eval-Print Loop:

```bash
macroni
```

---

### Execute a File

```bash
macroni --file script.macroni
```

!!! note
    The first run may take longer because PyTorch is a large dependency.

---

## Debug Mode

Enable interactive debugging with breakpoints:

```bash
# Enable debug mode
macroni --file script.macroni --debug

# Set breakpoints at specific lines
macroni --file script.macroni --debug --breakpoints 10 --breakpoints 25

# Short flags
macroni -f script.macroni -d -b 10 -b 25
```

### Debug Commands

| Command | Description |
|------|-------------|
| `n` | Execute next line |
| `c` | Continue to next breakpoint |
| `p <var>` | Print variable |
| `eval <expr>` | Evaluate expression |
| `q` | Quit debugger |

---

## OCR Text Search

Find and click text on the screen:

```macroni
region = @capture_region("login_area", false);
results = @ocr_find_text(region, 0.8, "Login", 1.0);

if @len(results) > 0 {
    text, conf, bbox = results[0];
    x1, y1 = bbox[0];
    @mouse_move(x1, y1, 500, true);
    @left_click();
}
```

---

## Template Matching

```macroni
@set_template_dir("./templates");
x, y = @find_template("login_button");

if x != null {
    @mouse_move(x, y, 1000, true);
    @left_click();
}
```

---

## Cache Files

Auto-created in the working directory:

- `regions_cache.json`
- `coordinates_cache.json`
- `pixel_colors_cache.json`
- `recordings_cache.json`
