import pytest
import uuid

from pulp_smash.pulp3.utils import gen_distribution, gen_repo

from pulpcore.client.pulp_file import (
    ApiException,
)
from pulpcore.client.pulp_file import AsyncOperationResponse

from pulp_file.tests.functional.utils import gen_file_remote, gen_artifact


@pytest.fixture()
def gen_users(gen_user):
    """Returns a user generator function for the tests."""

    def _gen_users(role_names=list()):
        if isinstance(role_names, str):
            role_names = [role_names]
        viewer_roles = [f"file.{role}_viewer" for role in role_names]
        creator_roles = [f"file.{role}_creator" for role in role_names]
        alice = gen_user(model_roles=viewer_roles)
        bob = gen_user(model_roles=creator_roles)
        charlie = gen_user()
        return alice, bob, charlie

    return _gen_users


@pytest.fixture
def try_action(monitor_task):
    def _try_action(user, client, action, outcome, *args, **kwargs):
        action_api = getattr(client, f"{action}_with_http_info")
        try:
            with user:
                response, status, _ = action_api(*args, **kwargs, _return_http_data_only=False)
            if isinstance(response, AsyncOperationResponse):
                response = monitor_task(response.task)
        except ApiException as e:
            assert e.status == outcome, f"{e}"
        else:
            assert status == outcome, f"User performed {action} when they shouldn't been able to"
            return response

    return _try_action


def test_basic_actions(
    gen_users, file_repository_api_client, gen_object_with_cleanup, try_action, file_repo
):
    """Test list, read, create, update and delete apis."""
    alice, bob, charlie = gen_users("filerepository")

    a_list = try_action(alice, file_repository_api_client, "list", 200)
    assert a_list.count >= 1
    b_list = try_action(bob, file_repository_api_client, "list", 200)
    c_list = try_action(charlie, file_repository_api_client, "list", 200)
    assert (b_list.count, c_list.count) == (0, 0)

    # Create testing
    try_action(alice, file_repository_api_client, "create", 403, gen_repo())
    repo = try_action(bob, file_repository_api_client, "create", 201, gen_repo())
    try_action(charlie, file_repository_api_client, "create", 403, gen_repo())

    # View testing
    try_action(alice, file_repository_api_client, "read", 200, repo.pulp_href)
    try_action(bob, file_repository_api_client, "read", 200, repo.pulp_href)
    try_action(charlie, file_repository_api_client, "read", 404, repo.pulp_href)

    # Update testing
    update_args = [repo.pulp_href, {"name": str(uuid.uuid4())}]
    try_action(alice, file_repository_api_client, "partial_update", 403, *update_args)
    try_action(bob, file_repository_api_client, "partial_update", 202, *update_args)
    try_action(charlie, file_repository_api_client, "partial_update", 404, *update_args)

    # Delete testing
    try_action(alice, file_repository_api_client, "delete", 403, repo.pulp_href)
    try_action(charlie, file_repository_api_client, "delete", 404, repo.pulp_href)
    try_action(bob, file_repository_api_client, "delete", 202, repo.pulp_href)


@pytest.mark.parallel
def test_role_management(
    gen_users, file_repository_api_client, gen_object_with_cleanup, try_action
):
    """Check that role management apis."""
    alice, bob, charlie = gen_users("filerepository")
    with bob:
        href = gen_object_with_cleanup(file_repository_api_client, gen_repo()).pulp_href
    # Permission check testing
    aperm_response = try_action(alice, file_repository_api_client, "my_permissions", 200, href)
    assert aperm_response.permissions == []
    bperm_response = try_action(bob, file_repository_api_client, "my_permissions", 200, href)
    assert len(bperm_response.permissions) > 0
    try_action(charlie, file_repository_api_client, "my_permissions", 404, href)

    # Add "viewer" role testing
    nested_role = {"users": [charlie.username], "role": "file.filerepository_viewer"}
    try_action(alice, file_repository_api_client, "add_role", 403, href, nested_role=nested_role)
    try_action(charlie, file_repository_api_client, "add_role", 404, href, nested_role=nested_role)
    try_action(bob, file_repository_api_client, "add_role", 201, href, nested_role=nested_role)

    # Permission check testing again
    cperm_response = try_action(charlie, file_repository_api_client, "my_permissions", 200, href)
    assert len(cperm_response.permissions) == 1

    # Remove "viewer" role testing
    try_action(alice, file_repository_api_client, "remove_role", 403, href, nested_role=nested_role)
    try_action(
        charlie, file_repository_api_client, "remove_role", 403, href, nested_role=nested_role
    )
    try_action(bob, file_repository_api_client, "remove_role", 201, href, nested_role=nested_role)

    # Permission check testing one more time
    try_action(charlie, file_repository_api_client, "my_permissions", 404, href)


