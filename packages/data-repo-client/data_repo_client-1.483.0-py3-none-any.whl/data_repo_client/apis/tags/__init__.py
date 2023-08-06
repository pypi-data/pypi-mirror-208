# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from data_repo_client.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    DATA_REPOSITORY_SERVICE = "DataRepositoryService"
    CONFIGS = "configs"
    REPOSITORY = "repository"
    DATASETS = "datasets"
    SEARCH = "search"
    DUOS = "duos"
    JOBS = "jobs"
    JOURNAL = "journal"
    PROFILES = "profiles"
    RESOURCES = "resources"
    REGISTER = "register"
    SNAPSHOTS = "snapshots"
    UPGRADE = "upgrade"
    UNAUTHENTICATED = "unauthenticated"
