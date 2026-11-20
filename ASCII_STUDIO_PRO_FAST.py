
import os
import sys
import math
import time
import shutil
import tempfile
import threading
import subprocess
import unicodedata
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
import numpy as np
import imageio.v2 as imageio
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageOps

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    TkinterDnD = None
    DND_FILES = None
    DND_AVAILABLE = False


BG = "#050505"
PANEL = "#09090b"
PANEL2 = "#17171b"
FG = "#f5f5f7"
MUTED = "#a4a4ad"
ACCENT = "#8b5cf6"
BLUE = "#60a5fa"
GREEN = "#00d084"
BORDER = "#29292f"

FONT_PATHS = [
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\lucon.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
]

RAMPS = {
    "Standard": " .'`^,:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Simple": " .:-=+*#%@",
    "Blocks": " ░▒▓█",
    "Dense": " .'`^,:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "·∙•●": " ·∙•●",
    "▪◾◼■": " ▪◾◼■"
}


UI_TEXT = {
    "DOSYA": "FILE", "＋  Dosya seç": "＋  Choose file", "Dosya seçilmedi": "No file selected",
    "GÖRÜNTÜ AYARLARI": "IMAGE SETTINGS", "ASCII çözünürlüğü": "ASCII resolution",
    "KARAKTER SETİ": "CHARACTER SET", "Özel karakterler (açık ton → koyu ton)": "Custom characters (light → dark)",
    "Ekle": "Add", "GÖRÜNÜM": "APPEARANCE", "Renkli": "Colour", "Monokrom": "Monochrome",
    "Negatif": "Negative", "VİDEO AYARLARI": "VIDEO SETTINGS", "Çıktı biçimi": "Output format",
    "◎  Dönüştür": "◎  Convert", "⊗  İptal": "⊗  Cancel", "▣  Kaydet": "▣  Save",
    "◉  CANLI ÖNİZLEME": "◉  LIVE PREVIEW",
    "ASCII önizleme alanı\n\nGörüntü burada gösterilecek.\n\nDosyayı bu alana sürükleyip bırak.": "ASCII preview area\n\nYour image will appear here.\n\nDrag and drop a file here.",
    "Ses açık": "Sound on", "Ses kapalı": "Sound off", "Ses": "Volume", "VLC gerekli": "VLC required",
    "Dosya seç veya sürükleyip bırak.": "Choose a file or drag and drop it here.",
    "karakter": "characters",
    "Karakter seti": "Character set", "En az 2 görünür karakter girmen gerekiyor.": "Enter at least 2 visible characters.",
    "Özel karakter seti eklendi": "Custom character set added",
    "Dönüştürme tamamlandı.": "Conversion completed.", "İşlem iptal edildi.": "Operation cancelled.",
    "Hata": "Error", "Uyarı": "Warning", "Bilgi": "Information",
    "Dosya açılamadı": "Could not open file", "Desteklenmeyen dosya biçimi": "Unsupported file format",
    "Dönüştürme başarısız": "Conversion failed", "Kaydet": "Save",
    "Dil / Language": "Dil / Language", "Türkçe": "Turkish", "English": "English",
    "Sürükle-bırak başlatılamadı: ": "Could not initialize drag and drop: ",
    "Dosya yükleme hatası": "File loading error", "Desteklenmeyen dosya": "Unsupported file",
    "Bu dosya türü desteklenmiyor.": "This file type is not supported.",
    "Dosya açılamadı": "Could not open file", "Görsel hazır.": "Image ready.",
    "Video okunamadı.": "Could not read video.", "Önce bir dosya seç.": "Choose a file first.",
    "İşlem iptal edildi": "Operation cancelled", "Dönüştürme işlemi iptal edildi. İlerleme sıfırlandı.": "Conversion was cancelled. Progress has been reset.",
    "Dönüştürme iptal edildi.": "Conversion cancelled.", "Önce dönüştürme işlemini tamamla.": "Complete the conversion first.",
    "Dosya kaydedildi:\n": "File saved:\n", "Başlıyor...": "Starting...",
    "Dönüştürülüyor...": "Converting...", "İptal ediliyor...": "Cancelling...",
    "%0 — İptal edildi": "%0 — Cancelled", "%100 — Tamamlandı": "%100 — Completed",
    "Önizleme hatası: ": "Preview error: ", "Video hazır.": "Video ready.",
}


VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"
}

IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".bmp"
}


def load_font(size=12):
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()



from functools import lru_cache

