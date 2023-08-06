import typing_extensions

from humanloop.paths import PathValues
from humanloop.apis.paths.completion import Completion
from humanloop.apis.paths.completion_deployed import CompletionDeployed
from humanloop.apis.paths.completion_experiment import CompletionExperiment
from humanloop.apis.paths.completion_model_config import CompletionModelConfig
from humanloop.apis.paths.chat import Chat
from humanloop.apis.paths.chat_deployed import ChatDeployed
from humanloop.apis.paths.chat_experiment import ChatExperiment
from humanloop.apis.paths.chat_model_config import ChatModelConfig
from humanloop.apis.paths.logs import Logs
from humanloop.apis.paths.feedback import Feedback
from humanloop.apis.paths.projects import Projects
from humanloop.apis.paths.projects_id import ProjectsId
from humanloop.apis.paths.projects_id_model_configs import ProjectsIdModelConfigs
from humanloop.apis.paths.projects_id_model_config import ProjectsIdModelConfig
from humanloop.apis.paths.projects_id_active_model_config import ProjectsIdActiveModelConfig
from humanloop.apis.paths.projects_id_active_experiment import ProjectsIdActiveExperiment
from humanloop.apis.paths.projects_id_feedback_types import ProjectsIdFeedbackTypes
from humanloop.apis.paths.projects_id_export import ProjectsIdExport
from humanloop.apis.paths.apps import Apps
from humanloop.apis.paths.apps_id import AppsId
from humanloop.apis.paths.apps_id_sessions import AppsIdSessions
from humanloop.apis.paths.sessions import Sessions
from humanloop.apis.paths.sessions_id import SessionsId
from humanloop.apis.paths.sessions_id_events import SessionsIdEvents
from humanloop.apis.paths.model_configs import ModelConfigs
from humanloop.apis.paths.model_configs_id import ModelConfigsId
from humanloop.apis.paths.projects_project_id_experiments import ProjectsProjectIdExperiments
from humanloop.apis.paths.experiments_experiment_id import ExperimentsExperimentId
from humanloop.apis.paths.experiments_experiment_id_model_config import ExperimentsExperimentIdModelConfig

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.COMPLETION: Completion,
        PathValues.COMPLETIONDEPLOYED: CompletionDeployed,
        PathValues.COMPLETIONEXPERIMENT: CompletionExperiment,
        PathValues.COMPLETIONMODELCONFIG: CompletionModelConfig,
        PathValues.CHAT: Chat,
        PathValues.CHATDEPLOYED: ChatDeployed,
        PathValues.CHATEXPERIMENT: ChatExperiment,
        PathValues.CHATMODELCONFIG: ChatModelConfig,
        PathValues.LOGS: Logs,
        PathValues.FEEDBACK: Feedback,
        PathValues.PROJECTS: Projects,
        PathValues.PROJECTS_ID: ProjectsId,
        PathValues.PROJECTS_ID_MODELCONFIGS: ProjectsIdModelConfigs,
        PathValues.PROJECTS_ID_MODELCONFIG: ProjectsIdModelConfig,
        PathValues.PROJECTS_ID_ACTIVEMODELCONFIG: ProjectsIdActiveModelConfig,
        PathValues.PROJECTS_ID_ACTIVEEXPERIMENT: ProjectsIdActiveExperiment,
        PathValues.PROJECTS_ID_FEEDBACKTYPES: ProjectsIdFeedbackTypes,
        PathValues.PROJECTS_ID_EXPORT: ProjectsIdExport,
        PathValues.APPS: Apps,
        PathValues.APPS_ID: AppsId,
        PathValues.APPS_ID_SESSIONS: AppsIdSessions,
        PathValues.SESSIONS: Sessions,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.SESSIONS_ID_EVENTS: SessionsIdEvents,
        PathValues.MODELCONFIGS: ModelConfigs,
        PathValues.MODELCONFIGS_ID: ModelConfigsId,
        PathValues.PROJECTS_PROJECT_ID_EXPERIMENTS: ProjectsProjectIdExperiments,
        PathValues.EXPERIMENTS_EXPERIMENT_ID: ExperimentsExperimentId,
        PathValues.EXPERIMENTS_EXPERIMENT_ID_MODELCONFIG: ExperimentsExperimentIdModelConfig,
    }
)

path_to_api = PathToApi(
    {
        PathValues.COMPLETION: Completion,
        PathValues.COMPLETIONDEPLOYED: CompletionDeployed,
        PathValues.COMPLETIONEXPERIMENT: CompletionExperiment,
        PathValues.COMPLETIONMODELCONFIG: CompletionModelConfig,
        PathValues.CHAT: Chat,
        PathValues.CHATDEPLOYED: ChatDeployed,
        PathValues.CHATEXPERIMENT: ChatExperiment,
        PathValues.CHATMODELCONFIG: ChatModelConfig,
        PathValues.LOGS: Logs,
        PathValues.FEEDBACK: Feedback,
        PathValues.PROJECTS: Projects,
        PathValues.PROJECTS_ID: ProjectsId,
        PathValues.PROJECTS_ID_MODELCONFIGS: ProjectsIdModelConfigs,
        PathValues.PROJECTS_ID_MODELCONFIG: ProjectsIdModelConfig,
        PathValues.PROJECTS_ID_ACTIVEMODELCONFIG: ProjectsIdActiveModelConfig,
        PathValues.PROJECTS_ID_ACTIVEEXPERIMENT: ProjectsIdActiveExperiment,
        PathValues.PROJECTS_ID_FEEDBACKTYPES: ProjectsIdFeedbackTypes,
        PathValues.PROJECTS_ID_EXPORT: ProjectsIdExport,
        PathValues.APPS: Apps,
        PathValues.APPS_ID: AppsId,
        PathValues.APPS_ID_SESSIONS: AppsIdSessions,
        PathValues.SESSIONS: Sessions,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.SESSIONS_ID_EVENTS: SessionsIdEvents,
        PathValues.MODELCONFIGS: ModelConfigs,
        PathValues.MODELCONFIGS_ID: ModelConfigsId,
        PathValues.PROJECTS_PROJECT_ID_EXPERIMENTS: ProjectsProjectIdExperiments,
        PathValues.EXPERIMENTS_EXPERIMENT_ID: ExperimentsExperimentId,
        PathValues.EXPERIMENTS_EXPERIMENT_ID_MODELCONFIG: ExperimentsExperimentIdModelConfig,
    }
)
