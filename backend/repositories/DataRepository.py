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
        sql = "SELECT aantal_shocken FROM orders"
        return Database.get_rows(sql)

    @staticmethod
    def read_aantal_shocken_by_idorder(id):
        sql = "SELECT aantal_shocken FROM orders WHERE idorder = %s"
        params = [id]
        return Database.get_one_row(sql, params)

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
    def read_ordered_products_by_id(id):
        sql = "SELECT o.idorder, p.name, c.name, i.amount from project_1.order_items as i inner join project_1.products as p inner join project_1.category as c inner join project_1.orders as o WHERE o.idorder = %s and o.idorder = i.orders_idorder and p.idproduct = i.products_idproduct and c.idcategory = i.products_category_idcategory"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_order_cost_by_id(id):
        sql = "SELECT o.idorder, sum(p.price * i.amount) as price from project_1.order_items as i inner join project_1.products as p inner join project_1.category as c inner join project_1.orders as o WHERE o.idorder = %s and o.idorder = i.orders_idorder and p.idproduct = i.products_idproduct and c.idcategory = i.products_category_idcategory group by o.idorder"
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

    @staticmethod
    def read_order_maxid():
        sql = "SELECT max(idorder) as maxid FROM orders;"
        return Database.get_one_row(sql)

    @staticmethod
    def create_order(id, adress, ordertime):
        sql = "INSERT INTO orders (idorder, adress, ordertime, idstep) VALUES (%s, %s, %s, 1);"
        params = [id, adress, ordertime]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_order_item(orderid, productid, categoryid, amount):
        sql = "INSERT INTO order_items (orders_idorder, products_idproduct, products_category_idcategory, amount) VALUES (%s, %s, %s, %s);"
        params = [orderid, productid, categoryid, amount]
        return Database.execute_sql(sql, params)

    @staticmethod
    def create_order_route(orderid, waypointid):
        sql = "INSERT INTO order_route (order_idorder, waypoints_idwaypoint) VALUES (%s, %s);"
        params = [orderid, waypointid]
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
        return Database.get_rows(sql, params)

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
    def read_products():
        sql = "SELECT p.idproduct, p.name, p.price, p.description, p.instock, c.name as category FROM products as p inner join category as c where p.category_idcategory = c.idcategory;"
        return Database.get_rows(sql)

    @staticmethod
    def get_category_by_idproduct(id):
        sql = "SELECT c.idcategory as idcategory FROM products as p inner join category as c where p.category_idcategory = c.idcategory and p.idproduct = %s;"
        params = [id]
        return Database.get_one_row(sql, params)

    ###########################################################################

    @staticmethod
    def update_status_alle_lampen(status):
        sql = "UPDATE lampen SET status = %s"
        params = [status]
        return Database.execute_sql(sql, params)
