###############################################################################
##  `gui_app.py`                                                             ##
##                                                                           ##
##  Purpose: AppKit (PyObjC) GUI: pure rendering, zero pipeline logic        ##
##           All conversation state lives in ConversationController.         ##
###############################################################################


import math
import objc

from AppKit import (
    NSApplication, NSWindow, NSView, NSButton, NSScrollView,
    NSTextField, NSPopUpButton, NSBezierPath, NSColor, NSFont,
    NSMakeRect, NSBackingStoreBuffered,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable,
    NSAttributedString,
    NSFontAttributeName, NSTextAlignmentCenter,
)
from Foundation import NSObject, NSMakePoint, NSMakeSize

from conversation.config import LANGUAGE_OPTIONS
from display.app_controller import ConversationController


# ── palette ───────────────────────────────────────────────────────────────────
def _rgb(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 1.0)

BG          = _rgb("141416")
HEADER_BG   = _rgb("1E1E22")
DIVIDER     = _rgb("2C2C30")
USER_BUBBLE = _rgb("0A84FF")
ASST_BUBBLE = _rgb("2C2C30")
WHITE       = NSColor.whiteColor()
SUBTEXT     = _rgb("8E8E93")
MIC_IDLE    = _rgb("0A84FF")
MIC_REC     = _rgb("FF3B30")
MIC_DIS     = _rgb("3A3A3C")

TITLE_FONT = NSFont.boldSystemFontOfSize_(16)
BODY_FONT  = NSFont.systemFontOfSize_(15)
SMALL_FONT = NSFont.systemFontOfSize_(12)

W, H      = 390, 720
HEADER_H  = 60
BOTTOM_H  = 120
CHAT_H    = H - HEADER_H - BOTTOM_H    # 540

MAX_BW    = 262     # max bubble width (incl. padding)
PAD_H     = 14     # horizontal padding inside bubble
PAD_V     = 10     # vertical padding inside bubble
MARGIN    = 14     # gap from window edge
RADIUS    = 18.0
ROW_GAP   = 7      # vertical gap between bubbles


# ── views ─────────────────────────────────────────────────────────────────────

class FlippedView(NSView):
    """Document view with top-left origin so bubbles stack downward."""
    def isFlipped(self):
        return True


class BubbleView(NSView):
    _color = objc.ivar()

    def drawRect_(self, rect):
        if self._color is None:
            return
        path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
            self.bounds(), RADIUS, RADIUS
        )
        self._color.set()
        path.fill()


