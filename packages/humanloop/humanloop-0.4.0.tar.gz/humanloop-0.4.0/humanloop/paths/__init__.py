# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from humanloop.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    COMPLETION = "/completion"
    COMPLETIONDEPLOYED = "/completion-deployed"
    COMPLETIONEXPERIMENT = "/completion-experiment"
    COMPLETIONMODELCONFIG = "/completion-model-config"
    CHAT = "/chat"
    CHATDEPLOYED = "/chat-deployed"
    CHATEXPERIMENT = "/chat-experiment"
    CHATMODELCONFIG = "/chat-model-config"
    LOGS = "/logs"
    FEEDBACK = "/feedback"
    PROJECTS = "/projects"
    PROJECTS_ID = "/projects/{id}"
    PROJECTS_ID_MODELCONFIGS = "/projects/{id}/model-configs"
    PROJECTS_ID_MODELCONFIG = "/projects/{id}/model-config"
    PROJECTS_ID_ACTIVEMODELCONFIG = "/projects/{id}/active-model-config"
    PROJECTS_ID_ACTIVEEXPERIMENT = "/projects/{id}/active-experiment"
    PROJECTS_ID_FEEDBACKTYPES = "/projects/{id}/feedback-types"
    PROJECTS_ID_EXPORT = "/projects/{id}/export"
    APPS = "/apps"
    APPS_ID = "/apps/{id}"
    APPS_ID_SESSIONS = "/apps/{id}/sessions"
    SESSIONS = "/sessions"
    SESSIONS_ID = "/sessions/{id}"
    SESSIONS_ID_EVENTS = "/sessions/{id}/events"
    MODELCONFIGS = "/model-configs"
    MODELCONFIGS_ID = "/model-configs/{id}"
    PROJECTS_PROJECT_ID_EXPERIMENTS = "/projects/{project_id}/experiments"
    EXPERIMENTS_EXPERIMENT_ID = "/experiments/{experiment_id}"
    EXPERIMENTS_EXPERIMENT_ID_MODELCONFIG = "/experiments/{experiment_id}/model-config"
