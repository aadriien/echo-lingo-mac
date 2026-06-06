###############################################################################
##  `gui_app.py`                                                             ##
##                                                                           ##
##  Purpose: customtkinter GUI: pure rendering, zero pipeline logic          ##
##           All conversation state lives in ConversationController.         ##
###############################################################################


import customtkinter as ctk

from conversation.config import LANGUAGE_OPTIONS
from display.app_controller import ConversationController

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ── palette ───────────────────────────────────────────────────────────────────
BG          = "#FFF3E0"   # warm amber cream
HEADER_BG   = "#FFFFFF"   # white
DIVIDER     = "#FFE0B2"   # warm peach
USER_BUBBLE = "#FFB74D"   # bright amber/orange
ASST_BUBBLE = "#80DEEA"   # bright cyan
TEXT_FG     = "#1A1A1A"   # near-black
SUBTEXT     = "#8D6E63"   # warm brown
MIC_IDLE    = "#58CC02"   # Duolingo green
MIC_REC     = "#FF4B4B"   # bright red
MIC_DIS     = "#D7CCC8"   # warm gray
TITLE_FG    = "#FF6D00"   # deep orange

W, H     = 860, 580
MAX_BW   = 360    # max bubble width
PAD_X    = 16     # horizontal padding inside bubble
PAD_Y    = 12     # vertical padding inside bubble
MARGIN   = 20     # gap from window edge
RADIUS   = 20     # corner radius
ROW_GAP  = 8      # vertical gap between bubbles


# ── app ───────────────────────────────────────────────────────────────────────

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Echo Lingo")
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self._streaming_label = None
        self._streaming_text  = ""

        self._controller = ConversationController(
            on_status                 = lambda t: self.after(0, lambda: self._set_status(t)),
            on_user_bubble            = lambda t: self.after(0, lambda: self._add_bubble(t, is_user=True)),
            on_assistant_stream_start = lambda: self.after(0, self._start_streaming_bubble),
            on_assistant_chunk        = lambda t: self.after(0, lambda: self._append_chunk(t)),
            on_mic_reset              = lambda: self.after(0, self._reset_mic),
            on_mic_disabled           = lambda: self.after(0, self._disable_mic),
        )

        self._build_ui()
        self._add_bubble("Hola! Tap 🎙 to start speaking.", is_user=False)

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self._make_header()
        self._make_chat_area()
        self._make_bottom_bar()

    def _make_header(self):
        header = ctk.CTkFrame(self, height=68, fg_color=HEADER_BG, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        ctk.CTkFrame(header, height=2, fg_color=DIVIDER, corner_radius=0).place(
            x=0, rely=1.0, anchor="sw", relwidth=1.0
        )
        ctk.CTkLabel(
            header,
            text="🦜 Echo Lingo",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TITLE_FG,
        ).place(relx=0.5, rely=0.5, anchor="center")

        self._lang_menu = ctk.CTkOptionMenu(
            header,
            values=list(LANGUAGE_OPTIONS.keys()),
            command=self._on_language_changed,
            width=130,
            height=28,
        )
        self._lang_menu.set(self._controller.language)
        self._lang_menu.place(x=W - 148, rely=0.5, anchor="w")

    def _make_chat_area(self):
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self._scroll.grid(row=1, column=0, sticky="nsew")

    def _make_bottom_bar(self):
        bar = ctk.CTkFrame(self, height=120, fg_color=HEADER_BG, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)

        ctk.CTkFrame(bar, height=2, fg_color=DIVIDER, corner_radius=0).place(
            x=0, y=0, relwidth=1.0
        )
        self._status_label = ctk.CTkLabel(
            bar,
            text="Tap to speak",
            font=ctk.CTkFont(size=13),
            text_color=SUBTEXT,
        )
        self._status_label.place(relx=0.5, y=20, anchor="n")

        self._mic_btn = ctk.CTkButton(
            bar,
            text="🎙",
            font=ctk.CTkFont(size=30),
            width=72,
            height=72,
            corner_radius=36,
            fg_color=MIC_IDLE,
            hover_color="#4CAF00",
            text_color="#FFFFFF",
            command=self._on_mic_clicked,
        )
        self._mic_btn.place(relx=0.5, y=108, anchor="s")

    # ── event handlers ────────────────────────────────────────────────────────

    def _on_language_changed(self, lang: str):
        self._controller.set_language(lang)

    def _on_mic_clicked(self):
        if not self._controller.recording:
            self._controller.start_recording()
            self._mic_btn.configure(fg_color=MIC_REC, hover_color="#CC3C3C")
            self._status_label.configure(text="Listening…")
        else:
            self._controller.stop_recording()

    # ── mic state ─────────────────────────────────────────────────────────────

    def _disable_mic(self):
        self._mic_btn.configure(state="disabled", fg_color=MIC_DIS, hover_color=MIC_DIS)

    def _reset_mic(self):
        self._mic_btn.configure(state="normal", fg_color=MIC_IDLE, hover_color="#4CAF00")

    # ── status ────────────────────────────────────────────────────────────────

    def _set_status(self, text: str):
        self._status_label.configure(text=text)

    # ── bubbles ───────────────────────────────────────────────────────────────

    def _add_bubble(self, text: str, *, is_user: bool):
        row = ctk.CTkFrame(self._scroll, fg_color=BG, corner_radius=0)
        row.pack(fill="x", padx=MARGIN, pady=(ROW_GAP, 0))

        bubble = ctk.CTkFrame(
            row,
            fg_color=USER_BUBBLE if is_user else ASST_BUBBLE,
            corner_radius=RADIUS,
        )
        bubble.pack(anchor="e" if is_user else "w")

        ctk.CTkLabel(
            bubble,
            text=text,
            font=ctk.CTkFont(size=16),
            text_color=TEXT_FG,
            wraplength=MAX_BW - PAD_X * 2,
            justify="left",
        ).pack(padx=PAD_X, pady=PAD_Y)

        self._scroll_to_bottom()

    def _start_streaming_bubble(self):
        self._streaming_text  = ""

        row = ctk.CTkFrame(self._scroll, fg_color=BG, corner_radius=0)
        row.pack(fill="x", padx=MARGIN, pady=(ROW_GAP, 0))

        bubble = ctk.CTkFrame(row, fg_color=ASST_BUBBLE, corner_radius=RADIUS)
        bubble.pack(anchor="w")

        self._streaming_label = ctk.CTkLabel(
            bubble,
            text="",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_FG,
            wraplength=MAX_BW - PAD_X * 2,
            justify="left",
        )
        self._streaming_label.pack(padx=PAD_X, pady=PAD_Y)

        self._scroll_to_bottom()

    def _append_chunk(self, chunk: str):
        if self._streaming_label is None:
            return
        self._streaming_text += chunk
        self._streaming_label.configure(text=self._streaming_text)
        self._scroll_to_bottom()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _scroll_to_bottom(self):
        self._scroll._parent_canvas.yview_moveto(1.0)


# ── entry point ───────────────────────────────────────────────────────────────

def run():
    app = App()
    app.mainloop()