# ── app delegate ──────────────────────────────────────────────────────────────
class AppDelegate(NSObject):

    def init(self):
        self = objc.super(AppDelegate, self).init()
        if self is None:
            return None
        self._y_cursor = ROW_GAP
        self._controller = ConversationController(
            on_status           = lambda t: self._ui(lambda: self._set_status(t)),
            on_user_bubble      = lambda t: self._ui(lambda: self._add_bubble(t, is_user=True)),
            on_assistant_bubble = lambda t: self._ui(lambda: self._add_bubble(t, is_user=False)),
            on_mic_reset        = lambda: self._ui(self._reset_mic),
            on_mic_disabled     = lambda: self._ui(self._disable_mic),
        )
        return self

    def applicationDidFinishLaunching_(self, _notif):
        self._build_window()
        self._add_bubble("Hola! Tap 🎙 to start speaking.", is_user=False)

    # ── window ────────────────────────────────────────────────────────────────

    @objc.python_method
    def _build_window(self):
        style = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                 NSWindowStyleMaskMiniaturizable)
        self._win = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(300, 200, W, H), style, NSBackingStoreBuffered, False,
        )
        self._win.setTitle_("Echo Lingo")
        self._win.setBackgroundColor_(BG)

        c = self._win.contentView()
        c.addSubview_(self._make_header())
        c.addSubview_(self._make_chat_area())
        c.addSubview_(self._make_bottom_bar())

        self._win.makeKeyAndOrderFront_(None)

    # ── header ────────────────────────────────────────────────────────────────

    @objc.python_method
    def _make_header(self):
        header = NSView.alloc().initWithFrame_(NSMakeRect(0, H - HEADER_H, W, HEADER_H))
        header.setWantsLayer_(True)
        header.layer().setBackgroundColor_(HEADER_BG.CGColor())

        div = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, W, 1))
        div.setWantsLayer_(True)
        div.layer().setBackgroundColor_(DIVIDER.CGColor())
        header.addSubview_(div)

        title = NSTextField.alloc().initWithFrame_(NSMakeRect(80, 18, W - 160, 24))
        title.setStringValue_("Echo Lingo")
        title.setFont_(TITLE_FONT)
        title.setTextColor_(WHITE)
        title.setAlignment_(NSTextAlignmentCenter)
        title.setBezeled_(False)
        title.setDrawsBackground_(False)
        title.setEditable_(False)
        title.setSelectable_(False)
        header.addSubview_(title)

        popup = NSPopUpButton.alloc().initWithFrame_(
            NSMakeRect(W - 116, 16, 104, 28)
        )
        for lang in LANGUAGE_OPTIONS:
            popup.addItemWithTitle_(lang)
        popup.selectItemWithTitle_(self._controller.language)
        popup.setFont_(NSFont.systemFontOfSize_(13))
        popup.setTarget_(self)
        popup.setAction_(objc.selector(self.languageChanged_, signature=b"v@:@"))
        header.addSubview_(popup)

        return header

    # ── chat area ─────────────────────────────────────────────────────────────

    @objc.python_method
    def _make_chat_area(self):
        self._scroll = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(0, BOTTOM_H, W, CHAT_H)
        )
        self._scroll.setHasVerticalScroller_(True)
        self._scroll.setDrawsBackground_(False)
        self._scroll.verticalScroller().setAlphaValue_(0.25)

        self._doc_view = FlippedView.alloc().initWithFrame_(
            NSMakeRect(0, 0, W, CHAT_H)
        )
        self._scroll.setDocumentView_(self._doc_view)
        return self._scroll

    # ── bottom bar ────────────────────────────────────────────────────────────

    @objc.python_method
    def _make_bottom_bar(self):
        bar = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, W, BOTTOM_H))
        bar.setWantsLayer_(True)
        bar.layer().setBackgroundColor_(HEADER_BG.CGColor())

        div = NSView.alloc().initWithFrame_(NSMakeRect(0, BOTTOM_H - 1, W, 1))
        div.setWantsLayer_(True)
        div.layer().setBackgroundColor_(DIVIDER.CGColor())
        bar.addSubview_(div)

        self._status_tf = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 78, W, 18))
        self._status_tf.setStringValue_("Tap to speak")
        self._status_tf.setFont_(SMALL_FONT)
        self._status_tf.setTextColor_(SUBTEXT)
        self._status_tf.setAlignment_(NSTextAlignmentCenter)
        self._status_tf.setBezeled_(False)
        self._status_tf.setDrawsBackground_(False)
        self._status_tf.setEditable_(False)
        self._status_tf.setSelectable_(False)
        bar.addSubview_(self._status_tf)

        btn_size = 60
        self._mic_btn = NSButton.alloc().initWithFrame_(
            NSMakeRect((W - btn_size) // 2, 12, btn_size, btn_size)
        )
        self._mic_btn.setTitle_("🎙")
        self._mic_btn.setFont_(NSFont.systemFontOfSize_(24))
        self._mic_btn.setWantsLayer_(True)
        self._mic_btn.layer().setCornerRadius_(btn_size / 2)
        self._mic_btn.layer().setBackgroundColor_(MIC_IDLE.CGColor())
        self._mic_btn.setBordered_(False)
        self._mic_btn.setBezelStyle_(0)
        self._mic_btn.setTarget_(self)
        self._mic_btn.setAction_(objc.selector(self.micClicked_, signature=b"v@:@"))
        bar.addSubview_(self._mic_btn)

        return bar

    # ── event handlers ────────────────────────────────────────────────────────

    def languageChanged_(self, sender):
        self._controller.set_language(sender.titleOfSelectedItem())

    def micClicked_(self, _sender):
        if not self._controller.recording:
            self._controller.start_recording()
            self._mic_btn.layer().setBackgroundColor_(MIC_REC.CGColor())
            self._status_tf.setStringValue_("Listening…")
        else:
            self._controller.stop_recording()

    # ── mic visual state ──────────────────────────────────────────────────────

    @objc.python_method
    def _disable_mic(self):
        self._mic_btn.setEnabled_(False)
        self._mic_btn.layer().setBackgroundColor_(MIC_DIS.CGColor())

    @objc.python_method
    def _reset_mic(self):
        self._mic_btn.setEnabled_(True)
        self._mic_btn.layer().setBackgroundColor_(MIC_IDLE.CGColor())

    # ── status label ──────────────────────────────────────────────────────────

    @objc.python_method
    def _set_status(self, text: str):
        self._status_tf.setStringValue_(text)

    # ── main-thread dispatch ──────────────────────────────────────────────────

    @objc.python_method
    def _ui(self, fn):
        from Foundation import NSThread
        if NSThread.isMainThread():
            fn()
        else:
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                objc.selector(self.runBlock_, signature=b"v@:@"), fn, False,
            )

    def runBlock_(self, fn):
        fn()

    # ── chat bubbles ──────────────────────────────────────────────────────────

    @objc.python_method
    def _add_bubble(self, text: str, is_user: bool):
        inner_w = MAX_BW - PAD_H * 2

        attr = NSAttributedString.alloc().initWithString_attributes_(
            text, {NSFontAttributeName: BODY_FONT}
        )
        bound = attr.boundingRectWithSize_options_context_(
            NSMakeSize(inner_w, 10_000),
            1,      # NSStringDrawingUsesLineFragmentOrigin
            None,
        )
        text_h = math.ceil(bound.size.height) + 2
        text_w = min(math.ceil(bound.size.width), inner_w)

        bubble_w = text_w + PAD_H * 2
        bubble_h = text_h + PAD_V * 2
        bubble_x = (W - MARGIN - bubble_w) if is_user else MARGIN

        bubble = BubbleView.alloc().initWithFrame_(
            NSMakeRect(bubble_x, self._y_cursor, bubble_w, bubble_h)
        )
        bubble._color = USER_BUBBLE if is_user else ASST_BUBBLE

        # Text field — y from bottom of bubble in non-flipped bubble coords
        tf_y = bubble_h - PAD_V - text_h
        tf = NSTextField.alloc().initWithFrame_(
            NSMakeRect(PAD_H, tf_y, text_w, text_h)
        )
        tf.setStringValue_(text)
        tf.setFont_(BODY_FONT)
        tf.setTextColor_(WHITE)
        tf.setBezeled_(False)
        tf.setDrawsBackground_(False)
        tf.setEditable_(False)
        tf.setSelectable_(True)
        tf.setWraps_(True)
        bubble.addSubview_(tf)

        self._doc_view.addSubview_(bubble)
        self._y_cursor += bubble_h + ROW_GAP

        # Grow document view if content exceeds current height
        if self._y_cursor + ROW_GAP > self._doc_view.frame().size.height:
            self._doc_view.setFrame_(
                NSMakeRect(0, 0, W, self._y_cursor + ROW_GAP)
            )

        # Scroll to show latest bubble
        scroll_y = max(0.0, self._y_cursor - CHAT_H + ROW_GAP)
        self._doc_view.scrollPoint_(NSMakePoint(0.0, scroll_y))


# ── entry point ───────────────────────────────────────────────────────────────

def run():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(0)
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.activateIgnoringOtherApps_(True)
    app.run()