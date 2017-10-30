from llibs import pg
from helpers import create_query_text
from config import connect_data as CONFIG_PARAMS

error_message = "Параметры указаны не верно"


class Donor:
    """
    Поля таблицы:
    "id": int,
    "blood_type": smallint,
    "rhesus": boolean,
    "location" GEOMETRY
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

    @staticmethod
    def insert_donor_geo(user_id, longitude, latitude):
        query_text = """UPDATE "Donor" SET ("location") = ('POINT({longitude} {latitude})') WHERE "id" = $1"""
        query = query_text.format(longitude=longitude, latitude=latitude)
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(query, user_id)


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
    "location" GEOMETRY
    "registration_flag" boolean,
    "send_flag" boolean
    """

    # @staticmethod
    # def empty_request(user_id):
    #     query_text = 'SELECT "request_id" FROM "Request" WHERE "user_id"= $1 AND "registration_flag" is False'
    #     with pg.DB(**CONFIG_PARAMS) as conn:
    #         return conn.query(query_text, user_id).getresult()  # проверяй массив на пустоту для ответа

    @staticmethod
    def update_request(request_info, user_id):
        query_text = '''
        UPDATE "Request"
        SET ({columns}) = ({values})
        WHERE "user_id" = ${user_id}
        AND "registration_flag" Is FALSE
        '''
        columns, values_len, values = create_query_text(request_info)
        values.append(user_id)
        query = query_text.format(columns=columns, values=values_len, user_id=len(values))
        print(query)
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(query, *values)

    @staticmethod
    def insert_request_geo(user_id, longitude, latitude):
        query_text = """UPDATE "Request" SET ("location") = ('POINT({longitude} {latitude})') WHERE "id" = $1"""
        query = query_text.format(longitude=longitude, latitude=latitude)
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(query, user_id)

    @staticmethod
    def upsert_request(request_info: dict):
        query_text = '''
        INSERT INTO "Request" ({columns})
        VALUES ({values})
        ON CONFLICT ("user_id")
        WHERE "registration_flag" Is FALSE
        DO UPDATE SET ({columns}) = ({values})'''
        columns, values_len, values = create_query_text(request_info)
        query = query_text.format(columns=columns, values=values_len)
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(query, *values)
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


def test():
    requests = get_requests()
    for x in requests:
        blood_type = x[1]
        need_rhesus = x[2]
        geo = x[3]
        answer_on_request(blood_type, need_rhesus, geo)


def answer_on_request(blood_type, need_rhesus, geo):
    query_text = '''SELECT * FROM "Donor" 
                        WHERE ST_DWithin("location", '{geo}',100000)
                        AND "blood_type" = ANY($1::INTEGER[])'''
    query = query_text.format(geo=geo)
    if not need_rhesus:
        query += '''AND "rhesus" = False'''
    if blood_type == 3:
        need = {1, 3}
    else:
        need = set(range(1, blood_type + 1))
    with pg.DB(**CONFIG_PARAMS) as conn:
        print(conn.query(query, need).getresult())


def get_requests():
    query_text = """SELECT "request_id","need_blood_type", "need_rhesus", "location" 
                    FROM "Request" WHERE "send_flag" IS FALSE 
                    AND "registration_flag" IS TRUE"""
    with pg.DB(**CONFIG_PARAMS) as conn:
        return conn.query(query_text).getresult()

        # def answer_on_request(blood_type, need_rhesus, geo):
        #     query_text = '''SELECT * FROM "Donor"
        #                     WHERE ST_DWithin(ST_GeometryFromText({geo}), ST_GeometryFromText("location"),100000)
        #                     AND "blood_type" = ANY($1::INTEGER[])'''
        #     query = query_text.format(geo=geo)
        #     if not need_rhesus:
        #         query += '''AND "rhesus" = False'''
        #     if blood_type == 3:
        #         need = {1, 3}
        #     else:
        #         need = set(range(1, blood_type + 1))
        #     with pg.DB(**CONFIG_PARAMS) as conn:
        #         return conn.query(query, need).getresult()
