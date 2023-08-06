import base64
import logging
import os
import traceback

from keycloak import KeycloakAdmin
from kubernetes import client, config

from nebari_workflow_controller.exceptions import (
    NebariWorkflowControllerException as NWFCException,
)
from nebari_workflow_controller.exceptions import (
    NebariWorkflowControllerUnsupportedException as NWFCUnsupportedException,
)
from nebari_workflow_controller.models import KeycloakGroup, KeycloakUser

logger = logging.getLogger(__name__)


def process_unhandled_exception(e, return_response, logger):
    error_message = f"An internal error occurred in nebari-workflow-controller while mutating the workflow.  Please open an issue at https://github.com/nebari-dev/nebari-workflow-controller/issues.  The error was: {traceback.format_exc()}"
    logger.exception(e)
    return return_response(False, message=error_message)


def sent_by_argo(workflow: dict):
    # Check if any of these labels shows up under ManagedFields with manager "argo" or "workflow-controller".  If so, then we can trust the uid from there.
    possible_labels_added_by_argo = {
        "workflows.argoproj.io/creator",
        "workflows.argoproj.io/cron-workflow",
        "workflows.argoproj.io/resubmitted-from-workflow",
    }

    for managedField in workflow["metadata"]["managedFields"]:
        if managedField.get("manager", "") not in {"argo", "workflow-controller"}:
            continue

        for possible_label_added_by_argo in possible_labels_added_by_argo:
            if (
                "f:" + possible_label_added_by_argo
                in managedField["fieldsV1"]["f:metadata"]["f:labels"]
            ):
                return possible_label_added_by_argo

    return None


def get_keycloak_user(request):
    kcadm = KeycloakAdmin(
        server_url=os.environ["KEYCLOAK_URL"],
        username=os.environ["KEYCLOAK_USERNAME"],
        password=os.environ["KEYCLOAK_PASSWORD"],
        user_realm_name="master",
        realm_name="nebari",
        client_id="admin-cli",
    )

    config.incluster_config.load_incluster_config()

    keycloak_uid, keycloak_username = get_keycloak_uid_username(
        kcadm, request["request"]["object"], client.ApiClient()
    )
    groups = kcadm.get_user_groups(keycloak_uid)

    keycloak_user = KeycloakUser(
        username=keycloak_username,
        id=keycloak_uid,
        groups=[KeycloakGroup(**group) for group in groups],
    )
    return keycloak_user


def get_keycloak_uid_username(
    kcadm,
    workflow: dict,
    k8s_client: client.ApiClient,
) -> KeycloakUser:
    # Check if `workflows.argoproj.io/creator` shows up under ManagedFields with manager "argo".
    # If so, then we can trust the uid from there.  If not, then we have to trust the username from the request.
    # Should volumeMounts be allowed based on current requester or based on the original requester?  Current Requester

    # TODO: put try catch here if can't connect to keycloak
    label_added_by_argo = sent_by_argo(workflow)
    if not label_added_by_argo:
        raise NWFCUnsupportedException(
            "Only workflows submitted via Argo Workflows (not kubectl) are supported by Nebari Workflow Controller"
        )

    if label_added_by_argo == "workflows.argoproj.io/creator":
        keycloak_uid = workflow["metadata"]["labels"][label_added_by_argo]
        keycloak_username = kcadm.get_user(keycloak_uid)["username"]
        return keycloak_uid, keycloak_username
    elif label_added_by_argo == "workflows.argoproj.io/resubmitted-from-workflow":
        raise NWFCUnsupportedException(
            "Resubmitting workflows is not supported by Nebari Workflow Controller"
        )
    elif label_added_by_argo == "workflows.argoproj.io/cron-workflow":
        api_path = "/apis/argoproj.io/v1alpha1/namespaces/{namespace}/cronworkflows/{parent_workflow_name}"
        parent_workflow_name = workflow["metadata"]["labels"][label_added_by_argo]
        # TODO: handle if parent workflow is not found.
        parent_workflow = k8s_client.call_api(
            api_path.format(
                namespace=os.environ["NAMESPACE"],
                parent_workflow_name=parent_workflow_name,
            ),
            "GET",
            auth_settings=["BearerToken"],
            response_type="object",
        )[0]
        return get_keycloak_uid_username(kcadm, parent_workflow, k8s_client)
    else:
        raise Exception("Label {label_added_by_argo} must be handled, but was not.")


def base_return_response(
    allowed, apiVersion, request_uid, message=None, patch=None, patchType=None
):
    if (not patch) != (not patchType):
        raise Exception(
            f"patch and patchType must be specified together.  patch: {patch}, patchType: {patchType}"
        )
    if (allowed) != (message is None):
        raise Exception(
            "Failure message must be specified only when workflow not allowed"
        )

    response = {
        "apiVersion": apiVersion,
        "kind": "AdmissionReview",
        "response": {
            "allowed": allowed,
            "uid": request_uid,
        },
    }
    if not allowed:
        response["response"]["status"] = {"message": message}

    if patch:
        response["response"]["patch"] = base64.b64encode(str(patch).encode()).decode()
        response["response"]["patchType"] = patchType

    return response


