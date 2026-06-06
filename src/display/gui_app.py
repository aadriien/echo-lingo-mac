###############################################################################
##  `gui_app.py`                                                             ##
##                                                                           ##
##  Purpose: customtkinter GUI: pure rendering, zero pipeline logic          ##
##           All conversation state lives in ConversationController.         ##
###############################################################################


import customtkinter as ctk

from conversation.config import LANGUAGE_OPTIONS
from display.app_controller import ConversationController
from display.summary_card import SummaryCard
from conversation.text.config import GREETINGS
from topics.config import TOPICS, topic_name, topic_hint

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
MIC_IDLE    = "#58CC02"   # bright green
MIC_REC     = "#FF4B4B"   # bright red
MIC_DIS     = "#D7CCC8"   # warm gray
TITLE_FG    = "#FF6D00"   # deep orange
SIDEBAR_BG  = "#FFFFFF"   # sidebar white
TOPIC_SEL   = "#FFB74D"   # selected topic block (amber)
TOPIC_NOR   = "#FFF8F0"   # unselected topic block

W, H        = 860, 580
MAX_BW      = 360    # max bubble width
PAD_X       = 16     # horizontal padding inside bubble
PAD_Y       = 12     # vertical padding inside bubble
MARGIN      = 20     # gap from window edge
RADIUS      = 20     # corner radius
ROW_GAP     = 8      # vertical gap between bubbles
SIDEBAR_W   = 178    # sidebar width when open


