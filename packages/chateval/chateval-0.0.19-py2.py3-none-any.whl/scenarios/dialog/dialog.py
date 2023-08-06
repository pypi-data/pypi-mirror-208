from __future__ import annotations

from chateval.chateval import ChatEval


class DialogEval(ChatEval):
    def _config_name(self):
        return "dialog"
