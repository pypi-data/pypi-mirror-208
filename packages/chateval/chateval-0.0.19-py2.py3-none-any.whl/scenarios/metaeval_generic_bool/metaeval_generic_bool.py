from __future__ import annotations

from chateval.chateval import ChatEval


class MetaEvalHelpfulnessEval(ChatEval):
    def _config_name(self):
        return "metaeval_generic_bool"
