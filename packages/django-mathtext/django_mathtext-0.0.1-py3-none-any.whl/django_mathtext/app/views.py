"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
or
`python -m uvicorn app:app --reload --host localhost --port 7860`
"""

import json
import sentry_sdk
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from json import JSONDecodeError
from logging import getLogger
from mathactive_django.views import start_quiz
from mathtext.text2int import text2int
# from django_mathtext.constants import SENTRY_DSN
# from mathtext_scripts.nlu import evaluate_message_with_nlu
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.utils import BadDsn

log = getLogger(__name__)

try:
    sentry_sdk.init(
        dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
        # ...
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=False,
            ),
        ],
    )
except BadDsn:
    pass


@csrf_exempt
@require_http_methods(["POST"])
def text2int_ep(request):
    payload = json.loads(request.body)
    ml_response = text2int(payload["content"])
    content = {"message": ml_response}
    return JsonResponse(content)


@csrf_exempt
@require_http_methods(["POST"])
def evaluate_user_message_with_nlu_api(request):
    """ Calls nlu evaluation and returns the nlu_response

    Input
    - request.body: json - message data for the most recent user response

    Output
    - int_data_dict or sent_data_dict: dict - the type of NLU run and result
      {'type':'integer', 'data': '8', 'confidence': 0}
    """
    log.info(f'Received request: {request}')
    log.info(f'Request header: {request.headers}')
    payload = json.loads(request.body)
    # request_body = await request.body()
    log.info(f'Request body: {payload}')
    request_body_str = payload.decode()
    log.info(f'Request_body_str: {request_body_str}')

    try:
        # data_dict = await request.json()
        data_dict = json.loads(request.body)
    except JSONDecodeError:
        log.error(f'Request.json failed: {dir(request)}')
        data_dict = {}
    message_data = data_dict.get('message_data')

    if not message_data:
        log.error(f'Data_dict: {data_dict}')
        message_data = data_dict.get('message', {})
    nlu_response = evaluate_message_with_nlu(message_data)
    return JsonResponse(nlu_response)


@csrf_exempt
@require_http_methods(["POST"])
def num_one(request):
    """
    Input:
    {
        "user_id": 1,
        "message_text": 5,
    }
    Output:
    {
        'messages':
            ["Let's", 'practice', 'counting', '', '', '46...', '47...', '48...', '49', '', '', 'After', '49,', 'what', 'is', 'the', 'next', 'number', 'you', 'will', 'count?\n46,', '47,', '48,', '49'],
        'input_prompt': '50',
        'state': 'question'
    }
    """
    data_dict = json.loads(request.body)
    print(data_dict)
    user_id = data_dict["user_id"]
    message_text = data_dict["message_text"]
    res = start_quiz(request)
    print(res)
    # res = num_one_quiz.process_user_message(user_id, message_text)
    # print(res)
    return res
