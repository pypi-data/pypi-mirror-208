from data_repo_client.paths.api_repository_v1_datasets_id.get import ApiForget
from data_repo_client.paths.api_repository_v1_datasets_id.delete import ApiFordelete
from data_repo_client.paths.api_repository_v1_datasets_id.patch import ApiForpatch


class ApiRepositoryV1DatasetsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