# ── app ───────────────────────────────────────────────────────────────────────

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Echo Lingo")
        self.geometry(f"{W}x{H}")
        self.minsize(600, 400)
        self.configure(fg_color=BG)

        self._streaming_label = None
        self._streaming_text  = ""
        self._sidebar_open    = True

        self._controller = ConversationController(
            on_status                 = lambda t: self.after(0, lambda: self._set_status(t)),
            on_user_bubble            = lambda t: self.after(0, lambda: self._add_bubble(t, is_user=True)),
            on_assistant_stream_start = lambda: self.after(0, self._start_streaming_bubble),
            on_assistant_chunk        = lambda t: self.after(0, lambda: self._append_chunk(t)),
            on_mic_reset              = lambda: self.after(0, self._reset_mic),
            on_mic_disabled           = lambda: self.after(0, self._disable_mic),
        )

        self._build_ui()
        self._add_bubble(GREETINGS.get(self._controller.language, GREETINGS["English"]), is_user=False)

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # main content
        self._make_sidebar()
        self._make_main()
        self.bind("<Configure>", self._on_window_resize)

    def _make_sidebar(self):
        self._sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_W, fg_color=SIDEBAR_BG, corner_radius=0
        )
        self._sidebar.grid(row=0, column=0, sticky="ns")
        self._sidebar.grid_propagate(False)

        # right border
        ctk.CTkFrame(self._sidebar, width=2, fg_color=DIVIDER, corner_radius=0).place(
            relx=1.0, x=-2, rely=0, relheight=1.0, anchor="nw"
        )

        self._topic_btns   = {}
        self._active_topic = None  # None = Freeform selected

        lang = self._controller.language
        for i, topic in enumerate(TOPICS):
            is_freeform = topic_hint(topic, lang) is None
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"{topic['emoji']}  {topic_name(topic, lang)}",
                font=ctk.CTkFont(size=13),
                fg_color=TOPIC_SEL if is_freeform else TOPIC_NOR,
                hover_color=DIVIDER,
                text_color=TEXT_FG,
                corner_radius=10,
                anchor="w",
                height=38,
                command=lambda t=topic: self._on_topic_clicked(t),
            )
            btn.pack(fill="x", padx=10, pady=(12 if i == 0 else 4, 0))
            self._topic_btns[topic["names"]["English"]] = btn

            # separator after freeform row
            if is_freeform:
                ctk.CTkFrame(
                    self._sidebar, height=1, fg_color=DIVIDER, corner_radius=0
                ).pack(fill="x", padx=10, pady=(8, 0))

    def _make_main(self):
        self._main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self._main.grid(row=0, column=1, sticky="nsew")
        self._main.grid_rowconfigure(0, weight=0)
        self._main.grid_rowconfigure(1, weight=1)
        self._main.grid_rowconfigure(2, weight=0)
        self._main.grid_columnconfigure(0, weight=1)
        self._make_header()
        self._make_chat_area()
        self._make_bottom_bar()

    def _make_header(self):
        header = ctk.CTkFrame(self._main, height=68, fg_color=HEADER_BG, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        ctk.CTkFrame(header, height=2, fg_color=DIVIDER, corner_radius=0).place(
            x=0, rely=1.0, anchor="sw", relwidth=1.0
        )

        # sidebar toggle (far left)
        self._toggle_btn = ctk.CTkButton(
            header,
            text="◀",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=DIVIDER,
            text_color=SUBTEXT,
            corner_radius=8,
            command=self._toggle_sidebar,
        )
        self._toggle_btn.place(x=12, rely=0.5, anchor="w")

        # active topic indicator (beside toggle)
        self._topic_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TITLE_FG,
        )
        self._topic_label.place(x=50, rely=0.5, anchor="w")

        # centered title
        ctk.CTkLabel(
            header,
            text="🦜 Echo Lingo",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TITLE_FG,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # language menu (far right)
        self._lang_menu = ctk.CTkOptionMenu(
            header,
            values=list(LANGUAGE_OPTIONS.keys()),
            command=self._on_language_changed,
            width=130,
            height=28,
        )
        self._lang_menu.set(self._controller.language)
        self._lang_menu.place(relx=1.0, x=-18, rely=0.5, anchor="e")

    def _make_chat_area(self):
        self._scroll = ctk.CTkScrollableFrame(self._main, fg_color=BG, corner_radius=0)
        self._scroll.grid(row=1, column=0, sticky="nsew")

    def _make_bottom_bar(self):
        bar = ctk.CTkFrame(self._main, height=120, fg_color=HEADER_BG, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)

        ctk.CTkFrame(bar, height=2, fg_color=DIVIDER, corner_radius=0).pack(fill="x")

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
        self._mic_btn.pack(side="bottom", pady=(0, 10))

        self._status_label = ctk.CTkLabel(
            bar,
            text="Tap to speak",
            font=ctk.CTkFont(size=13),
            text_color=SUBTEXT,
        )
        self._status_label.pack(expand=True)

    # ── sidebar ───────────────────────────────────────────────────────────────

    def _toggle_sidebar(self):
        if self._sidebar_open:
            self._sidebar.grid_remove()
            self._toggle_btn.configure(text="▶")
        else:
            self._sidebar.grid()
            self._toggle_btn.configure(text="◀")
        self._sidebar_open = not self._sidebar_open

    def _on_topic_clicked(self, topic: dict):
        lang      = self._controller.language
        new_topic = topic if topic_hint(topic, lang) else None
        eng_name  = topic["names"]["English"]

        for name, btn in self._topic_btns.items():
            btn.configure(fg_color=TOPIC_SEL if name == eng_name else TOPIC_NOR)
        self._topic_label.configure(
            text=f"{topic['emoji']} {topic_name(topic, lang)}" if new_topic else ""
        )

        self._save_current_topic()
        self._controller.set_topic(new_topic)
        self._active_topic = new_topic

    # ── event handlers ────────────────────────────────────────────────────────

    def _on_language_changed(self, lang: str):
        self._save_current_topic()
        self._controller.set_language(lang)
        self._refresh_topic_labels(lang)
        self._reset_chat(lang)

    def _refresh_topic_labels(self, language: str):
        for topic in TOPICS:
            btn = self._topic_btns.get(topic["names"]["English"])
            if btn:
                btn.configure(text=f"{topic['emoji']}  {topic_name(topic, language)}")
        if self._active_topic:
            self._topic_label.configure(
                text=f"{self._active_topic['emoji']} {topic_name(self._active_topic, language)}"
            )

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

    def _on_window_resize(self, event):
        if event.widget is not self:
            return
        # Proportionally scale topic button heights and font to fill the sidebar.
        # overhead = first-button top pad + separator + inter-button gaps
        n = len(TOPICS)
        overhead = 12 + 9 + 4 * (n - 1)
        btn_h = max(28, (event.height - overhead) // n)
        font_size = max(11, min(18, round(btn_h * 0.34)))
        for btn in self._topic_btns.values():
            btn.configure(height=btn_h, font=ctk.CTkFont(size=font_size))

    def _save_current_topic(self):
        """Summarize → show review card → save. No-ops if no topic or too little history."""
        if not self._controller.has_saveable_history:
            return
        self._set_saving(True)
        self.update_idletasks()
        try:
            bullets = self._controller.get_summary()
            if bullets:
                self._status_label.configure(text="Review your notes")
                self.update_idletasks()  # repaint before blocking.. safer than update()
                card = SummaryCard(self, bullets)
                if card.result:
                    self._controller.save_summary(card.result)
        except RuntimeError as e:
            self._status_label.configure(text=str(e))
        finally:
            self._set_saving(False)

    def _set_saving(self, saving: bool):
        state = "disabled" if saving else "normal"
        self._mic_btn.configure(state=state)
        self._toggle_btn.configure(state=state)
        self._lang_menu.configure(state=state)
        for btn in self._topic_btns.values():
            btn.configure(state=state)
        if saving:
            self._status_label.configure(text="💾 Saving notes…")
        else:
            self._status_label.configure(text="Tap to speak")

    def _reset_chat(self, lang: str):
        for widget in self._scroll.winfo_children():
            widget.destroy()
        self._streaming_label = None
        self._streaming_text  = ""
        self._add_bubble(GREETINGS.get(lang, GREETINGS["English"]), is_user=False)

    def _scroll_to_bottom(self):
        self._scroll._parent_canvas.yview_moveto(1.0)


# ── entry point ───────────────────────────────────────────────────────────────

def run():
    app = App()
    app.mainloop()
