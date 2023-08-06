import typing_extensions

from data_repo_client.paths import PathValues
from data_repo_client.apis.paths.status import Status
from data_repo_client.apis.paths.configuration import Configuration
from data_repo_client.apis.paths.shutdown import Shutdown
from data_repo_client.apis.paths.api_resources_v1_profiles import ApiResourcesV1Profiles
from data_repo_client.apis.paths.api_resources_v1_profiles_id import ApiResourcesV1ProfilesId
from data_repo_client.apis.paths.api_resources_v1_profiles_id_policies import ApiResourcesV1ProfilesIdPolicies
from data_repo_client.apis.paths.api_resources_v1_profiles_id_policies_policy_name_members import ApiResourcesV1ProfilesIdPoliciesPolicyNameMembers
from data_repo_client.apis.paths.api_resources_v1_profiles_id_policies_policy_name_members_member_email import ApiResourcesV1ProfilesIdPoliciesPolicyNameMembersMemberEmail
from data_repo_client.apis.paths.api_repository_v1_snapshots import ApiRepositoryV1Snapshots
from data_repo_client.apis.paths.api_repository_v1_snapshots_role_map import ApiRepositoryV1SnapshotsRoleMap
from data_repo_client.apis.paths.api_repository_v1_snapshots_tags import ApiRepositoryV1SnapshotsTags
from data_repo_client.apis.paths.api_repository_v1_snapshots_id import ApiRepositoryV1SnapshotsId
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_summary import ApiRepositoryV1SnapshotsIdSummary
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_data_table import ApiRepositoryV1SnapshotsIdDataTable
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_export import ApiRepositoryV1SnapshotsIdExport
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_files_fileid import ApiRepositoryV1SnapshotsIdFilesFileid
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_filesystem_objects import ApiRepositoryV1SnapshotsIdFilesystemObjects
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_policies import ApiRepositoryV1SnapshotsIdPolicies
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_policies_policy_name_members import ApiRepositoryV1SnapshotsIdPoliciesPolicyNameMembers
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_policies_policy_name_members_member_email import ApiRepositoryV1SnapshotsIdPoliciesPolicyNameMembersMemberEmail
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_roles import ApiRepositoryV1SnapshotsIdRoles
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_link_duos_dataset_duos_id import ApiRepositoryV1SnapshotsIdLinkDuosDatasetDuosId
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_unlink_duos_dataset import ApiRepositoryV1SnapshotsIdUnlinkDuosDataset
from data_repo_client.apis.paths.api_repository_v1_snapshots_id_tags import ApiRepositoryV1SnapshotsIdTags
from data_repo_client.apis.paths.api_repository_v1_duos import ApiRepositoryV1Duos
from data_repo_client.apis.paths.api_repository_v1_duos_duos_id import ApiRepositoryV1DuosDuosId
from data_repo_client.apis.paths.api_repository_v1_duos_sync_authorized_users import ApiRepositoryV1DuosSyncAuthorizedUsers
from data_repo_client.apis.paths.api_repository_v1_duos_duos_id_sync_authorized_users import ApiRepositoryV1DuosDuosIdSyncAuthorizedUsers
from data_repo_client.apis.paths.api_repository_v1_datasets import ApiRepositoryV1Datasets
from data_repo_client.apis.paths.api_repository_v1_datasets_tags import ApiRepositoryV1DatasetsTags
from data_repo_client.apis.paths.api_repository_v1_datasets_id import ApiRepositoryV1DatasetsId
from data_repo_client.apis.paths.api_repository_v1_datasets_id_data_table import ApiRepositoryV1DatasetsIdDataTable
from data_repo_client.apis.paths.api_repository_v1_datasets_id_summary import ApiRepositoryV1DatasetsIdSummary
from data_repo_client.apis.paths.api_repository_v1_datasets_id_policies import ApiRepositoryV1DatasetsIdPolicies
from data_repo_client.apis.paths.api_repository_v1_datasets_id_policies_policy_name_members import ApiRepositoryV1DatasetsIdPoliciesPolicyNameMembers
from data_repo_client.apis.paths.api_repository_v1_datasets_id_policies_policy_name_members_member_email import ApiRepositoryV1DatasetsIdPoliciesPolicyNameMembersMemberEmail
from data_repo_client.apis.paths.api_repository_v1_datasets_id_roles import ApiRepositoryV1DatasetsIdRoles
from data_repo_client.apis.paths.api_repository_v1_datasets_id_ingest import ApiRepositoryV1DatasetsIdIngest
from data_repo_client.apis.paths.api_repository_v1_datasets_id_update_schema import ApiRepositoryV1DatasetsIdUpdateSchema
from data_repo_client.apis.paths.api_repository_v1_datasets_id_transactions import ApiRepositoryV1DatasetsIdTransactions
from data_repo_client.apis.paths.api_repository_v1_datasets_id_transactions_transaction_id import ApiRepositoryV1DatasetsIdTransactionsTransactionId
from data_repo_client.apis.paths.api_repository_v1_datasets_id_assets import ApiRepositoryV1DatasetsIdAssets
from data_repo_client.apis.paths.api_repository_v1_datasets_id_assets_assetid import ApiRepositoryV1DatasetsIdAssetsAssetid
from data_repo_client.apis.paths.api_repository_v1_datasets_id_deletes import ApiRepositoryV1DatasetsIdDeletes
from data_repo_client.apis.paths.api_repository_v1_datasets_id_tags import ApiRepositoryV1DatasetsIdTags
from data_repo_client.apis.paths.api_repository_v1_register_user import ApiRepositoryV1RegisterUser
from data_repo_client.apis.paths.api_repository_v1_datasets_id_files import ApiRepositoryV1DatasetsIdFiles
from data_repo_client.apis.paths.api_repository_v1_datasets_id_files_bulk import ApiRepositoryV1DatasetsIdFilesBulk
from data_repo_client.apis.paths.api_repository_v1_datasets_id_files_bulk_load_tag import ApiRepositoryV1DatasetsIdFilesBulkLoadTag
from data_repo_client.apis.paths.api_repository_v1_datasets_id_files_bulk_array import ApiRepositoryV1DatasetsIdFilesBulkArray
from data_repo_client.apis.paths.api_repository_v1_datasets_id_files_fileid import ApiRepositoryV1DatasetsIdFilesFileid
from data_repo_client.apis.paths.api_repository_v1_datasets_id_filesystem_objects import ApiRepositoryV1DatasetsIdFilesystemObjects
from data_repo_client.apis.paths.api_repository_v1_jobs import ApiRepositoryV1Jobs
from data_repo_client.apis.paths.api_repository_v1_jobs_id import ApiRepositoryV1JobsId
from data_repo_client.apis.paths.api_repository_v1_jobs_id_result import ApiRepositoryV1JobsIdResult
from data_repo_client.apis.paths.api_repository_v1_configs_name import ApiRepositoryV1ConfigsName
from data_repo_client.apis.paths.api_repository_v1_configs import ApiRepositoryV1Configs
from data_repo_client.apis.paths.api_repository_v1_configs_reset import ApiRepositoryV1ConfigsReset
from data_repo_client.apis.paths.api_repository_v1_upgrade import ApiRepositoryV1Upgrade
from data_repo_client.apis.paths.api_repository_v1_search_id_index import ApiRepositoryV1SearchIdIndex
from data_repo_client.apis.paths.api_repository_v1_search_query import ApiRepositoryV1SearchQuery
from data_repo_client.apis.paths.ga4gh_drs_v1_service_info import Ga4ghDrsV1ServiceInfo
from data_repo_client.apis.paths.ga4gh_drs_v1_objects_object_id import Ga4ghDrsV1ObjectsObjectId
from data_repo_client.apis.paths.ga4gh_drs_v1_objects_object_id_access_access_id import Ga4ghDrsV1ObjectsObjectIdAccessAccessId
from data_repo_client.apis.paths.api_repository_v1_journal_resource_key import ApiRepositoryV1JournalResourceKey

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.STATUS: Status,
        PathValues.CONFIGURATION: Configuration,
        PathValues.SHUTDOWN: Shutdown,
        PathValues.API_RESOURCES_V1_PROFILES: ApiResourcesV1Profiles,
        PathValues.API_RESOURCES_V1_PROFILES_ID: ApiResourcesV1ProfilesId,
        PathValues.API_RESOURCES_V1_PROFILES_ID_POLICIES: ApiResourcesV1ProfilesIdPolicies,
        PathValues.API_RESOURCES_V1_PROFILES_ID_POLICIES_POLICY_NAME_MEMBERS: ApiResourcesV1ProfilesIdPoliciesPolicyNameMembers,
        PathValues.API_RESOURCES_V1_PROFILES_ID_POLICIES_POLICY_NAME_MEMBERS_MEMBER_EMAIL: ApiResourcesV1ProfilesIdPoliciesPolicyNameMembersMemberEmail,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS: ApiRepositoryV1Snapshots,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ROLE_MAP: ApiRepositoryV1SnapshotsRoleMap,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_TAGS: ApiRepositoryV1SnapshotsTags,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID: ApiRepositoryV1SnapshotsId,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_SUMMARY: ApiRepositoryV1SnapshotsIdSummary,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_DATA_TABLE: ApiRepositoryV1SnapshotsIdDataTable,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_EXPORT: ApiRepositoryV1SnapshotsIdExport,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_FILES_FILEID: ApiRepositoryV1SnapshotsIdFilesFileid,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_FILESYSTEM_OBJECTS: ApiRepositoryV1SnapshotsIdFilesystemObjects,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_POLICIES: ApiRepositoryV1SnapshotsIdPolicies,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_POLICIES_POLICY_NAME_MEMBERS: ApiRepositoryV1SnapshotsIdPoliciesPolicyNameMembers,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_POLICIES_POLICY_NAME_MEMBERS_MEMBER_EMAIL: ApiRepositoryV1SnapshotsIdPoliciesPolicyNameMembersMemberEmail,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_ROLES: ApiRepositoryV1SnapshotsIdRoles,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_LINK_DUOS_DATASET_DUOS_ID: ApiRepositoryV1SnapshotsIdLinkDuosDatasetDuosId,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_UNLINK_DUOS_DATASET: ApiRepositoryV1SnapshotsIdUnlinkDuosDataset,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_TAGS: ApiRepositoryV1SnapshotsIdTags,
        PathValues.API_REPOSITORY_V1_DUOS: ApiRepositoryV1Duos,
        PathValues.API_REPOSITORY_V1_DUOS_DUOS_ID: ApiRepositoryV1DuosDuosId,
        PathValues.API_REPOSITORY_V1_DUOS_SYNC_AUTHORIZED_USERS: ApiRepositoryV1DuosSyncAuthorizedUsers,
        PathValues.API_REPOSITORY_V1_DUOS_DUOS_ID_SYNC_AUTHORIZED_USERS: ApiRepositoryV1DuosDuosIdSyncAuthorizedUsers,
        PathValues.API_REPOSITORY_V1_DATASETS: ApiRepositoryV1Datasets,
        PathValues.API_REPOSITORY_V1_DATASETS_TAGS: ApiRepositoryV1DatasetsTags,
        PathValues.API_REPOSITORY_V1_DATASETS_ID: ApiRepositoryV1DatasetsId,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_DATA_TABLE: ApiRepositoryV1DatasetsIdDataTable,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_SUMMARY: ApiRepositoryV1DatasetsIdSummary,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_POLICIES: ApiRepositoryV1DatasetsIdPolicies,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_POLICIES_POLICY_NAME_MEMBERS: ApiRepositoryV1DatasetsIdPoliciesPolicyNameMembers,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_POLICIES_POLICY_NAME_MEMBERS_MEMBER_EMAIL: ApiRepositoryV1DatasetsIdPoliciesPolicyNameMembersMemberEmail,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_ROLES: ApiRepositoryV1DatasetsIdRoles,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_INGEST: ApiRepositoryV1DatasetsIdIngest,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_UPDATE_SCHEMA: ApiRepositoryV1DatasetsIdUpdateSchema,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_TRANSACTIONS: ApiRepositoryV1DatasetsIdTransactions,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_TRANSACTIONS_TRANSACTION_ID: ApiRepositoryV1DatasetsIdTransactionsTransactionId,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_ASSETS: ApiRepositoryV1DatasetsIdAssets,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_ASSETS_ASSETID: ApiRepositoryV1DatasetsIdAssetsAssetid,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_DELETES: ApiRepositoryV1DatasetsIdDeletes,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_TAGS: ApiRepositoryV1DatasetsIdTags,
        PathValues.API_REPOSITORY_V1_REGISTER_USER: ApiRepositoryV1RegisterUser,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES: ApiRepositoryV1DatasetsIdFiles,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_BULK: ApiRepositoryV1DatasetsIdFilesBulk,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_BULK_LOAD_TAG: ApiRepositoryV1DatasetsIdFilesBulkLoadTag,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_BULK_ARRAY: ApiRepositoryV1DatasetsIdFilesBulkArray,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_FILEID: ApiRepositoryV1DatasetsIdFilesFileid,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILESYSTEM_OBJECTS: ApiRepositoryV1DatasetsIdFilesystemObjects,
        PathValues.API_REPOSITORY_V1_JOBS: ApiRepositoryV1Jobs,
        PathValues.API_REPOSITORY_V1_JOBS_ID: ApiRepositoryV1JobsId,
        PathValues.API_REPOSITORY_V1_JOBS_ID_RESULT: ApiRepositoryV1JobsIdResult,
        PathValues.API_REPOSITORY_V1_CONFIGS_NAME: ApiRepositoryV1ConfigsName,
        PathValues.API_REPOSITORY_V1_CONFIGS: ApiRepositoryV1Configs,
        PathValues.API_REPOSITORY_V1_CONFIGS_RESET: ApiRepositoryV1ConfigsReset,
        PathValues.API_REPOSITORY_V1_UPGRADE: ApiRepositoryV1Upgrade,
        PathValues.API_REPOSITORY_V1_SEARCH_ID_INDEX: ApiRepositoryV1SearchIdIndex,
        PathValues.API_REPOSITORY_V1_SEARCH_QUERY: ApiRepositoryV1SearchQuery,
        PathValues.GA4GH_DRS_V1_SERVICEINFO: Ga4ghDrsV1ServiceInfo,
        PathValues.GA4GH_DRS_V1_OBJECTS_OBJECT_ID: Ga4ghDrsV1ObjectsObjectId,
        PathValues.GA4GH_DRS_V1_OBJECTS_OBJECT_ID_ACCESS_ACCESS_ID: Ga4ghDrsV1ObjectsObjectIdAccessAccessId,
        PathValues.API_REPOSITORY_V1_JOURNAL_RESOURCE_KEY: ApiRepositoryV1JournalResourceKey,
    }
)