def test_content_apis(
    gen_users,
    file_content_api_client,
    file_repository_api_client,
    file_remote_api_client,
    file_fixture_server,
    basic_manifest_path,
    gen_object_with_cleanup,
    monitor_task,
    try_action,
):
    """Check content listing, scoping and upload APIs."""
    alice, bob, charlie = gen_users()
    aresponse = try_action(alice, file_content_api_client, "list", 200)
    bresponse = try_action(bob, file_content_api_client, "list", 200)
    cresponse = try_action(charlie, file_content_api_client, "list", 200)

    assert aresponse.count == bresponse.count == cresponse.count == 0

    alice, bob, charlie = gen_users(["filerepository"])
    repo = gen_object_with_cleanup(file_repository_api_client, gen_repo())
    remote = gen_object_with_cleanup(file_remote_api_client, gen_file_remote())
    monitor_task(file_repository_api_client.sync(repo.pulp_href, {"remote": remote.pulp_href}).task)

    aresponse = try_action(alice, file_content_api_client, "list", 200)
    bresponse = try_action(bob, file_content_api_client, "list", 200)
    cresponse = try_action(charlie, file_content_api_client, "list", 200)

    assert aresponse.count > bresponse.count
    assert bresponse.count == cresponse.count == 0

    nested_role = {"users": [charlie.username], "role": "file.filerepository_viewer"}
    file_repository_api_client.add_role(repo.pulp_href, nested_role)

    cresponse = try_action(charlie, file_content_api_client, "list", 200)
    assert cresponse.count > bresponse.count

    file_url = file_fixture_server.make_url("/basic")
    # This might need to change if we change Artifact's default upload policy
    artifact1 = gen_artifact(url=file_url + "/1.iso")["pulp_href"]

    body = {"artifact": artifact1}
    try_action(alice, file_content_api_client, "create", 400, "1.iso", **body)
    body["repository"] = repo.pulp_href
    try_action(bob, file_content_api_client, "create", 403, "1.iso", **body)
    try_action(charlie, file_content_api_client, "create", 403, "1.iso", **body)

    nested_role = {"users": [charlie.username], "role": "file.filerepository_owner"}
    file_repository_api_client.add_role(repo.pulp_href, nested_role)
    try_action(charlie, file_content_api_client, "create", 202, "1.iso", **body)


@pytest.mark.parallel
def test_repository_apis(
    gen_users,
    file_repository_api_client,
    file_remote_api_client,
    gen_object_with_cleanup,
    try_action,
):
    """Test repository specific actions, Modify & Sync."""
    alice, bob, charlie = gen_users(["filerepository", "fileremote"])
    # Sync tests
    with bob:
        repo = gen_object_with_cleanup(file_repository_api_client, gen_repo())
        bob_remote = gen_object_with_cleanup(file_remote_api_client, gen_file_remote())
    body = {"remote": bob_remote.pulp_href}
    try_action(alice, file_repository_api_client, "sync", 403, repo.pulp_href, body)
    try_action(bob, file_repository_api_client, "sync", 202, repo.pulp_href, body)
    try_action(charlie, file_repository_api_client, "sync", 404, repo.pulp_href, body)
    # Modify tests
    try_action(alice, file_repository_api_client, "modify", 403, repo.pulp_href, {})
    try_action(bob, file_repository_api_client, "modify", 202, repo.pulp_href, {})
    try_action(charlie, file_repository_api_client, "modify", 404, repo.pulp_href, {})


@pytest.mark.parallel
def test_repository_version_repair(
    gen_users,
    file_repository_api_client,
    file_repository_version_api_client,
    gen_object_with_cleanup,
    try_action,
):
    """Test the repository version repair action"""
    alice, bob, charlie = gen_users("filerepository")
    with bob:
        repo = gen_object_with_cleanup(file_repository_api_client, gen_repo())
        ver_href = repo.latest_version_href
    body = {"verify_checksums": True}
    try_action(alice, file_repository_version_api_client, "repair", 403, ver_href, body)
    try_action(bob, file_repository_version_api_client, "repair", 202, ver_href, body)
    try_action(charlie, file_repository_version_api_client, "repair", 403, ver_href, body)


@pytest.mark.parallel
def test_acs_apis(
    gen_users,
    file_remote_api_client,
    file_acs_api_client,
    gen_object_with_cleanup,
    monitor_task,
    try_action,
):
    """Test acs refresh action."""
    alice, bob, charlie = gen_users(["filealternatecontentsource", "fileremote"])
    with bob:
        remote_body = gen_file_remote(policy="on_demand")
        remote = gen_object_with_cleanup(file_remote_api_client, remote_body)
        body = {"name": str(uuid.uuid4()), "remote": remote.pulp_href}
        acs = file_acs_api_client.create(body)
    # Test that only bob can do the refresh action
    try_action(alice, file_acs_api_client, "refresh", 403, acs.pulp_href)
    try_action(bob, file_acs_api_client, "refresh", 202, acs.pulp_href)
    try_action(charlie, file_acs_api_client, "refresh", 404, acs.pulp_href)

    monitor_task(file_acs_api_client.delete(acs.pulp_href).task)


@pytest.mark.parallel
def test_object_creation(
    gen_users,
    file_repository_api_client,
    file_publication_api_client,
    file_distribution_api_client,
    gen_object_with_cleanup,
    monitor_task,
    try_action,
):
    """Test that objects can only be created when having all the required permissions."""
    alice, bob, charlie = gen_users(["filerepository", "filepublication", "filedistribution"])
    admin_repo = gen_object_with_cleanup(file_repository_api_client, gen_repo())
    with bob:
        repo = gen_object_with_cleanup(file_repository_api_client, gen_repo())
    try_action(
        bob, file_publication_api_client, "create", 403, {"repository": admin_repo.pulp_href}
    )
    pub = try_action(
        bob, file_publication_api_client, "create", 202, {"repository": repo.pulp_href}
    )
    pub = pub.created_resources[0]
    admin_body = gen_distribution(repository=admin_repo.pulp_href)
    bob_body = gen_distribution(publication=pub)
    try_action(bob, file_distribution_api_client, "create", 403, admin_body)
    dis = try_action(bob, file_distribution_api_client, "create", 202, bob_body).created_resources[
        0
    ]
    admin_body = {"repository": admin_repo.pulp_href, "publication": None}
    bob_body = {"repository": repo.pulp_href, "publication": None}
    try_action(bob, file_distribution_api_client, "partial_update", 403, dis, admin_body)
    try_action(bob, file_distribution_api_client, "partial_update", 202, dis, bob_body)
    monitor_task(file_distribution_api_client.delete(dis).task)
