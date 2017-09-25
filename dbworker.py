import pg
from helpers import load_config, create_query_text
from helpers import create_query_text

error_message = "Параметры указаны не верно"
# CONFIG_PARAMS = load_config()
CONFIG_PARAMS = {'passwd': 'postgres',
                 'user': 'postgres',
                 'port': 5432,
                 'dbname': 'Blood',
                 'host': 'localhost'}


class Donor:
    """
    Поля таблицы:
    "id": int,
    "blood_type": smallint,
    "rhesus" boolean,
    "birth_date" date,
    "longitude" real,
    "latitude" real,
    """

    @staticmethod
    def new_donor(donor_info: dict):
        query_text = 'INSERT INTO "Donor" ({columns}) VALUES ({values})'
        columns, values_len, values = create_query_text(donor_info)
        query = query_text.format(columns=columns, values=values_len)
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(query, *values)

    @staticmethod
    def try_exist(user_id: int):
        query_text = 'SELECT EXISTS (SELECT 1 FROM "Donor" WHERE "id"=$1)'
        with pg.DB(**CONFIG_PARAMS) as conn:
            return conn.query(query_text, user_id).getresult()[0][0]

    @staticmethod
    def get_donor_data(user_id: int) -> tuple:
        query_text = 'SELECT * FROM "Donor" WHERE "id"=$1'
        with pg.DB(**CONFIG_PARAMS) as conn:
            return conn.query(query_text, user_id).getresult()[0]

    @staticmethod
    def update_with_data(donor_data: dict):
        if donor_data:
            query_text = 'UPDATE "Donor" SET ({columns}) = ({values}) WHERE "id" = ${user_param}'
            columns, values_len, values = create_query_text(donor_data)
            query_text = 'UPDATE "Donor" SET ({columns}) = ({values}) WHERE "id" = {user_param}'
            columns, values_len, values = create_query_text(donor_data)
            query = query_text.format(columns=columns, values=values_len, user_param=donor_data["donor_id"])
            with pg.DB(**CONFIG_PARAMS) as conn:
                conn.query(query, *values)


class Request:
    """
    Поля таблицы:
    "request_id" smallserial,
    "user_id" int,
    "need_blood_type" smallint,
    "need_rhesus" boolean,
    "post_date" date,
    "longitude" real,
    "latitude" real
    "registration_flag" boolean,
    "send_flag" boolean
    """

    @staticmethod
    def empty_request(user_id):
        query_text = 'SELECT "request_id" FROM "Request" WHERE "user_id"= $1 AND "registration_flag"=False'
        with pg.DB(**CONFIG_PARAMS) as conn:
            return conn.query(query_text, user_id).getresult()  # проверяй массив на пустоту для ответа

    @staticmethod
    def update_request(request_info, request_id):
        query_text = 'UPDATE "Request" SET ({columns}) = ({values}) WHERE "request_id" = ${request_param}'
        columns, values_len, values = create_query_text(request_info)
        query_text = 'UPDATE "Request" SET ({columns}) = ({values}) WHERE "request_id" = {request_param}'
        columns, values_len, values = create_query_text(request_info)
        query = query_text.format(columns=columns, values=values_len, request_param=request_id)
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(query, *values)

    @staticmethod
    def new_request(request_info: dict):
        empty_exist = Request.empty_request(request_info["user_id"])
        if empty_exist:
            Request.update_request(request_info, empty_exist[0][0])
            return empty_exist[0][0]  # возвращаю номер запроса

        else:
            query_text = 'INSERT INTO "Request" ({columns}) VALUES ({values}) RETURNING request_id'
            columns, values_len, values = create_query_text(request_info)
            query_text = 'INSERT INTO "Request" ({columns}) VALUES ({values})'
            columns, values_len, values = create_query_text(request_info)
            query = query_text.format(columns=columns, values=values_len)
            with pg.DB(**CONFIG_PARAMS) as conn:
                return conn.query(query, *values).getresult()[0][0]
                # return request_id