path_to_api = PathToApi(
    {
        PathValues.STATUS: Status,
        PathValues.CONFIGURATION: Configuration,
        PathValues.SHUTDOWN: Shutdown,
        PathValues.API_RESOURCES_V1_PROFILES: ApiResourcesV1Profiles,
        PathValues.API_RESOURCES_V1_PROFILES_ID: ApiResourcesV1ProfilesId,
        PathValues.API_RESOURCES_V1_PROFILES_ID_POLICIES: ApiResourcesV1ProfilesIdPolicies,
        PathValues.API_RESOURCES_V1_PROFILES_ID_POLICIES_POLICY_NAME_MEMBERS: ApiResourcesV1ProfilesIdPoliciesPolicyNameMembers,
        PathValues.API_RESOURCES_V1_PROFILES_ID_POLICIES_POLICY_NAME_MEMBERS_MEMBER_EMAIL: ApiResourcesV1ProfilesIdPoliciesPolicyNameMembersMemberEmail,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS: ApiRepositoryV1Snapshots,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ROLE_MAP: ApiRepositoryV1SnapshotsRoleMap,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_TAGS: ApiRepositoryV1SnapshotsTags,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID: ApiRepositoryV1SnapshotsId,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_SUMMARY: ApiRepositoryV1SnapshotsIdSummary,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_DATA_TABLE: ApiRepositoryV1SnapshotsIdDataTable,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_EXPORT: ApiRepositoryV1SnapshotsIdExport,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_FILES_FILEID: ApiRepositoryV1SnapshotsIdFilesFileid,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_FILESYSTEM_OBJECTS: ApiRepositoryV1SnapshotsIdFilesystemObjects,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_POLICIES: ApiRepositoryV1SnapshotsIdPolicies,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_POLICIES_POLICY_NAME_MEMBERS: ApiRepositoryV1SnapshotsIdPoliciesPolicyNameMembers,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_POLICIES_POLICY_NAME_MEMBERS_MEMBER_EMAIL: ApiRepositoryV1SnapshotsIdPoliciesPolicyNameMembersMemberEmail,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_ROLES: ApiRepositoryV1SnapshotsIdRoles,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_LINK_DUOS_DATASET_DUOS_ID: ApiRepositoryV1SnapshotsIdLinkDuosDatasetDuosId,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_UNLINK_DUOS_DATASET: ApiRepositoryV1SnapshotsIdUnlinkDuosDataset,
        PathValues.API_REPOSITORY_V1_SNAPSHOTS_ID_TAGS: ApiRepositoryV1SnapshotsIdTags,
        PathValues.API_REPOSITORY_V1_DUOS: ApiRepositoryV1Duos,
        PathValues.API_REPOSITORY_V1_DUOS_DUOS_ID: ApiRepositoryV1DuosDuosId,
        PathValues.API_REPOSITORY_V1_DUOS_SYNC_AUTHORIZED_USERS: ApiRepositoryV1DuosSyncAuthorizedUsers,
        PathValues.API_REPOSITORY_V1_DUOS_DUOS_ID_SYNC_AUTHORIZED_USERS: ApiRepositoryV1DuosDuosIdSyncAuthorizedUsers,
        PathValues.API_REPOSITORY_V1_DATASETS: ApiRepositoryV1Datasets,
        PathValues.API_REPOSITORY_V1_DATASETS_TAGS: ApiRepositoryV1DatasetsTags,
        PathValues.API_REPOSITORY_V1_DATASETS_ID: ApiRepositoryV1DatasetsId,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_DATA_TABLE: ApiRepositoryV1DatasetsIdDataTable,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_SUMMARY: ApiRepositoryV1DatasetsIdSummary,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_POLICIES: ApiRepositoryV1DatasetsIdPolicies,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_POLICIES_POLICY_NAME_MEMBERS: ApiRepositoryV1DatasetsIdPoliciesPolicyNameMembers,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_POLICIES_POLICY_NAME_MEMBERS_MEMBER_EMAIL: ApiRepositoryV1DatasetsIdPoliciesPolicyNameMembersMemberEmail,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_ROLES: ApiRepositoryV1DatasetsIdRoles,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_INGEST: ApiRepositoryV1DatasetsIdIngest,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_UPDATE_SCHEMA: ApiRepositoryV1DatasetsIdUpdateSchema,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_TRANSACTIONS: ApiRepositoryV1DatasetsIdTransactions,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_TRANSACTIONS_TRANSACTION_ID: ApiRepositoryV1DatasetsIdTransactionsTransactionId,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_ASSETS: ApiRepositoryV1DatasetsIdAssets,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_ASSETS_ASSETID: ApiRepositoryV1DatasetsIdAssetsAssetid,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_DELETES: ApiRepositoryV1DatasetsIdDeletes,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_TAGS: ApiRepositoryV1DatasetsIdTags,
        PathValues.API_REPOSITORY_V1_REGISTER_USER: ApiRepositoryV1RegisterUser,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES: ApiRepositoryV1DatasetsIdFiles,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_BULK: ApiRepositoryV1DatasetsIdFilesBulk,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_BULK_LOAD_TAG: ApiRepositoryV1DatasetsIdFilesBulkLoadTag,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_BULK_ARRAY: ApiRepositoryV1DatasetsIdFilesBulkArray,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILES_FILEID: ApiRepositoryV1DatasetsIdFilesFileid,
        PathValues.API_REPOSITORY_V1_DATASETS_ID_FILESYSTEM_OBJECTS: ApiRepositoryV1DatasetsIdFilesystemObjects,
        PathValues.API_REPOSITORY_V1_JOBS: ApiRepositoryV1Jobs,
        PathValues.API_REPOSITORY_V1_JOBS_ID: ApiRepositoryV1JobsId,
        PathValues.API_REPOSITORY_V1_JOBS_ID_RESULT: ApiRepositoryV1JobsIdResult,
        PathValues.API_REPOSITORY_V1_CONFIGS_NAME: ApiRepositoryV1ConfigsName,
        PathValues.API_REPOSITORY_V1_CONFIGS: ApiRepositoryV1Configs,
        PathValues.API_REPOSITORY_V1_CONFIGS_RESET: ApiRepositoryV1ConfigsReset,
        PathValues.API_REPOSITORY_V1_UPGRADE: ApiRepositoryV1Upgrade,
        PathValues.API_REPOSITORY_V1_SEARCH_ID_INDEX: ApiRepositoryV1SearchIdIndex,
        PathValues.API_REPOSITORY_V1_SEARCH_QUERY: ApiRepositoryV1SearchQuery,
        PathValues.GA4GH_DRS_V1_SERVICEINFO: Ga4ghDrsV1ServiceInfo,
        PathValues.GA4GH_DRS_V1_OBJECTS_OBJECT_ID: Ga4ghDrsV1ObjectsObjectId,
        PathValues.GA4GH_DRS_V1_OBJECTS_OBJECT_ID_ACCESS_ACCESS_ID: Ga4ghDrsV1ObjectsObjectIdAccessAccessId,
        PathValues.API_REPOSITORY_V1_JOURNAL_RESOURCE_KEY: ApiRepositoryV1JournalResourceKey,
    }
)
