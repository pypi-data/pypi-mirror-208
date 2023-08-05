"""Tests that sync file plugin repositories."""
import uuid

import pytest

from pulpcore.tests.functional.utils import PulpTaskError
from pulp_smash.pulp3.utils import (
    get_added_content_summary,
    get_content_summary,
    wget_download_on_host,
)

from pulp_file.tests.functional.constants import (
    FILE_FIXTURE_URL,
)

from pulpcore.client.pulp_file import (
    RepositorySyncURL,
)


def test_sync_file_protocol_handler(
    file_repo,
    file_repository_api_client,
    file_remote_api_client,
    gen_object_with_cleanup,
    monitor_task,
):
    """Test syncing from a file repository with the file:// protocol handler"""
    wget_download_on_host(FILE_FIXTURE_URL, "/tmp")

    remote_kwargs = {
        "url": "file:///tmp/file/PULP_MANIFEST",
        "policy": "immediate",
        "name": str(uuid.uuid4()),
    }
    remote = gen_object_with_cleanup(file_remote_api_client, remote_kwargs)

    body = RepositorySyncURL(remote=remote.pulp_href)
    monitor_task(file_repository_api_client.sync(file_repo.pulp_href, body).task)

    file_repo = file_repository_api_client.read(file_repo.pulp_href)
    assert file_repo.latest_version_href.endswith("/versions/1/")
    assert get_content_summary(file_repo.to_dict()) == {"file.file": 3}
    assert get_added_content_summary(file_repo.to_dict()) == {"file.file": 3}


@pytest.mark.parallel
def test_mirrored_sync(
    file_repo,
    file_remote_ssl_factory,
    file_repository_api_client,
    basic_manifest_path,
    monitor_task,
):
    """Assert that syncing the repository w/ mirror=True creates a publication."""
    remote = file_remote_ssl_factory(manifest_path=basic_manifest_path, policy="on_demand")

    repository_sync_data = RepositorySyncURL(remote=remote.pulp_href, mirror=True)
    sync_response = file_repository_api_client.sync(file_repo.pulp_href, repository_sync_data)
    task = monitor_task(sync_response.task)

    # Check that all the appropriate resources were created
    assert len(task.created_resources) == 2
    assert any(["publication" in resource for resource in task.created_resources])
    assert any(["version" in resource for resource in task.created_resources])


@pytest.mark.parallel
def test_invalid_url(
    file_repo,
    gen_object_with_cleanup,
    file_remote_api_client,
    file_repository_api_client,
    monitor_task,
):
    """Sync a repository using a remote url that does not exist."""
    remote_kwargs = {
        "url": "http://i-am-an-invalid-url.com/invalid/",
        "policy": "immediate",
        "name": str(uuid.uuid4()),
    }
    remote = gen_object_with_cleanup(file_remote_api_client, remote_kwargs)

    body = RepositorySyncURL(remote=remote.pulp_href)
    with pytest.raises(PulpTaskError):
        monitor_task(file_repository_api_client.sync(file_repo.pulp_href, body).task)


@pytest.mark.parallel
def test_invalid_file(
    file_repo, file_repository_api_client, invalid_manifest_path, file_remote_factory, monitor_task
):
    """Sync a repository using an invalid file repository."""
    remote = file_remote_factory(manifest_path=invalid_manifest_path, policy="immediate")
    body = RepositorySyncURL(remote=remote.pulp_href)
    with pytest.raises(PulpTaskError):
        monitor_task(file_repository_api_client.sync(file_repo.pulp_href, body).task)


@pytest.mark.parallel
def test_duplicate_file_sync(
    file_repo,
    file_remote_factory,
    duplicate_filename_paths,
    file_repository_api_client,
    monitor_task,
):
    remote = file_remote_factory(manifest_path=duplicate_filename_paths[0], policy="on_demand")
    remote2 = file_remote_factory(manifest_path=duplicate_filename_paths[1], policy="on_demand")

    body = RepositorySyncURL(remote=remote.pulp_href)
    monitor_task(file_repository_api_client.sync(file_repo.pulp_href, body).task)
    file_repo = file_repository_api_client.read(file_repo.pulp_href)

    assert get_content_summary(file_repo.to_dict()) == {"file.file": 3}
    assert get_added_content_summary(file_repo.to_dict()) == {"file.file": 3}
    assert file_repo.latest_version_href.endswith("/1/")

    body = RepositorySyncURL(remote=remote2.pulp_href)
    monitor_task(file_repository_api_client.sync(file_repo.pulp_href, body).task)
    file_repo = file_repository_api_client.read(file_repo.pulp_href)

    assert get_content_summary(file_repo.to_dict()) == {"file.file": 3}
    assert get_added_content_summary(file_repo.to_dict()) == {"file.file": 3}
    assert file_repo.latest_version_href.endswith("/2/")


@pytest.mark.parallel
def test_filepath_includes_commas(
    file_repo,
    file_remote_factory,
    manifest_path_with_commas,
    file_repository_api_client,
    monitor_task,
):
    """Sync a repository using a manifest file with a file whose relative_path includes commas"""
    remote = file_remote_factory(manifest_path=manifest_path_with_commas, policy="on_demand")

    body = RepositorySyncURL(remote=remote.pulp_href)
    monitor_task(file_repository_api_client.sync(file_repo.pulp_href, body).task)
    file_repo = file_repository_api_client.read(file_repo.pulp_href)

    assert get_content_summary(file_repo.to_dict()) == {"file.file": 3}
    assert get_added_content_summary(file_repo.to_dict()) == {"file.file": 3}
    assert file_repo.latest_version_href.endswith("/1/")
