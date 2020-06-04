from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_aantal_shocken():
        sql = "SELECT aantal_shocken from orders"
        return Database.get_rows(sql)

    @staticmethod
    def update_aantal_shocken(id, aantal_shocken):
        sql = "UPDATE orders SET aantal_shocken = %s WHERE idorder = %s"
        params = [aantal_shocken, id]
        return Database.execute_sql(sql, params)

    ###########################################################################

    @staticmethod
    def read_orders():
        sql = "SELECT * from orders"
        return Database.get_rows(sql)

    @staticmethod
    def read_order_by_id(id):
        sql = "SELECT * from orders WHERE idorder = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_order_start(id, starttime):
        sql = "UPDATE orders SET deliverystarttime = %s WHERE idorder = %s"
        params = [starttime, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_order_end(id, endtime):
        sql = "UPDATE orders SET deliveryendtime = %s WHERE idorder = %s"
        params = [endtime, id]
        return Database.execute_sql(sql, params)

    ###########################################################################

    @staticmethod
    def read_waypoints():
        sql = "SELECT * from waypoints"
        return Database.get_rows(sql)

    @staticmethod
    def read_waypoints_by_idorder(id):
        sql = "SELECT w.longitude, w.latitude from order_route as r inner join waypoints as w inner join orders as o WHERE o.idorder = %s and o.idorder = r.order_idorder and w.idwaypoint = r.waypoints_idwaypoint"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def insert_waypoint(id, longitude, latitude, avgspeed):
        sql = "INSERT INTO waypoints (`idwaypoint`, `longitude`, `latitude`, `avgspeed`) VALUES ('%s', '%s', '%s', '%s');"
        params = [id, longitude, latitude, avgspeed]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_waypoints_maxid():
        sql = "SELECT max(idwaypoint) as maxid FROM waypoints;"
        return Database.get_one_row(sql)

    ###########################################################################

    @staticmethod
    def update_status_alle_lampen(status):
        sql = "UPDATE lampen SET status = %s"
        params = [status]
        return Database.execute_sql(sql, params)
