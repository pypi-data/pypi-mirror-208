from __future__ import annotations

from chateval.chateval import ChatEval


class BrainstormingEval(ChatEval):
    def _config_name(self):
        return "brainstorming"
