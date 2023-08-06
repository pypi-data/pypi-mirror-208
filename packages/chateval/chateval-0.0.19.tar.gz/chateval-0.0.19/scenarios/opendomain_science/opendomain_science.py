from __future__ import annotations

from chateval.chateval import ChatEval


class OpendomainScienceEval(ChatEval):
    def _config_name(self):
        return "opendomain_science"
