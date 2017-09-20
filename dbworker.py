import pg
from helpers import load_config, prepared, quote2

error_message = "Параметры указаны не верно"
CONFIG_PARAMS = ""
# CONFIG_PARAMS = load_config()
CONFIG_PARAMS = {'passwd': 'postgres', 'user': 'postgres', 'port': 5432, 'dbname': 'Blood',
                 'host': 'localhost'}



class Donor():
    """
    Поля таблицы:
    "id": int,
	"goup": smallserial,
	"rhesus" boolean,
	"birth_date" date,
	"longitude" real,
	"latitude" real,
	"donor_flag" boolean
    """

    # def __init__(self, host='localhost', port=5432, username='postgres', password='postgres'):
    #     try:
    #         self.__connection = pg.DB(user=username,
    #                                   passwd=password,
    #                                   host=host,
    #                                   port=port,
    #                                   dbname='Blood')
    #
    #     except:
    #         print("База данных не подключена")

    def delete(user_id: int):
        del_query = 'DELETE FROM "Donor" WHERE "id" = $1'
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(del_query, user_id)

    def new_donor(donor_info: dict):
        keys = donor_info.keys()
        must_be = ("id", "goup", "rhesus", "birth_date")
        if any(param not in keys for param in must_be):
            raise error_message
        query_text = 'INSERT INTO "Donor" ({columns}) VALUES ({values})'
        ins_query = query_text.format(columns=', '.join(quote2(x) for x in keys),
                                      values=', '.join(prepared(len(keys))))
        vals = [donor_info[x] for x in keys]
        with pg.DB(**CONFIG_PARAMS) as conn:
            conn.query(ins_query, *vals)

    def try_exist(id: int):
        query_text = 'SELECT count(*) FROM Donor WHERE id =$'
        with pg.DB(**CONFIG_PARAMS) as conn:
            count = conn.query(query_text, id)
            if count != 0:
                return True
            else:
                return False

    def update_with_data(donor_id: int, donor_data: dict):
        if donor_data:
            query_text = 'UPDATE "Donor" SET ({columns}) = ({values}) WHERE "id" = ${user_param}'
            cols = donor_data.keys()
            upd_query = query_text.format(columns=', '.join(quote2(k) for k in cols),
                                          values=', '.join(prepared(len(cols))),
                                          user_param=len(cols) + 1)
            vals = [donor_data[k] for k in cols] + [donor_data]
            with pg.DB(**CONFIG_PARAMS) as conn:
                conn.query(upd_query, *vals)





class Request():
    """
    Поля таблицы:
    "id"int,
	"need_goup" smallserial,
	"need_rhesus" boolean,
	"post_date" date,
	"longitude" real,
	"latitude" real
	"request_flag" boolean
    """

    def new_request(request_info: dict):
        keys = request_info.keys()
        must_be = ("id", "birth_date")
        if any(param not in keys for param in must_be):
            raise error_message
        query_text = 'INSERT INTO "Request" ({columns}) VALUES ({values})'
        ins_query = query_text.format(columns=', '.join(quote2(x) for x in keys),
                                      values=', '.join(prepared(len(keys))))
        vals = [request_info[x] for x in keys]
        with pg.DB() as conn:
            conn.query(ins_query, *vals)
