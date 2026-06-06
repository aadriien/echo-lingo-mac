import customtkinter as ctk

MAX_ROWS  = 4
MAX_CHARS = 30

# Local palette (mirrors gui_app.py)
CARD_BG  = "#FFFFFF"
ROW_BG   = "#FFF3E0"
DIVIDER  = "#FFE0B2"
TEXT_FG  = "#1A1A1A"
SUBTEXT  = "#8D6E63"
TITLE_FG = "#FF6D00"
GREEN    = "#58CC02"
RED_FG   = "#FF4B4B"
SEL      = "#FFB74D"


class SummaryCard(ctk.CTkToplevel):
    """Modal notecard for reviewing and editing summary bullets before saving."""

    def __init__(self, parent, bullets: list[str]):
        super().__init__(parent)
        self.result: list[str] = list(bullets)

        self.configure(fg_color=CARD_BG)
        self.title("")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_confirm)

        self._rows: list[dict] = []
        self._build(bullets)
        self._center_on(parent)

        self.grab_set()
        self.wait_window()

    # ── layout ────────────────────────────────────────────────────────────────

    def _build(self, bullets: list[str]):
        ctk.CTkLabel(
            self,
            text="Does this look right?",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TITLE_FG,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(16, 2))

        ctk.CTkLabel(
            self,
            text="Here's a quick recap of what you covered:",
            font=ctk.CTkFont(size=11),
            text_color=SUBTEXT,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 10))

        self._rows_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._rows_frame.pack(fill="x", padx=16)

        for text in bullets:
            self._append_row(text)

        # bottom frame: add_btn (row 0) + confirm_btn (row 1) in stable grid positions
        self._bottom = ctk.CTkFrame(self, fg_color="transparent")
        self._bottom.pack(fill="x", padx=16, pady=(8, 16))
        self._bottom.grid_columnconfigure(0, weight=1)

        self._add_btn = ctk.CTkButton(
            self._bottom,
            text="+ Add",
            height=30,
            fg_color="transparent",
            hover_color=DIVIDER,
            text_color=SUBTEXT,
            border_width=1,
            border_color=DIVIDER,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            command=self._on_add,
        )
        self._add_btn.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        ctk.CTkButton(
            self._bottom,
            text="✓  Looks good",
            height=40,
            fg_color=GREEN,
            hover_color="#4CAF00",
            text_color="#FFFFFF",
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_confirm,
        ).grid(row=1, column=0, sticky="ew")

        self._sync_add_btn()

    def _append_row(self, text: str):
        if len(self._rows) >= MAX_ROWS:
            return

        idx = len(self._rows)
        frame = ctk.CTkFrame(
            self._rows_frame,
            fg_color=ROW_BG,
            corner_radius=8,
            border_width=1,
            border_color=DIVIDER,
        )
        frame.pack(fill="x", pady=(0, 6))
        frame.grid_columnconfigure(0, weight=1)

        var = ctk.StringVar(value=text)

        label = ctk.CTkLabel(
            frame,
            textvariable=var,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_FG,
            anchor="w",
        )
        label.grid(row=0, column=0, sticky="ew", padx=(10, 4), pady=8)

        entry = ctk.CTkEntry(
            frame,
            textvariable=var,
            font=ctk.CTkFont(size=13),
            fg_color="#FFFFFF",
            border_color=SEL,
            border_width=2,
            corner_radius=6,
        )

        edit_btn = ctk.CTkButton(
            frame, text="✏", width=28, height=28,
            fg_color="transparent", hover_color=DIVIDER,
            text_color=SUBTEXT, corner_radius=6,
            font=ctk.CTkFont(size=13),
            command=lambda i=idx: self._toggle_edit(i),
        )
        edit_btn.grid(row=0, column=1, padx=(0, 2), pady=8)

        del_btn = ctk.CTkButton(
            frame, text="✕", width=28, height=28,
            fg_color="transparent", hover_color="#FFCDD2",
            text_color=RED_FG, corner_radius=6,
            font=ctk.CTkFont(size=13),
            command=lambda i=idx: self._delete_row(i),
        )
        del_btn.grid(row=0, column=2, padx=(0, 6), pady=8)

        self._rows.append({
            "frame":    frame,
            "var":      var,
            "label":    label,
            "entry":    entry,
            "edit_btn": edit_btn,
            "del_btn":  del_btn,
            "editing":  False,
            "trace_id": None,
        })

    # ── row editing ───────────────────────────────────────────────────────────

    def _toggle_edit(self, idx: int):
        row = self._rows[idx]
        if row["editing"]:
            self._stop_edit(idx)
        else:
            self._start_edit(idx)

    def _start_edit(self, idx: int):
        row = self._rows[idx]
        row["label"].grid_remove()
        row["entry"].grid(row=0, column=0, sticky="ew", padx=(10, 4), pady=8)
        row["edit_btn"].configure(
            text="✓", fg_color=GREEN, hover_color="#4CAF00", text_color="#FFFFFF",
        )
        row["trace_id"] = row["var"].trace_add("write", lambda *_: self._clamp(idx))
        row["entry"].focus_set()
        row["editing"] = True

    def _stop_edit(self, idx: int):
        row = self._rows[idx]
        if row["trace_id"]:
            row["var"].trace_remove("write", row["trace_id"])
            row["trace_id"] = None
        val = row["var"].get()
        if len(val) > MAX_CHARS:
            row["var"].set(val[:MAX_CHARS])
        row["entry"].grid_remove()
        row["label"].grid(row=0, column=0, sticky="ew", padx=(10, 4), pady=8)
        row["edit_btn"].configure(
            text="✏", fg_color="transparent", hover_color=DIVIDER, text_color=SUBTEXT,
        )
        row["editing"] = False

    def _clamp(self, idx: int):
        row = self._rows[idx]
        val = row["var"].get()
        if len(val) > MAX_CHARS:
            row["var"].set(val[:MAX_CHARS])

    # ── add / delete ──────────────────────────────────────────────────────────

    def _on_add(self):
        self._append_row("")
        self._sync_add_btn()
        self._start_edit(len(self._rows) - 1)

    def _delete_row(self, idx: int):
        row = self._rows[idx]
        if row["trace_id"]:
            row["var"].trace_remove("write", row["trace_id"])
        row["frame"].destroy()
        self._rows.pop(idx)
        for i in range(idx, len(self._rows)):
            self._rows[i]["edit_btn"].configure(command=lambda i=i: self._toggle_edit(i))
            self._rows[i]["del_btn"].configure(command=lambda i=i: self._delete_row(i))
        self._sync_add_btn()

    def _sync_add_btn(self):
        if len(self._rows) >= MAX_ROWS:
            self._add_btn.grid_remove()
        else:
            self._add_btn.grid()

    # ── confirm ───────────────────────────────────────────────────────────────

    def _on_confirm(self):
        for i, row in enumerate(self._rows):
            if row["editing"]:
                self._stop_edit(i)
        self.result = [r["var"].get().strip() for r in self._rows if r["var"].get().strip()]
        self.destroy()

    # ── positioning ───────────────────────────────────────────────────────────

    def _center_on(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        cw = self.winfo_width()
        ch = self.winfo_height()
        x  = px + (pw - cw) // 2
        y  = py + (ph - ch) // 2
        self.geometry(f"+{x}+{y}")
