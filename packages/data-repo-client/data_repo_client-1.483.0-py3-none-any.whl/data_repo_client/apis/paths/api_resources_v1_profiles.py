from data_repo_client.paths.api_resources_v1_profiles.get import ApiForget
from data_repo_client.paths.api_resources_v1_profiles.put import ApiForput
from data_repo_client.paths.api_resources_v1_profiles.post import ApiForpost


class ApiResourcesV1Profiles(
    ApiForget,
    ApiForput,
    ApiForpost,
):
    pass
