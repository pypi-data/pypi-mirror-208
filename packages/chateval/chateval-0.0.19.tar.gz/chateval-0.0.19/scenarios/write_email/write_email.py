from __future__ import annotations

from chateval.chateval import ChatEval


class WriteEmailEval(ChatEval):
    def _config_name(self):
        return "write_email"
