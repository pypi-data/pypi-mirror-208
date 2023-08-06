import enum

from chateval.utils.logging import get_logger

logger = get_logger(__name__)


class DownloadMode(enum.Enum):

    REUSE_DATASET_IF_EXISTS = "reuse_dataset_if_exists"
    REUSE_CACHE_IF_EXISTS = "reuse_cache_if_exists"
    FORCE_REDOWNLOAD = "force_redownload"
