from __future__ import annotations

from chateval.chateval import ChatEval


class JudgementEval(ChatEval):
    def _config_name(self):
        return "judgement"
