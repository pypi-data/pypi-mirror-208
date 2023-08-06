from __future__ import annotations

from chateval.chateval import ChatEval


class InformationExtractionEval(ChatEval):
    def _config_name(self):
        return "information_extraction"
