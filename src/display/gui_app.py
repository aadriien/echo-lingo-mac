###############################################################################
##  `gui_app.py`                                                             ##
##                                                                           ##
##  Purpose: PySide6 GUI — chat interface for the conversation pipeline      ##
###############################################################################


# TODO: implement using PySide6
#
# Target feel: clean, dark, minimal — intuitive enough to just open and talk
#
# Components:
#   - Header: app title + language selector (dropdown or segmented control)
#   - Chat area: scrollable message bubbles (user right, assistant left)
#   - Mic button: single click to start / stop recording
#   - Status bar: pipeline state (listening / thinking / speaking / ready)
#
# Threading:
#   - STT, LLM, TTS all run in QThread workers off the main thread
#   - Emit Qt signals to push transcript + response text back to UI
#   - Never call UI methods directly from worker threads
#
# Bundling (when ready):
#   - Package as .app with py2app or PyInstaller
#   - Add custom icon via .icns for dock presence