@lru_cache(maxsize=32)
def _glyph_atlas(font_path, font_size, ramp):
    """Build a fixed-cell glyph atlas, using symbol fonts for Unicode glyphs."""
    primary = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    # Put symbol-capable fonts before the monospace primary for Unicode glyphs.
    # Consolas/Lucida Console can return a tofu box for unsupported symbols.
    font_candidates = []
    for candidate in (
        r"C:\Windows\Fonts\seguisym.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(candidate) and candidate != font_path:
            try:
                font_candidates.append(ImageFont.truetype(candidate, font_size))
            except Exception:
                pass
    font_candidates.append(primary)

    bbox = primary.getbbox("M")
    cell_h = max(1, bbox[3] - bbox[1])
    try:
        cell_w = max(1, round(primary.getlength("M")))
    except Exception:
        cell_w = max(1, round(cell_h * 0.6))

    atlas = np.zeros((len(ramp), cell_h, cell_w), dtype=np.uint8)
    for i, char in enumerate(ramp):
        # Prefer the monospaced font for ASCII; prefer symbol fonts for Unicode.
        candidates = font_candidates if any(ord(c) > 127 for c in char) else [primary]
        glyph_font = candidates[0]
        if any(ord(c) > 127 for c in char):
            for candidate in candidates:
                try:
                    if candidate.getmask(char).getbbox() is not None:
                        glyph_font = candidate
                        break
                except Exception:
                    continue
        try:
            gb = glyph_font.getbbox(char)
            gw = max(1, gb[2] - gb[0])
            gh = max(1, gb[3] - gb[1])
            tile = Image.new("L", (cell_w, cell_h), 0)
            x = max(0, (cell_w - gw) // 2) - gb[0]
            y = max(0, (cell_h - gh) // 2) - gb[1]
            ImageDraw.Draw(tile).text((x, y), char, font=glyph_font, fill=255)
            atlas[i] = np.asarray(tile)
        except Exception:
            # Unsupported glyphs remain blank rather than crashing conversion.
            pass
    return atlas, cell_w, cell_h


def render_ascii(frame, columns=120, ramp_name="Standard", colour=True, negative=False):
    """Fast vectorized ASCII renderer. No effects; glyphs are composited in NumPy."""
    if isinstance(frame, Image.Image):
        source = frame.convert("RGB")
    else:
        arr = np.asarray(frame)
        if arr.ndim == 2:
            arr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_GRAY2RGB)
        elif arr.shape[2] == 4:
            arr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGBA2RGB)
        source = Image.fromarray(arr.astype(np.uint8)).convert("RGB")

    if negative:
        source = ImageOps.invert(source)

    src_w, src_h = source.size
    columns = max(20, min(240, int(columns)))
    ramp = RAMPS.get(ramp_name, ramp_name if isinstance(ramp_name, str) and len(ramp_name) >= 1 else RAMPS["Standard"])

    font_path = next((p for p in FONT_PATHS if os.path.exists(p)), None)
    atlas, cell_w, cell_h = _glyph_atlas(font_path, 12, ramp)

    rows = max(1, round(columns * (src_h / max(1, src_w)) * (cell_w / cell_h)))
    small = source.resize((columns, rows), Image.Resampling.BILINEAR)
    pixels = np.asarray(small, dtype=np.uint8)

    luminance = (0.2126 * pixels[:, :, 0] +
                 0.7152 * pixels[:, :, 1] +
                 0.0722 * pixels[:, :, 2])
    indices = np.clip(
        np.rint(luminance / 255.0 * (len(ramp) - 1)).astype(np.int16),
        0, len(ramp) - 1
    )

    # Atlas lookup creates all character masks in one vectorized operation.
    glyph_mask = atlas[indices].transpose(0, 2, 1, 3).reshape(
        rows * cell_h, columns * cell_w
    ) > 48

    if colour:
        cell_colours = np.minimum(
            255, (pixels.astype(np.float32) * 0.94 + 8)
        ).astype(np.uint8)
    else:
        grey = np.clip(luminance, 0, 255).astype(np.uint8)
        cell_colours = np.repeat(grey[:, :, None], 3, axis=2)

    colour_grid = np.repeat(np.repeat(cell_colours, cell_h, axis=0),
                            cell_w, axis=1)
    output = np.empty((rows * cell_h, columns * cell_w, 3), dtype=np.uint8)
    output[:] = (5, 7, 10)
    output[glyph_mask] = colour_grid[glyph_mask]
    return Image.fromarray(output, "RGB")


class AudioController:

    def __init__(self):
        self.player = None
        self.instance = None
        self.available = False

        try:
            if sys.platform == "win32":
                for path in (
                    r"C:\Program Files\VideoLAN\VLC",
                    r"C:\Program Files (x86)\VideoLAN\VLC"
                ):
                    if os.path.isdir(path):
                        try:
                            os.add_dll_directory(path)
                        except Exception:
                            pass

            import vlc

            self.instance = vlc.Instance(
                "--no-video", "--quiet"
            )
            self.player = self.instance.media_player_new()
            self.available = True

        except Exception:
            self.available = False

    def load(self, path):
        if self.available:
            media = self.instance.media_new(str(path))
            self.player.set_media(media)

    def play(self):
        if self.available:
            self.player.play()

    def pause(self):
        if self.available:
            self.player.set_pause(1)

    def stop(self):
        if self.available:
            self.player.stop()

    def seek(self, seconds):
        if self.available:
            self.player.set_time(
                int(max(0, seconds) * 1000)
            )

    def volume(self, value):
        if self.available:
            self.player.audio_set_volume(int(value))

    def mute(self, value):
        if self.available:
            self.player.audio_set_mute(bool(value))

    def close(self):
        if self.available:
            self.player.stop()


class RoundedButton(tk.Canvas):
    """Sharp, square-corner button drawn on a canvas for consistent styling."""
    def __init__(self, parent, text, command, bg="#17171c", fg=FG,
                 active_bg="#30303a", width=110, height=34, font=("Segoe UI", 9, "bold")):
        super().__init__(parent, width=width, height=height, bg=parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.text, self.command = text, command
        self.bg_color, self.fg_color, self.active_bg = bg, fg, active_bg
        self.font = font
        self.state = "normal"
        self._base_bg = bg
        self._base_fg = fg
        self._draw(bg)
        # Redraw to the actual widget dimensions. pack(fill="x") can make the
        # Canvas wider than its requested width; drawing only the requested
        # width leaves a visually empty but clickable strip.
        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda _e: self._draw(self.active_bg))
        self.bind("<Leave>", lambda _e: self._draw(self.bg_color))

    def _on_resize(self, _event=None):
        self._draw(self.bg_color)

    def _on_click(self, _event=None):
        if self.state == "normal" and callable(self.command):
            self.command()

    def configure(self, cnf=None, **kwargs):
        state = kwargs.pop("state", None)
        if state is not None:
            self.state = state
            if state == "disabled":
                self.bg_color = "#202024"
                self.fg_color = "#77777f"
            self._draw(self.bg_color)
        return super().configure(cnf, **kwargs)

    config = configure

    def _draw(self, color):
        self.delete("all")
        # Use the live size, not the constructor's requested size, so every
        # visible pixel belongs to the painted button surface.
        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height())
        self.create_rectangle(0, 0, w, h, fill=color, outline=color, width=1)
        self.create_text(w / 2, h / 2, text=self.text, fill=self.fg_color, font=self.font)


