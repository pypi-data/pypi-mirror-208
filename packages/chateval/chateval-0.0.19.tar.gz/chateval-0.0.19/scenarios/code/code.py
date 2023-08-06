from __future__ import annotations

from chateval.chateval import ChatEval


class CodeEval(ChatEval):
    def _config_name(self):
        return "code"
