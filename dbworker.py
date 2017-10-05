import pg
from helpers import load_config, create_query_text
from config import connect_data as CONFIG_PARAMS

error_message = "Параметры указаны не верно"


# CONFIG_PARAMS = load_config()



class Donor:
    """
    Поля таблицы:
    "id": int,
    "blood_type": smallint,
    "rhesus": boolean,
    "birth_date": date,
    "longitude": real,
    "latitude": real,
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
        query_text = 'SELECT EXISTS (SELECT 1 FROM "Donor" WHERE "id" = $1)'
        with pg.DB(**CONFIG_PARAMS) as conn:
            return conn.query(query_text, user_id).getresult()[0][0]

    @staticmethod
    def get_donor_data(user_id: int) -> tuple:
        """
        использовать только если донор есть в базе 
        :param user_id: 
        :return: неизменяймый список типа:
                            (id(int),
                            blood_type(smallint), 
                            rhesus(1/0),
                            birth_date(datetime.date(1994, 12, 07)),
                            longitude(real),
                            latitude(real))
        """
        query_text = 'SELECT * FROM "Donor" WHERE "id" = $1'
        with pg.DB(**CONFIG_PARAMS) as conn:
            return conn.query(query_text, user_id).getresult()[0]

    @staticmethod
    def update_with_data(user_id: int, donor_data: dict):
        if donor_data:
            query_text = 'UPDATE "Donor" SET ({columns}) = ({values}) WHERE "id" = ${user_param}'
            columns, values_len, values = create_query_text(donor_data)
            values.append(user_id)
            query = query_text.format(columns=columns, values=values_len, user_param=len(values))
            with pg.DB(**CONFIG_PARAMS) as conn:
                conn.query(query, *values)


class Request:
    """
    Поля таблицы:
    "request_id" smallserial,
	"user_id" int,
	"phone_number" text,
	"need_blood_type" smallint,
	"need_rhesus" boolean,
	"message" text,
	"post_date" timestamp,
	"longitude" real,
	"latitude" real,
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
        values.append(request_id)
        query = query_text.format(columns=columns, values=values_len, request_param=len(values))
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(query, *values)

    @staticmethod
    def new_request(request_info: dict):
        query_text = 'INSERT INTO "Request" ({columns}) VALUES ({values}) ON CONFLICT (request_id) DO UPDATE SET ({columns}) = ({values}) RETURNING request_id'
        columns, values_len, values = create_query_text(request_info)
        query = query_text.format(columns=columns, values=values_len)
        with pg.DB(**CONFIG_PARAMS) as conn:
            return conn.query(query, *values).getresult()[0][0]

        # empty_exist = Request.empty_request(request_info["user_id"])
        # if empty_exist:
        #     Request.update_request(request_info, empty_exist[0][0])
        #     return empty_exist[0][0]  # возвращаю номер запроса
        #
        # else:
        #     query_text = 'INSERT INTO "Request" ({columns}) VALUES ({values}) RETURNING request_id'
        #     columns, values_len, values = create_query_text(request_info)
        #     query = query_text.format(columns=columns, values=values_len)
        #     with pg.DB(**CONFIG_PARAMS) as conn:
        #         return conn.query(query, *values).getresult()[0][0]
