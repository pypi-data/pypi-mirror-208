from __future__ import annotations

from chateval.chateval import ChatEval


class OpendomainCommonsenseEval(ChatEval):
    def _config_name(self):
        return "opendomain_commonsense"