class ASCIIStudio:

    def __init__(self, root):
        self.root = root

        self.root.title("ASCII Studio Pro")
        self.root.geometry("1180x790")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)

        self.audio = AudioController()

        self.path = None
        self.cap = None

        self.fps = 25.0
        self.total_frames = 0
        self.duration = 0.0
        self.frame_no = 0

        self.playing = False
        self.muted = False
        self.seek_dragging = False

        self.after_id = None

        self.preview_image = None
        self.current_frame = None
        self.gif_frames = []
        self.gif_durations = []
        self.gif_index = 0
        self.gif_after_id = None
        self.gif_playing = False
        self.preview_busy = False
        self.pending_preview = None
        self.preview_token = 0
        self.settings_after_id = None
        self.play_start_time = 0.0
        self.play_start_frame = 0

        self.processing = False
        self.cancel_requested = False
        self.result_path = None

        self.columns = tk.IntVar(value=120)
        self.ramp = tk.StringVar(value="Standard")
        self.custom_ramp = tk.StringVar(value="")
        self.output_format = tk.StringVar(value="PNG")
        self.colour = tk.BooleanVar(value=True)
        self.negative = tk.BooleanVar(value=False)
        self.volume_value = tk.IntVar(value=75)
        self.language = "tr"
        self._text_widgets = []

        self._build()
        self._bind_setting_changes()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.setup_drag_drop()

    def _build(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Horizontal.TProgressbar", troughcolor="#242429", background=ACCENT,
                        bordercolor="#242429", lightcolor=ACCENT, darkcolor=ACCENT)
        self.root.title("ASCII Studio Pro")
        self.root.geometry("1380x860")
        self.root.minsize(1050, 680)
        self.root.configure(bg=BG)

        shell = tk.Frame(self.root, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill="both", expand=True, padx=10, pady=10)
        header = tk.Frame(shell, bg=BG)
        header.pack(fill="x", padx=18, pady=(12, 8))
        title_area = tk.Frame(header, bg=BG); title_area.pack(side="left", anchor="w")
        tk.Label(title_area, text="ASCII STUDIO", bg=BG, fg=FG,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(title_area, text="IMAGE, GIF & VIDEO CONVERTER", bg=BG, fg=BLUE,
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(2, 0))
        self.lang_button = tk.Button(header, text="TR | EN", command=self.toggle_language,
                                     bg="#202027", fg=FG, activebackground="#30303a",
                                     activeforeground=FG, relief="flat", padx=10, pady=4,
                                     font=("Segoe UI", 8, "bold"))
        self.lang_button.pack(side="right", anchor="n", padx=(0, 8))
        tk.Label(header, text="PRO", bg="#062817", fg=GREEN,
                 font=("Segoe UI", 8, "bold"), padx=9, pady=3).pack(side="right", anchor="n")

        body = tk.Frame(shell, bg=BG); body.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        left = tk.Frame(body, bg=BG, width=310); left.pack(side="left", fill="y", padx=(0, 12)); left.pack_propagate(False)
        right = tk.Frame(body, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="left", fill="both", expand=True)

        # File selection stays in the left column; drag-and-drop is handled
        # exclusively by the large preview surface on the right.
        self.section(left, "DOSYA")
        self.file_button = RoundedButton(left, "＋  Dosya seç", self.choose_file,
                                         bg="#25252c", active_bg="#353541", width=280, height=38)
        self.file_button.pack(fill="x", pady=(0, 7))
        self.file_label = tk.Label(left, text="Dosya seçilmedi", bg=BG, fg=MUTED,
                                   font=("Segoe UI", 8), anchor="w")
        self.file_label.pack(fill="x", pady=(0, 3))

        self.section(left, "GÖRÜNTÜ AYARLARI")
        row = tk.Frame(left, bg=BG); row.pack(fill="x")
        tk.Label(row, text="ASCII çözünürlüğü", bg=BG, fg=FG, font=("Segoe UI", 9)).pack(side="left")
        self.width_value = tk.Label(row, text="220 karakter", bg=BG, fg=FG, font=("Segoe UI", 9, "bold")); self.width_value.pack(side="right")
        self.columns.set(220)
        self.width_scale = tk.Scale(left, from_=40, to=240, variable=self.columns, orient="horizontal", showvalue=False,
                                     bg=BG, fg=FG, troughcolor="#28282e", activebackground=ACCENT,
                                     highlightthickness=0, bd=0, sliderrelief="flat", command=self._width_changed)
        self.width_scale.pack(fill="x", pady=(1, 5))

        self.section(left, "KARAKTER SETİ")
        self.ramp_box = ttk.Combobox(left, textvariable=self.ramp, state="readonly",
                                     values=list(RAMPS.keys()), font=("Segoe UI", 9))
        self.ramp_box.pack(fill="x", pady=(0, 5))
        tk.Label(left, text="Özel karakterler (açık ton → koyu ton)", bg=BG, fg=MUTED,
                 font=("Segoe UI", 7)).pack(anchor="w")
        custom_row = tk.Frame(left, bg=BG); custom_row.pack(fill="x", pady=(3, 0))
        self.custom_entry = tk.Entry(custom_row, textvariable=self.custom_ramp, bg="#111115", fg=FG,
                                     insertbackground=FG, relief="flat", font=("Consolas", 9))
        self.custom_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 5))
        self.add_ramp_button = RoundedButton(custom_row, "Ekle", self.add_custom_ramp,
                                             bg="#25252c", active_bg="#353541", width=58, height=29,
                                             font=("Segoe UI", 8, "bold"))
        self.add_ramp_button.pack(side="right")

        self.section(left, "GÖRÜNÜM")
        mode_row = tk.Frame(left, bg=BG); mode_row.pack(fill="x", pady=(0, 2))
        self.mode_buttons = {}
        for label, mode in (("Renkli", "colour"), ("Monokrom", "mono"), ("Negatif", "negative")):
            b = RoundedButton(mode_row, label, lambda m=mode: self.set_appearance(m),
                              bg="#17171c", active_bg="#30303a", width=88, height=29,
                              font=("Segoe UI", 8, "bold"))
            b.pack(side="left", padx=(0, 5)); self.mode_buttons[mode] = b
        self.set_appearance("colour", refresh=False)

        self.section(left, "VİDEO AYARLARI")
        video_row = tk.Frame(left, bg=BG); video_row.pack(fill="x", pady=(0, 4))
        tk.Label(video_row, text="FPS", bg=BG, fg=FG, font=("Segoe UI", 9)).pack(side="left")
        self.fps_label = tk.Label(video_row, text="30", bg=BG, fg=FG, font=("Segoe UI", 9, "bold")); self.fps_label.pack(side="right")
        output_row = tk.Frame(left, bg=BG); output_row.pack(fill="x", pady=(0, 5))
        tk.Label(output_row, text="Çıktı biçimi", bg=BG, fg=FG, font=("Segoe UI", 9)).pack(side="left")
        self.output_label = tk.Label(output_row, text="PNG", bg=BG, fg=FG, font=("Segoe UI", 9, "bold")); self.output_label.pack(side="right")

        self.progress = ttk.Progressbar(left, maximum=100, mode="determinate"); self.progress.pack(fill="x", pady=(5, 2))
        self.progress_text = tk.StringVar(value="")
        tk.Label(left, textvariable=self.progress_text, bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")

        # Actions live at the bottom of the left settings column.
        actions = tk.Frame(left, bg=BG); actions.pack(side="bottom", fill="x", pady=(8, 0))
        self.convert_button = RoundedButton(actions, "◎  Dönüştür", self.convert,
                                            bg="#25252c", active_bg="#383844", width=280, height=38)
        self.convert_button.pack(fill="x", pady=(0, 6))
        bottom_actions = tk.Frame(actions, bg=BG); bottom_actions.pack(fill="x")
        bottom_actions.grid_columnconfigure(0, weight=1, uniform="action")
        bottom_actions.grid_columnconfigure(1, weight=1, uniform="action")
        self.cancel_button = RoundedButton(bottom_actions, "⊗  İptal", self.cancel,
                                           bg="#19191e", active_bg="#303039", width=120, height=36,
                                           font=("Segoe UI", 8, "bold"))
        self.cancel_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.save_button = RoundedButton(bottom_actions, "▣  Kaydet", self.save_result,
                                         bg="#303035", active_bg="#414149", width=120, height=36,
                                         font=("Segoe UI", 8, "bold"))
        self.save_button.configure(state="disabled")
        self.save_button.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        self.section(right, "◉  CANLI ÖNİZLEME")
        self.preview_wrap = tk.Frame(right, bg="#030304", highlightbackground="#17171d", highlightthickness=1)
        self.preview_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.preview = tk.Label(self.preview_wrap, bg="#030304", fg=MUTED,
                                text="ASCII önizleme alanı\n\nGörüntü burada gösterilecek.\n\nDosyayı bu alana sürükleyip bırak.",
                                font=("Segoe UI", 10), justify="center")
        self.preview.pack(fill="both", expand=True, padx=8, pady=8)
        controls = tk.Frame(right, bg=BG); controls.pack(fill="x", padx=10, pady=(0, 4))
        self.play_button = tk.Button(controls, text="▶", command=self.toggle_play, bg="#202027", fg=FG,
                                     activebackground="#30303a", activeforeground=FG, relief="flat", width=4, pady=5)
        self.play_button.pack(side="left", padx=(0, 5))
        tk.Button(controls, text="■", command=self.stop_video, bg="#202027", fg=FG,
                  activebackground="#30303a", activeforeground=FG, relief="flat", width=4, pady=5).pack(side="left", padx=(0, 7))
        self.seek = tk.Scale(controls, from_=0, to=1000, orient="horizontal", showvalue=False, command=self.seek_changed,
                             bg=BG, fg=FG, troughcolor="#28282e", highlightthickness=0, activebackground=ACCENT, bd=0)
        self.seek.pack(side="left", fill="x", expand=True, padx=5)
        self.seek.bind("<ButtonPress-1>", self.seek_start); self.seek.bind("<ButtonRelease-1>", self.seek_end)
        self.time_label = tk.StringVar(value="00:00 / 00:00")
        tk.Label(controls, textvariable=self.time_label, bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="right", padx=(6, 0))
        audio_row = tk.Frame(right, bg=BG); audio_row.pack(fill="x", padx=10, pady=(0, 9))
        self.mute_button = tk.Button(audio_row, text="Ses açık", command=self.toggle_mute, bg="#202027", fg=FG,
                                     activebackground="#30303a", activeforeground=FG, relief="flat", padx=10, pady=4, font=("Segoe UI", 8))
        self.mute_button.pack(side="left")
        tk.Label(audio_row, text="Ses", bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", padx=(10, 5))
        tk.Scale(audio_row, from_=0, to=100, variable=self.volume_value, orient="horizontal", showvalue=False,
                 command=self.change_volume, length=130, bg=BG, fg=FG, troughcolor="#28282e",
                 highlightthickness=0, activebackground=ACCENT, bd=0).pack(side="left")
        if not self.audio.available:
            tk.Label(audio_row, text="VLC gerekli", bg=BG, fg="#eab308", font=("Segoe UI", 8)).pack(side="right")

        self.status = tk.StringVar(value="Dosya seç veya sürükleyip bırak.")
        tk.Label(shell, textvariable=self.status, bg=BG, fg=MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=18, pady=(0, 7))
        self._width_changed()
        self._collect_text_widgets()

    def _collect_text_widgets(self):
        self._text_widgets = []
        def walk(parent):
            for child in parent.winfo_children():
                try:
                    if child.winfo_class() in ("Label", "Button"):
                        original = child.cget("text")
                        if original in UI_TEXT:
                            self._text_widgets.append((child, original))
                    elif isinstance(child, RoundedButton):
                        original = child.text
                        if original in UI_TEXT:
                            self._text_widgets.append((child, original))
                except Exception:
                    pass
                walk(child)
        walk(self.root)

    def t(self, value):
        if not isinstance(value, str):
            return value
        if self.language == "en":
            if value in UI_TEXT:
                return UI_TEXT[value]
            if value.endswith(" karakter"):
                return value[:-9] + " characters"
            for tr, en in UI_TEXT.items():
                if value.startswith(tr):
                    return en + value[len(tr):]
        else:
            reverse = {en: tr for tr, en in UI_TEXT.items()}
            if value in reverse:
                return reverse[value]
            if value.endswith(" characters"):
                return value[:-11] + " karakter"
            for en, tr in reverse.items():
                if value.startswith(en):
                    return tr + value[len(en):]
        return value

    def toggle_language(self):
        self.language = "en" if self.language == "tr" else "tr"
        for widget, original in self._text_widgets:
            try:
                translated = self.t(original)
                if isinstance(widget, RoundedButton):
                    widget.text = translated
                    widget._draw(widget.bg_color)
                else:
                    widget.configure(text=translated)
            except Exception:
                pass
        self.root.title("ASCII Studio Pro" if self.language == "en" else "ASCII Studio Pro")
        self.lang_button.configure(text="EN | TR" if self.language == "en" else "TR | EN")
        try:
            self.width_value.configure(text=f"{self.columns.get()} " +
                                        ("characters" if self.language == "en" else "karakter"))
        except Exception:
            pass
        try:
            self.mute_button.configure(text=self.t("Ses kapalı" if self.muted else "Ses açık"))
        except Exception:
            pass
        try:
            self.status.set(self.t(self.status.get()))
            self.progress_text.set(self.t(self.progress_text.get()))
        except Exception:
            pass

    def add_custom_ramp(self):
        # NFC combines equivalent Unicode spellings (e.g. base letter + accent).
        # Keep intentional spaces and repeated glyphs because both affect the ramp.
        chars = unicodedata.normalize("NFC", self.custom_ramp.get())
        chars = "".join(ch for ch in chars if ch not in "\r\n\t" and unicodedata.category(ch) != "Cf")
        if len(chars) < 2:
            messagebox.showwarning(self.t("Karakter seti"), self.t("En az 2 görünür karakter girmen gerekiyor."))
            return

        base_name = "Özel: " + chars[:10]
        name = base_name
        suffix = 2
        while name in RAMPS and RAMPS[name] != chars:
            name = f"{base_name} ({suffix})"
            suffix += 1
        RAMPS[name] = chars
        self.ramp_box.configure(values=list(RAMPS.keys()))
        self.ramp.set(name)
        self.status.set((f"Custom character set added ({len(chars)} characters)." if self.language == "en" else f"Özel karakter seti eklendi ({len(chars)} karakter)."))
        self.settings_changed()

    def section(self, parent, title):
        tk.Label(parent, text=title, bg=BG, fg=FG, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 6))

    def _width_changed(self, *_):
        if hasattr(self, "width_value"):
            self.width_value.config(text=f"{self.columns.get()} " + ("characters" if self.language == "en" else "karakter"))
        if hasattr(self, "current_frame") and self.current_frame is not None:
            self.settings_changed()

    def set_appearance(self, mode, refresh=True):
        self.colour.set(mode == "colour")
        self.negative.set(mode == "negative")
        for key, button in getattr(self, "mode_buttons", {}).items():
            active = key == mode
            button.bg_color = ("#07351f" if active and mode == "colour" else "#20203a" if active else "#17171c")
            button.fg_color = (GREEN if active and mode == "colour" else BLUE if active else FG)
            button._draw(button.bg_color)
        if refresh and hasattr(self, "current_frame") and self.current_frame is not None:
            self.settings_changed()

    # ------------------------------------------------
    # DRAG AND DROP
    # ------------------------------------------------

    def setup_drag_drop(self):
        if not DND_AVAILABLE:
            self.status.set(
                "Sürükle-bırak için tkinterdnd2 kurulmalı."
            )
            return

        try:
            # Only the preview pane accepts dropped files. The root window is
            # intentionally not registered, preventing drops on random controls.
            for target in (self.preview_wrap, self.preview):
                target.drop_target_register(DND_FILES)
                target.dnd_bind("<<Drop>>", self.drop_file)

            self.status.set(
                "Dosyayı sağdaki önizleme alanına sürükleyip bırakabilirsin."
            )

        except Exception as error:
            self.status.set(
                "Sürükle-bırak başlatılamadı: " + str(error)
            )

    def drop_file(self, event):
        try:
            files = self.root.tk.splitlist(event.data)

            if not files:
                return

            path = files[0]

            if os.path.isfile(path):
                self.load_file(path)

        except Exception as error:
            messagebox.showerror(
                self.t("Dosya yükleme hatası"),
                str(error)
            )

    # ------------------------------------------------
    # SETTINGS
    # ------------------------------------------------

    def _bind_setting_changes(self):
        self.columns.trace_add(
            "write", self.settings_changed
        )
        self.ramp.trace_add(
            "write", self.settings_changed
        )
        self.colour.trace_add(
            "write", self.settings_changed
        )
        self.negative.trace_add(
            "write", self.settings_changed
        )

    def settings_changed(self, *_):
        # Slider changes are debounced; heavy rendering never runs on Tk's UI thread.
        if self.current_frame is None:
            return
        if self.settings_after_id is not None:
            try:
                self.root.after_cancel(self.settings_after_id)
            except Exception:
                pass
        self.settings_after_id = self.root.after(140, self._apply_settings_preview)

    def _apply_settings_preview(self):
        self.settings_after_id = None
        if self.current_frame is not None:
            self.show_frame(self.current_frame)

    # ------------------------------------------------
    # FILE LOADING
    # ------------------------------------------------

    def choose_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                (
                    "Desteklenen dosyalar",
                    "*.png *.jpg *.jpeg *.webp *.bmp *.gif "
                    "*.mp4 *.mkv *.mov *.avi *.webm *.m4v"
                ),
                ("Tüm dosyalar", "*.*")
            ]
        )

        if path:
            self.load_file(path)

    def load_file(self, path):
        path = os.path.abspath(path)

        if not os.path.isfile(path):
            return

        ext = Path(path).suffix.lower()

        if ext not in VIDEO_EXTENSIONS | IMAGE_EXTENSIONS | {".gif"}:
            messagebox.showwarning(
                self.t("Desteklenmeyen dosya"),
                self.t("Bu dosya türü desteklenmiyor.")
            )
            return

        self.stop_video()
        self.audio.stop()
        self.release_capture()
        self.stop_image_animation()

        self.path = path
        self.output_format.set("GIF" if ext == ".gif" else "MP4" if ext in VIDEO_EXTENSIONS else "PNG")
        self.output_label.config(text=self.output_format.get())
        self.file_label.config(
            text=Path(path).name
        )

        self.current_frame = None
        self.frame_no = 0
        self.gif_frames = []
        self.gif_durations = []
        self.gif_index = 0

        try:
            if ext in VIDEO_EXTENSIONS:
                self.open_video(path)

            elif ext == ".gif":
                self.load_gif(path)

            else:
                image = Image.open(path).convert("RGB")
                self.current_frame = np.asarray(image)
                self.show_frame(self.current_frame)
                self.start_image_animation()
                self.status.set(self.t("Görsel hazır."))

        except Exception as error:
            messagebox.showerror(
                self.t("Dosya açılamadı"),
                str(error)
            )

    def load_gif(self, path):
        """Load all composited GIF frames and start animated ASCII preview."""
        self.stop_image_animation()
        frames = []
        durations = []
        with Image.open(path) as gif:
            frame_count = getattr(gif, "n_frames", 1)
            for index in range(frame_count):
                gif.seek(index)
                # Pillow's seek() applies GIF disposal/compositing before convert().
                frame = gif.convert("RGB").copy()
                frames.append(np.asarray(frame))
                duration = gif.info.get("duration", 100)
                durations.append(max(20, int(duration or 100)))

        if not frames:
            raise RuntimeError("GIF dosyasında görüntülenebilir kare bulunamadı.")

        self.gif_frames = frames
        self.gif_durations = durations
        self.gif_index = 0
        self.frame_no = 0
        self.current_frame = self.gif_frames[0]
        self.show_frame(self.current_frame)
        self.start_image_animation()
        self.status.set(f"GIF önizlemesi çalışıyor · {len(frames)} kare")

    def open_video(self, path):
        self.cap = cv2.VideoCapture(path)

        if not self.cap.isOpened():
            self.cap = None
            raise RuntimeError("Video açılamadı.")

        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
        ) or 25.0

        if not 1 <= self.fps <= 240:
            self.fps = 25.0
        if hasattr(self, "fps_label"):
            self.fps_label.config(text="30")

        self.total_frames = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            ) or 0
        )

        self.duration = (
            self.total_frames / self.fps
            if self.total_frames else 0
        )

        ok, frame = self.cap.read()

        if ok:
            self.current_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )
            self.frame_no = 0
            self.show_frame(self.current_frame)

        self.cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            0
        )

        self.seek.configure(
            to=max(1, int(self.duration * 1000))
        )

        self.time_label.set(
            f"00:00 / {self.format_time(self.duration)}"
        )

        self.audio.load(path)
        self.audio.volume(
            self.volume_value.get()
        )
        self.audio.mute(self.muted)

        self.status.set(self.t("Video hazır."))

    # ------------------------------------------------
    # PREVIEW
    # ------------------------------------------------

    def show_frame(self, frame):
        if frame is None:
            return
        self.current_frame = frame
        self.preview_token += 1
        token = self.preview_token
        settings = self.settings_snapshot()
        frame_copy = np.asarray(frame).copy()

        if self.preview_busy:
            self.pending_preview = (frame_copy, self.frame_no, settings, token)
            return

        self._start_preview_render(frame_copy, self.frame_no, settings, token)

    def _start_preview_render(self, frame, frame_no, settings, token):
        self.preview_busy = True

        def worker():
            try:
                rendered = render_ascii(
                    frame, settings["columns"], settings["ramp"], settings["colour"], settings.get("negative", False)
                )
                error = None
            except Exception as exc:
                rendered, error = None, str(exc)

            def finish():
                self.preview_busy = False
                if error:
                    self.status.set("Önizleme hatası: " + error)
                elif token == self.preview_token and rendered is not None:
                    max_w = max(200, self.preview.winfo_width() - 20)
                    max_h = max(150, self.preview.winfo_height() - 20)
                    rendered.thumbnail((max_w, max_h), Image.Resampling.NEAREST)
                    self.preview_image = ImageTk.PhotoImage(rendered)
                    self.preview.configure(image=self.preview_image, text="")

                pending = self.pending_preview
                self.pending_preview = None
                if pending is not None:
                    self._start_preview_render(*pending)
                elif self.playing:
                    self.root.after(1, self.next_frame)

            try:
                self.root.after(0, finish)
            except tk.TclError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def start_image_animation(self):
        """Start or resume animated GIF preview using per-frame delays."""
        if not self.path or Path(self.path).suffix.lower() != ".gif":
            return
        if len(self.gif_frames) <= 1:
            self.gif_playing = False
            return
        self.stop_image_animation()
        self.gif_playing = True
        if hasattr(self, "play_button"):
            self.play_button.config(text="Ⅱ")
        self._schedule_gif_frame()

    def _schedule_gif_frame(self):
        if (not self.gif_playing or not self.gif_frames or not self.path
                or Path(self.path).suffix.lower() != ".gif"):
            return
        delay = self.gif_durations[self.gif_index]
        self.gif_after_id = self.root.after(delay, self._advance_gif_frame)

    def _advance_gif_frame(self):
        self.gif_after_id = None
        if not self.gif_playing or not self.gif_frames or not self.path:
            return
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.frame_no = self.gif_index
        self.show_frame(self.gif_frames[self.gif_index])
        self._schedule_gif_frame()

    def stop_image_animation(self):
        self.gif_playing = False
        if self.gif_after_id is not None:
            try:
                self.root.after_cancel(self.gif_after_id)
            except Exception:
                pass
            self.gif_after_id = None
        if hasattr(self, "play_button"):
            self.play_button.config(text="▶")

    def toggle_play(self):
        """Play/pause the currently loaded GIF or video preview."""
        if self.path and Path(self.path).suffix.lower() == ".gif":
            if self.gif_playing:
                self.stop_image_animation()
            else:
                self.start_image_animation()
            return

        if self.cap is None:
            return

        if self.playing:
            self.playing = False
            if self.after_id is not None:
                try:
                    self.root.after_cancel(self.after_id)
                except Exception:
                    pass
                self.after_id = None
            self.audio.pause()
            self.play_button.config(text="▶")
            return

        if self.total_frames <= 0:
            return
        if self.frame_no >= self.total_frames - 1:
            self.seek_to(0)
        self.playing = True
        self.play_start_frame = self.frame_no
        self.play_start_time = time.monotonic()
        self.play_button.config(text="Ⅱ")
        if not self.muted:
            self.audio.play()
            self.audio.seek(self.frame_no / max(self.fps, 1))
        self.schedule_next()

    def schedule_next(self):
        if self.playing and self.after_id is None and not self.preview_busy:
            self.after_id = self.root.after(1, self.next_frame)

    def next_frame(self):
        self.after_id = None
        if not self.playing or self.cap is None:
            return

        elapsed = max(0.0, time.monotonic() - self.play_start_time)
        target_frame = self.play_start_frame + int(elapsed * self.fps)
        target_frame = min(target_frame, max(0, self.total_frames - 1))

        if target_frame <= self.frame_no:
            delay = max(1, int(1000 / self.fps))
            self.after_id = self.root.after(delay, self.next_frame)
            return

        # Skip late frames rather than accumulating delay; render only the newest frame.
        delta = target_frame - self.frame_no
        if 0 < delta <= 8:
            # Sequential decoding is much cheaper than seeking on every frame.
            for _ in range(delta - 1):
                if not self.cap.grab():
                    self.stop_video()
                    return
            ok, frame = self.cap.read()
        else:
            # If rendering fell far behind, jump directly to the current clock position.
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ok, frame = self.cap.read()

        if not ok:
            self.stop_video()
            return

        self.frame_no = target_frame
        self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        position = self.frame_no / self.fps

        if not self.seek_dragging:
            self.seek.set(int(position * 1000))
        self.time_label.set(
            f"{self.format_time(position)} / {self.format_time(self.duration)}"
        )

        self.show_frame(self.current_frame)

        if self.frame_no >= self.total_frames - 1:
            # Let the last preview finish before stopping.
            self.playing = False
            self.audio.pause()
            self.play_button.config(text="▶")

    def stop_video(self):
        self.playing = False
        self.stop_image_animation()

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass

            self.after_id = None

        self.audio.stop()
        self.play_button.config(text="▶")

        if self.cap is not None:
            self.seek_to(0)
        elif self.path and Path(self.path).suffix.lower() == ".gif" and self.gif_frames:
            self.gif_index = 0
            self.frame_no = 0
            self.show_frame(self.gif_frames[0])

    def seek_start(self, _event):
        self.seek_dragging = True

    def seek_changed(self, value):
        if self.seek_dragging and self.duration:
            self.time_label.set(
                f"{self.format_time(float(value)/1000)} / "
                f"{self.format_time(self.duration)}"
            )

    def seek_end(self, _event):
        self.seek_dragging = False

        if self.cap is not None:
            self.seek_to(
                float(self.seek.get()) / 1000
            )

    def seek_to(self, seconds):
        if self.cap is None:
            return

        seconds = max(
            0,
            min(self.duration, seconds)
        )

        target = min(
            max(0, self.total_frames - 1),
            int(seconds * self.fps)
        )

        self.cap.set(
            cv2.CAP_PROP_POS_FRAMES,
            target
        )

        ok, frame = self.cap.read()

        if ok:
            self.frame_no = target
            self.current_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )
            self.show_frame(self.current_frame)

        self.seek.set(
            int(seconds * 1000)
        )

        self.time_label.set(
            f"{self.format_time(seconds)} / "
            f"{self.format_time(self.duration)}"
        )

        if self.playing:
            self.play_start_frame = target
            self.play_start_time = time.monotonic()
            if not self.muted:
                self.audio.seek(seconds)

    def toggle_mute(self):
        self.muted = not self.muted

        self.audio.mute(self.muted)

        self.mute_button.config(
            text="Ses kapalı" if self.muted else "Ses açık"
        )

        if self.playing:
            if self.muted:
                self.audio.pause()
            else:
                self.audio.play()
                self.audio.seek(
                    self.frame_no / self.fps
                )

    def change_volume(self, value):
        self.audio.volume(
            int(float(value))
        )

    @staticmethod
    def format_time(seconds):
        seconds = max(0, int(seconds))
        return (
            f"{seconds // 60:02d}:"
            f"{seconds % 60:02d}"
        )

    # ------------------------------------------------
    # CONVERSION
    # ------------------------------------------------

    def convert(self):
        if not self.path:
            messagebox.showinfo(
                "ASCII Studio",
                self.t("Önce bir dosya seç.")
            )
            return

        if self.processing:
            return

        self.stop_video()

        self.cancel_requested = False
        self.processing = True
        self.result_path = None

        self.save_button.config(
            state="disabled"
        )

        self.progress["value"] = 0
        self.progress_text.set(self.t("Başlıyor..."))
        self.status.set(self.t("Dönüştürülüyor..."))

        source = self.path
        settings = self.settings_snapshot()

        threading.Thread(
            target=self.convert_worker,
            args=(source, settings),
            daemon=True
        ).start()

    def settings_snapshot(self):
        return {
            "columns": self.columns.get(),
            "ramp": self.ramp.get(),
            "colour": self.colour.get(),
            "negative": self.negative.get()
        }

    def convert_worker(self, source, settings):
        try:
            ext = Path(source).suffix.lower()
            temp_dir = tempfile.gettempdir()

            if ext in VIDEO_EXTENSIONS:
                destination = tempfile.NamedTemporaryFile(
                    prefix="ascii_studio_output_",
                    suffix=".mp4",
                    dir=temp_dir,
                    delete=False
                ).name
                self._active_destination = destination
                self._active_temp_video = destination + ".silent.mp4"

                self.convert_video(
                    source,
                    destination,
                    settings
                )

            elif ext == ".gif":
                destination = tempfile.NamedTemporaryFile(
                    prefix="ascii_studio_output_",
                    suffix=".gif",
                    dir=temp_dir,
                    delete=False
                ).name
                self._active_destination = destination
                self._active_temp_video = None

                self.convert_gif(
                    source,
                    destination,
                    settings
                )

            else:
                destination = tempfile.NamedTemporaryFile(
                    prefix="ascii_studio_output_",
                    suffix=".png",
                    dir=temp_dir,
                    delete=False
                ).name
                self._active_destination = destination
                self._active_temp_video = None

                image = Image.open(source).convert("RGB")

                result = render_ascii(
                    image,
                    settings["columns"],
                    settings["ramp"],
                    settings["colour"], settings.get("negative", False)
                )

                if not self.cancel_requested:
                    result.save(destination)
                    self.set_progress(100)

            if self.cancel_requested:
                self.root.after(
                    0,
                    lambda: self.status.set(self.t("İşlem iptal edildi" ) + ".")
                )
                return

            self.result_path = destination

            self.root.after(
                0,
                lambda: self.save_button.config(
                    state="normal"
                )
            )

            self.root.after(
                0,
                lambda: self.status.set(
                    "Dönüştürme tamamlandı. Kaydet'e bas."
                )
            )

        except Exception as error:
            if not self.cancel_requested:
                self.root.after(
                    0,
                    lambda e=str(error): messagebox.showerror(
                        "Dönüştürme hatası", e
                    )
                )
                self.root.after(
                    0,
                    lambda: self.status.set("Dönüştürme başarısız.")
                )

        finally:
            was_cancelled = self.cancel_requested
            self.processing = False
            if was_cancelled:
                # Remove any incomplete output so it cannot be mistaken for a valid result.
                for candidate in (
                    getattr(self, "_active_destination", None),
                    getattr(self, "_active_temp_video", None),
                ):
                    if candidate and os.path.isfile(candidate):
                        try:
                            os.remove(candidate)
                        except OSError:
                            pass
                self.result_path = None
                self.root.after(0, self._finish_cancelled)
            else:
                self.root.after(0, self._finish_conversion_ui)

    def _finish_cancelled(self):
        self.progress.configure(value=0)
        self.progress_text.set(self.t("%0 — İptal edildi"))
        self.status.set(self.t("Dönüştürme iptal edildi."))
        self.save_button.config(state="disabled")
        messagebox.showwarning(
            "İşlem iptal edildi",
            self.t("Dönüştürme işlemi iptal edildi. İlerleme sıfırlandı.")
        )

    def _finish_conversion_ui(self):
        # Called on Tk's main thread after the worker has ended.
        if self.result_path and os.path.isfile(self.result_path):
            self.progress.configure(value=100)
            self.progress_text.set(self.t("%100 — Tamamlandı"))


    def convert_video(self, source, destination, settings):
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise RuntimeError("Video okunamadı.")

        source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        if not 1 <= source_fps <= 240:
            source_fps = 30.0
        fps = 30.0

        total = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        )

        ok, first = cap.read()

        if not ok:
            cap.release()
            raise RuntimeError(
                "Videoda kare bulunamadı."
            )

        rgb = cv2.cvtColor(
            first,
            cv2.COLOR_BGR2RGB
        )

        first_ascii = render_ascii(
            rgb,
            settings["columns"],
            settings["ramp"],
            settings["colour"],
            settings.get("negative", False)
        )

        width, height = first_ascii.size

        width += width % 2
        height += height % 2

        temp_video = destination + ".silent.mp4"
        self._active_temp_video = temp_video

        writer = cv2.VideoWriter(
            temp_video,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height)
        )

        if not writer.isOpened():
            cap.release()
            raise RuntimeError(
                "Video yazıcısı başlatılamadı."
            )

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        index = 0

        while True:
            if self.cancel_requested:
                break

            ok, bgr = cap.read()

            if not ok:
                break

            rgb = cv2.cvtColor(
                bgr,
                cv2.COLOR_BGR2RGB
            )

            ascii_frame = render_ascii(
                rgb,
                settings["columns"],
                settings["ramp"],
                settings["colour"], settings.get("negative", False)
            )

            if ascii_frame.size != (width, height):
                canvas = Image.new(
                    "RGB",
                    (width, height),
                    (0, 0, 0)
                )
                canvas.paste(ascii_frame, (0, 0))
                ascii_frame = canvas

            writer.write(
                cv2.cvtColor(
                    np.asarray(ascii_frame),
                    cv2.COLOR_RGB2BGR
                )
            )

            index += 1

            if total:
                self.set_progress(
                    min(90, index * 90 / total)
                )

        cap.release()
        writer.release()

        if self.cancel_requested:
            if os.path.exists(temp_video):
                os.remove(temp_video)
            return

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

        command = [
            ffmpeg, "-y",
            "-i", temp_video,
            "-i", source,
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            destination
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt" else 0
            )
        )
        while process.poll() is None:
            if self.cancel_requested:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                break
            time.sleep(0.08)
        stdout, stderr = process.communicate()

        if os.path.exists(temp_video):
            os.remove(temp_video)

        if self.cancel_requested:
            if os.path.exists(destination):
                try:
                    os.remove(destination)
                except OSError:
                    pass
            return

        if process.returncode != 0:
            raise RuntimeError(
                "FFmpeg birleştirme hatası:\n" +
                stderr.decode(errors="ignore")[-1800:]
            )

        self.set_progress(100)

    def convert_gif(self, source, destination, settings):
        gif = Image.open(source)

        frame_count = getattr(
            gif,
            "n_frames",
            1
        )

        frames = []
        durations = []

        for i in range(frame_count):
            if self.cancel_requested:
                break

            gif.seek(i)

            frame = gif.convert("RGB")

            ascii_frame = render_ascii(
                frame,
                settings["columns"],
                settings["ramp"],
                settings["colour"], settings.get("negative", False)
            )

            frames.append(
                np.asarray(ascii_frame)
            )

            durations.append(
                max(20, gif.info.get("duration", 80))
            )

            self.set_progress(
                (i + 1) * 100 / frame_count
            )

        if not self.cancel_requested and frames:
            imageio.mimsave(
                destination,
                frames,
                duration=[
                    d / 1000 for d in durations
                ],
                loop=0
            )

    def set_progress(self, value):
        self.root.after(
            0,
            lambda v=value:
            self.progress.configure(value=v)
        )

        self.root.after(
            0,
            lambda v=value:
            self.progress_text.set(f"%{int(v)}")
        )

    def cancel(self):
        if self.processing and not self.cancel_requested:
            self.cancel_requested = True
            self.status.set(self.t("İptal ediliyor..."))
            self.progress_text.set(self.t("İptal ediliyor..."))

    # ------------------------------------------------
    # SAVE
    # ------------------------------------------------

    def save_result(self):
        if (
            not self.result_path or
            not os.path.exists(self.result_path)
        ):
            messagebox.showwarning(
                "ASCII Studio",
                self.t("Önce dönüştürme işlemini tamamla.")
            )
            return

        ext = Path(self.result_path).suffix

        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile="ascii_output" + ext,
            filetypes=[
                (
                    ext.upper().replace(".", "") + " dosyası",
                    "*" + ext
                ),
                ("Tüm dosyalar", "*.*")
            ]
        )

        if path:
            shutil.copy2(
                self.result_path,
                path
            )

            messagebox.showinfo(
                "ASCII Studio",
                self.t("Dosya kaydedildi:\n") + path
            )

    # ------------------------------------------------
    # CLEANUP
    # ------------------------------------------------

    def release_capture(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def close(self):
        self.cancel_requested = True
        self.playing = False

        self.stop_image_animation()

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass

        self.audio.close()
        self.release_capture()
        self.root.destroy()


def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    ASCIIStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
