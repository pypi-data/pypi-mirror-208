import typing_extensions

from humanloop.apis.tags import TagValues
from humanloop.apis.tags.projects_api import ProjectsApi
from humanloop.apis.tags.experiments_api import ExperimentsApi
from humanloop.apis.tags.completions_api import CompletionsApi
from humanloop.apis.tags.chats_api import ChatsApi
from humanloop.apis.tags.apps_api import AppsApi
from humanloop.apis.tags.sessions_api import SessionsApi
from humanloop.apis.tags.model_configurations_api import ModelConfigurationsApi
from humanloop.apis.tags.logs_api import LogsApi
from humanloop.apis.tags.feedback_api import FeedbackApi
from humanloop.apis.tags.authentication_api import AuthenticationApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.PROJECTS: ProjectsApi,
        TagValues.EXPERIMENTS: ExperimentsApi,
        TagValues.COMPLETIONS: CompletionsApi,
        TagValues.CHATS: ChatsApi,
        TagValues.APPS: AppsApi,
        TagValues.SESSIONS: SessionsApi,
        TagValues.MODEL_CONFIGURATIONS: ModelConfigurationsApi,
        TagValues.LOGS: LogsApi,
        TagValues.FEEDBACK: FeedbackApi,
        TagValues.AUTHENTICATION: AuthenticationApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.PROJECTS: ProjectsApi,
        TagValues.EXPERIMENTS: ExperimentsApi,
        TagValues.COMPLETIONS: CompletionsApi,
        TagValues.CHATS: ChatsApi,
        TagValues.APPS: AppsApi,
        TagValues.SESSIONS: SessionsApi,
        TagValues.MODEL_CONFIGURATIONS: ModelConfigurationsApi,
        TagValues.LOGS: LogsApi,
        TagValues.FEEDBACK: FeedbackApi,
        TagValues.AUTHENTICATION: AuthenticationApi,
    }
)
