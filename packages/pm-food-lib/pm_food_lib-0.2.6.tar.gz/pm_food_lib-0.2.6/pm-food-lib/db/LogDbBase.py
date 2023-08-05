from paketmutfak.utils.constants.error_codes import MessageCode
from paketmutfak.utils.functions.general import generate_uid
from paketmutfak.db.sql_db_base_class import PmMysqlBaseClass
from datetime import date
from flask import request
from enum import Enum
import json


class LogLevels(Enum):
    WARNING = 1
    ERROR = 2
    CRITICAL_ERROR = 3
    INFO = 4


def edit_request_headers(_headers):
    try:
        edited_headers = json.dumps({
            'SERVER_SOFTWARE': _headers.get('SERVER_SOFTWARE'),
            'REQUEST_METHOD': _headers.get('REQUEST_METHOD'),
            'QUERY_STRING': _headers.get('QUERY_STRING'),
            'REQUEST_URI': _headers.get('REQUEST_URI'),
            'REMOTE_ADDR': _headers.get('REMOTE_ADDR'),
            'REMOTE_PORT': _headers.get('REMOTE_PORT'),
            'SERVER_NAME': _headers.get('SERVER_NAME'),
            'SERVER_PORT': _headers.get('SERVER_PORT'),
            'SERVER_PROTOCOL': _headers.get('SERVER_PROTOCOL'),
            'HTTP_AUTHORIZATION': _headers.get('HTTP_AUTHORIZATION'),
            'HTTP_USER_AGENT': _headers.get('HTTP_USER_AGENT'),
            'HTTP_CACHE_CONTROL': _headers.get('HTTP_CACHE_CONTROL'),
            'HTTP_ACCEPT': _headers.get('HTTP_ACCEPT'),
            'HTTP_ACCEPT_ENCODING': _headers.get('HTTP_ACCEPT_ENCODING'),
            'HTTP_CONNECTION': _headers.get('HTTP_CONNECTION')
        })

    except (Exception,):
        return None
    else:
        return edited_headers


class LogRDS(PmMysqlBaseClass):
    """
                create a pool when connect mysql, which will decrease the time spent in
                request connection, create connection and close connection
                """

    def __init__(self, service_name):
        self.service_name = service_name

    def insert_log(self, _message: str, _func_name: str, _line_no: str = None,
                   _request: request = None, _query: str = None,
                   _level: LogLevels = LogLevels.ERROR):

        # Request
        headers = None
        full_path = None
        request_method = None
        user_agent = None
        base_url = None
        endpoint = None
        body = None

        query = None

        try:
            message = _message
            short_message = _message[:200]
            level = _level
            line_no = _line_no
            func_name = _func_name
            # INFO: inspect içerisinde fonksiyonların sıralı olarak çağrıldığı tüm fonksiyonlar var

            if _request:
                full_path = _request.full_path
                headers = edit_request_headers(request.headers.environ)
                request_method = _request.method
                user_agent = None
                base_url = _request.base_url
                endpoint = _request.path
                if type(_request.json) == dict:
                    body = json.dumps(_request.json)
                # json.dumps({
                #     "browser": _request.user_agent.browser,
                #     "language": _request.user_agent.language,
                #     "platform": _request.user_agent.platform,
                #     "version": _request.user_agent.version
                # }) if _request.user_agent else None

            if _query:
                query = _query

            conn, cursor = self.get_connection_conn_cursor()

            if type(conn) == dict and conn.get("status_code") == "BAD":
                respond_error_data = {'log_id': conn.get("log_id"),
                                      'message_code': MessageCode.UNEXPECTED_ERROR_ON_SERVICE_MESSAGE}

                return respond_error_data, 500

            insert_service_logs_query = "INSERT INTO Service_Logs (id, service_name, message, short_message, " \
                                        "func_name, line_no, headers, level, full_path, request_method, " \
                                        "user_agent, base_url, endpoint, query, body, `utc_date`) " \
                                        "VALUES (%(log_id)s, %(service_name)s , %(message)s, %(short_message)s, %(func_name)s, " \
                                        "%(line_no)s, %(headers)s, %(level)s, %(full_path)s, %(request_method)s, " \
                                        "%(user_agent)s, %(base_url)s, %(endpoint)s, %(query)s, %(body)s, %(utc_date)s);"

            log_id = generate_uid()
            utc_date = str(date.today())

            record_args = {
                'log_id': log_id,
                'service_name': self.service_name,
                'message': message,
                'short_message': short_message,
                'func_name': func_name,
                'line_no': line_no,
                'headers': headers,
                'level': level.name,
                'full_path': full_path,
                'request_method': request_method,
                'user_agent': user_agent,
                'base_url': base_url,
                'endpoint': endpoint,
                'query': query,
                'body': body,
                'utc_date': utc_date
            }

            respond_record = self.execute_without_commit(conn=conn, cursor=cursor, sql=insert_service_logs_query,
                                                         args=record_args)

            if type(respond_record) == dict and respond_record.get("status_code") == "BAD":
                if 'Duplicate entry' in respond_record.get('error_message'):
                    return str(respond_record.get('error_message')), 500
                return "Log Oluşturulamadı", 500

            commit_result = self.commit_without_execute(conn=conn, cursor=cursor)

            if type(commit_result) == dict and commit_result.get("status_code") == "BAD":
                return "Log Oluşturulamadı", 500

        except Exception as ex:
            return str(ex), 500
        else:
            return log_id, 200

    def get_service_name(self):
        return self.service_name
