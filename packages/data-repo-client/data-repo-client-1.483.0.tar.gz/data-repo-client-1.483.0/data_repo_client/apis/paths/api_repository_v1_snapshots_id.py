from data_repo_client.paths.api_repository_v1_snapshots_id.get import ApiForget
from data_repo_client.paths.api_repository_v1_snapshots_id.delete import ApiFordelete
from data_repo_client.paths.api_repository_v1_snapshots_id.patch import ApiForpatch


class ApiRepositoryV1SnapshotsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
