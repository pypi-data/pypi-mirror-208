''' OpenAI API Connect '''
from enum import Enum
from typing import List
from requests import Session
from pydantic import BaseModel


class Role(str, Enum):
    ''' Role '''
    ASSISTANT = 'assistant'
    SYSTEM = 'system'
    USER = 'user'


class Message(BaseModel):
    ''' Message in chat format '''
    role: Role
    content: str

    class Config:
        use_enum_values = True


class TokenUsage(BaseModel):
    ''' Token usage '''
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class Choice(BaseModel):
    ''' choice '''
    finish_reason: str
    index: int
    message: Message


class RespCompletions(BaseModel):
    ''' Response of chat.completions'''
    id: str
    model: str
    object: str
    created: int
    usage: TokenUsage
    choices: list[Choice]


class OpenAIAPI(Session):
    ''' OpenAI API '''

    def __init__(self, token: str, organization: str | None) -> None:
        super().__init__()
        self.url = 'https://api.openai.com/v1'
        self.headers['Authorization'] = f'Bearer {token}'

        if organization:
            self.headers['OpenAI-Organization'] = organization

    def chat_completions(self,
                         messages: List[Message],
                         model: str = 'gpt-3.5-turbo',
                         temperature: int = 1,
                         n: int = 1,
                         user: str = 'api') -> RespCompletions:
        ''' chat completions '''
        data = {
            'model': model,
            'messages': [msg.dict() for msg in messages],
            'temperature': temperature,
            'n': n,
            'user': user,
        }
        return RespCompletions.parse_obj(
            self.post(self.url + '/chat/completions', json=data).json()
        )