def find_invalid_volume_mount(
    volume_mounts, volume_name_pvc_name_map, allowed_pvc_sub_paths_iterable
):
    # verify only allowed volume_mounts were mounted
    for volume_mount in volume_mounts:
        if volume_mount["name"] in volume_name_pvc_name_map:
            for allowed_pvc, allowed_sub_paths in allowed_pvc_sub_paths_iterable:
                if volume_name_pvc_name_map[volume_mount["name"]] == allowed_pvc:
                    if (
                        sub_path := volume_mount.get("subPath", "")
                    ) not in allowed_sub_paths:
                        denyReason = f"Workflow attempts to mount disallowed subPath: {sub_path}. Allowed subPaths are: {allowed_sub_paths}."
                        logger.info(denyReason)
                        return denyReason


def get_user_pod_spec(keycloak_user):
    config.incluster_config.load_incluster_config()
    k8s_client = client.CoreV1Api()

    jupyter_pod_list = k8s_client.list_namespaced_pod(
        os.environ["NAMESPACE"],
        label_selector=f"hub.jupyter.org/username={keycloak_user.username}",
    ).items

    if len(jupyter_pod_list) > 1:
        logger.warning(
            f"More than one pod found for user {keycloak_user.username}. Using last pod started."
        )
        jupyter_pod_list.sort(key=lambda pod: pod.status.start_time, reverse=True)

    # throw error if no pods found
    if len(jupyter_pod_list) == 0:
        raise NWFCException(
            f"A user pod instance for Jupyterhub user {keycloak_user.username} must be running when workflow starts. No pod found for user {keycloak_user.username}."
        )

    jupyter_pod_spec = jupyter_pod_list[0]
    return jupyter_pod_spec


def get_spec_keep_portions(user_pod_spec, api):
    return [
        (
            [
                api.sanitize_for_serialization(iC)
                for iC in user_pod_spec.spec.init_containers
            ],
            "initContainers",
        ),
        (
            api.sanitize_for_serialization(user_pod_spec.spec.security_context),
            "securityContext",
        ),
        (
            [api.sanitize_for_serialization(t) for t in user_pod_spec.spec.tolerations],
            "tolerations",
        ),
        (
            [
                api.sanitize_for_serialization(v)
                for v in user_pod_spec.spec.volumes
                if not v.name.startswith("kupe-api-access-")
            ],
            "volumes",
        ),
        (
            api.sanitize_for_serialization(user_pod_spec.spec.node_selector),
            "nodeSelector",
        ),
    ]


def recursive_dict_merge(greater_dict, lesser_dict, path=None):
    "merges lesser_dict into greater_dict and assigns to greater_dict, greater_dict value takes precedence in case of conflict between greater and lesser dict"
    if path is None:
        path = []
    for key in lesser_dict:
        if key in greater_dict:
            if isinstance(greater_dict[key], dict) and isinstance(
                lesser_dict[key], dict
            ):
                recursive_dict_merge(
                    greater_dict[key], lesser_dict[key], path + [str(key)]
                )
            else:
                pass
        else:
            greater_dict[key] = lesser_dict[key]
    return greater_dict


def get_container_keep_portions(user_pod_spec, api):
    return [
        (user_pod_spec.spec.containers[0].image, "image"),
        (
            [
                api.sanitize_for_serialization(var)
                for var in user_pod_spec.spec.containers[0].env
            ],
            "env",
        ),
        (
            api.sanitize_for_serialization(user_pod_spec.spec.containers[0].lifecycle),
            "lifecycle",
        ),
        (
            api.sanitize_for_serialization(user_pod_spec.spec.containers[0].resources),
            "resources",
        ),
        (
            api.sanitize_for_serialization(
                user_pod_spec.spec.containers[0].security_context
            ),
            "securityContext",
        ),
        (
            [
                api.sanitize_for_serialization(v)
                for v in user_pod_spec.spec.containers[0].volume_mounts
            ],
            "volumeMounts",
        ),
        (user_pod_spec.spec.containers[0].working_dir, "workingDir"),
    ]


def mutate_template(
    container_keep_portions,
    spec_keep_portions,
    template,
):
    for value, key in container_keep_portions:
        if "container" not in template:
            continue

        if isinstance(value, dict):
            if key in template["container"]:
                recursive_dict_merge(template["container"][key], value)
            else:
                template["container"][key] = value
        elif isinstance(value, list):
            if key in template["container"]:
                template["container"][key].append(value)
            else:
                template["container"][key] = value
        else:
            template["container"][key] = value

    for value, key in spec_keep_portions:
        if isinstance(value, dict):
            if key in template:
                recursive_dict_merge(template[key], value)
            else:
                template[key] = value
        elif isinstance(value, list):
            if key in template:
                template[key].append(value)
            else:
                template[key] = value
        else:
            template[key] = value
