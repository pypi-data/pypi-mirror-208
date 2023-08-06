import os
import shlex
import subprocess
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
import tabulate

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.experimental_workspace import (
    ExperimentalWorkspace,
)
from anyscale.cluster_config import configure_for_session
from anyscale.controllers.base_controller import BaseController
from anyscale.util import get_endpoint, get_working_dir
from anyscale.workspace import load_workspace_id_or_throw, write_workspace_id_to_disk


ANYSCALE_WORKSPACES_SSH_OPTIONS = [
    "-o",
    "StrictHostKeyChecking=no",
    "-o",
    "UserKnownHostsFile=/dev/null",
    "-o",
    "IdentitiesOnly=yes",
]


class WorkspaceCommandContext(BaseModel):
    cluster_config: Dict[str, Any]
    head_ip: str
    project_id: str


class WorkspaceController(BaseController):
    def __init__(
        self, log: Optional[BlockLogger] = None, initialize_auth_api_client: bool = True
    ):
        if log is None:
            log = BlockLogger()

        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log

    def list(self) -> None:
        """
        prints a non-exhaustive tabular list of information about non-deleted workspaces.
        """
        workspaces_data: List[
            ExperimentalWorkspace
        ] = self.api_client.list_workspaces_api_v2_experimental_workspaces_get().results

        workspaces_table: List[List[Any]] = [
            [
                workspace.name,
                workspace.id,
                workspace.state,
                get_endpoint(f"/workspaces/{workspace.id}/{workspace.cluster_id}"),
            ]
            for workspace in workspaces_data
            if not workspace.is_deleted
        ]

        table = tabulate.tabulate(
            workspaces_table, headers=["NAME", "ID", "STATE", "URL",], tablefmt="plain",
        )

        print(f"Workspaces:\n{table}")

    def clone(self, workspace: ExperimentalWorkspace) -> None:
        dir_name = workspace.name
        os.makedirs(dir_name)

        workspace_id = workspace.id
        write_workspace_id_to_disk(workspace_id, dir_name)

    def get_activated_workspace(self) -> ExperimentalWorkspace:
        workspace_id = load_workspace_id_or_throw()
        return self.api_client.get_workspace_api_v2_experimental_workspaces_workspace_id_get(
            workspace_id
        ).result

    def get_workspace_dir_name(self) -> str:
        """
        Currently the directory name of Workspaces/Clusters
        is determiend by the project name.
        """
        workspace = self.get_activated_workspace()
        project = self.api_client.get_project_api_v2_projects_project_id_get(
            workspace.project_id
        ).result
        return project.name

    def _get_workspace_command_context(self) -> WorkspaceCommandContext:
        workspace = self.get_activated_workspace()

        cluster_id = workspace.cluster_id
        project_id = workspace.project_id

        cluster_config = configure_for_session(
            cluster_id,
            api_client=self.api_client,
            disable_project_sync=True,
            ssh_dir="/tmp/anyscale/.ssh",
        )
        head_ip = self.api_client.get_session_head_ip_api_v2_sessions_session_id_head_ip_get(
            cluster_id
        ).result.head_ip

        return WorkspaceCommandContext(
            cluster_config=cluster_config, head_ip=head_ip, project_id=project_id,
        )

    def run_cmd(self, cmd: str, args: List[str]):
        workspace_command_context = self._get_workspace_command_context()
        cluster_config = workspace_command_context.cluster_config

        key_path = cluster_config["auth"]["ssh_private_key"]

        head_ip = workspace_command_context.head_ip
        ssh_user = cluster_config["auth"]["ssh_user"]
        target_host = f"{ssh_user}@{head_ip}"

        command = shlex.quote(cmd)

        ssh_command = (
            ["ssh"]
            + ANYSCALE_WORKSPACES_SSH_OPTIONS
            + [
                "-o",
                f"ProxyCommand=ssh -W %h:%p -i {key_path} -o StrictHostKeyChecking=accept-new {target_host}",
            ]
            + ["-tt", "-i", key_path]
            + ["ray@0.0.0.0", "-p", "5020"]
            + (args if args and len(args) > 0 else [""])
            + [f"sh -c {command}"]
        )

        subprocess.run(ssh_command)

    def run_rsync(
        self,
        local_path: str,
        *,
        down: bool,
        rsync_filters: List[str],
        rsync_excludes: List[str],
    ) -> None:
        workspace_command_context = self._get_workspace_command_context()
        cluster_config = workspace_command_context.cluster_config
        head_ip = workspace_command_context.head_ip
        project_id = workspace_command_context.project_id

        ssh_user: str = cluster_config["auth"]["ssh_user"]
        key_path: str = cluster_config["auth"]["ssh_private_key"]

        identity_file_option = ["-i", key_path]
        proxy_thorugh_ssh_user_option = [
            "-o",
            f"ProxyCommand=ssh -W %h:%p -i {key_path} -o StrictHostKeyChecking=accept-new {ssh_user}@{head_ip}",
        ]
        ray_user_ssh_port_option = ["-p", "5020"]
        base_ssh_command = (
            ["ssh"]
            + identity_file_option
            + ANYSCALE_WORKSPACES_SSH_OPTIONS
            + proxy_thorugh_ssh_user_option
            + ray_user_ssh_port_option
        )

        source_directory = (
            get_working_dir(cluster_config, project_id, self.api_client) + "/"
        )

        rsync_command = [
            "rsync",
            "--rsh",
            subprocess.list2cmdline(base_ssh_command),
            "-rvz",
            "--delete",
        ]

        for rsync_exclude in rsync_excludes:
            rsync_command.extend(["--exclude", rsync_exclude])

        for rsync_filter in rsync_filters:
            rsync_command.extend(["--filter", f"dir-merge,- {rsync_filter}"])

        # TODO: Perhaps include this in cluster_config somewhere so that below isn't hardcoded
        # if either the user or host for the ray container is changed in the future
        ray_user_on_host = "ray@0.0.0.0"
        source_directory = (
            get_working_dir(cluster_config, project_id, self.api_client) + "/"
        )

        if down:
            rsync_command += [
                f"{ray_user_on_host}:{source_directory}",
                local_path,
            ]
        else:
            rsync_command += [
                local_path,
                f"{ray_user_on_host}:{source_directory}",
            ]

        subprocess.run(rsync_command)
