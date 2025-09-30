import mysql.connector as connector
import pandas as pd

# Global connection for reuse in multiple functions
global con, cur
con = connector.connect(
    host="localhost",
    port='3306',
    user="root",
    password="1234rayyan",
    database="hoteldatabase"
)
cur = con.cursor()

def get_connection():
    return connector.connect(
        host="localhost",
        port='3306',
        user="root",
        password="1234rayyan",
        database="hoteldatabase"
    )

def createTables():
    queries = [
        "CREATE TABLE customerdetails(cid INT PRIMARY KEY, cnic CHAR(20), cname CHAR(50), cage INT, phone CHAR(20), caddress CHAR(100), finalprice FLOAT, checkin DATE, checkout DATE);",
        "CREATE TABLE room(roomnum INT PRIMARY KEY, roomtypeid INT, size INT);",
        "CREATE TABLE roomtype(roomtypeid INT PRIMARY KEY, bednum INT, ac CHAR(10), rate FLOAT, description CHAR(200));",
        "CREATE TABLE roomservice(orderid INT PRIMARY KEY, itemid INT, quantity INT, rscid INT);",
        "CREATE TABLE items(itemid INT PRIMARY KEY, itemname CHAR(50), rate FLOAT);",
        "CREATE TABLE bookingdetails(bid INT PRIMARY KEY, cid INT, checkin DATE, checkout DATE, finalprice FLOAT);",
        "CREATE TABLE employees(empid INT PRIMARY KEY, cnic CHAR(20), ename CHAR(50), age INT, gender CHAR(10), roleid INT, sal FLOAT);",
        "CREATE TABLE roles(roleid INT PRIMARY KEY, rolename CHAR(50), sal FLOAT);"
    ]
    for query in queries:
        cur.execute(query)
        print("OK", query)

def addDefaultValues():
    queries = [
        "INSERT INTO customerdetails VALUES(100,'123456789101','Haris Hussain',23,'3158145161','#77, 1st Main, Malir, Pakistan',1500,'2025-12-12','2025-12-13');",
        "INSERT INTO roles VALUES(10,'Manager',95000);",
        "INSERT INTO employees VALUES(11,'123456789101','Sameer Ahmed',21,'Male',10,95000);",
        "INSERT INTO items VALUES(1,'Chocolate Ice Cream',150);",
        "INSERT INTO roomtype VALUES(1,2,'AC',2500,'Comfortable double room with AC, two single beds, a wardrobe and an outward facing window');",
        "INSERT INTO room VALUES(188,1,268);",
        "INSERT INTO roomservice VALUES(1768,1,3,100);",
        "INSERT INTO bookingdetails VALUES(1327,100,'2025-12-12','2025-12-13',1950);"
    ]
    for query in queries:
        cur.execute(query)
        con.commit()
        print("OK", query)

def addForeignKeys():
    queries = [
        "ALTER TABLE room ADD FOREIGN KEY (roomtypeid) REFERENCES roomtype(roomtypeid) ON UPDATE CASCADE ON DELETE CASCADE",
        "ALTER TABLE roomservice ADD FOREIGN KEY (itemid) REFERENCES items(itemid) ON UPDATE CASCADE ON DELETE CASCADE",
        "ALTER TABLE bookingdetails ADD FOREIGN KEY (cid) REFERENCES customerdetails(cid) ON UPDATE CASCADE ON DELETE CASCADE",
        "ALTER TABLE employees ADD FOREIGN KEY (roleid) REFERENCES roles(roleid) ON UPDATE CASCADE ON DELETE CASCADE",
        "ALTER TABLE roomservice ADD FOREIGN KEY (rscid) REFERENCES customerdetails(cid)"
    ]
    for query in queries:
        cur.execute(query)
        con.commit()
        print("OK", query)

def addCustDetails(cnic, cname, cage, phone, caddress, finalprice, checkin, checkout):
    query = 'SELECT cid FROM customerdetails ORDER BY cid DESC LIMIT 1'
    cur.execute(query)
    for row in cur:
        cid = int(row[0])
    cid += 10
    query = f"INSERT INTO customerdetails VALUES({cid}, '{cnic}', '{cname}', {cage}, '{phone}', '{caddress}', {finalprice}, '{checkin}', '{checkout}')"
    cur.execute(query)
    con.commit()
    return cid

def addEmployeeDetails(empid, cnic, ename, age, gender, roleid):
    query = f"SELECT sal FROM roles WHERE roleid = {roleid}"
    cur.execute(query)
    for row in cur:
        sal = float(row[0])
    query = f"INSERT INTO employees VALUES({empid}, '{cnic}', '{ename}', {age}, '{gender}', {roleid}, {sal})"
    cur.execute(query)
    con.commit()

def addItem(itemid, itemname, itemrate):
    query = f"INSERT INTO items VALUES({itemid}, '{itemname}', {itemrate})"
    cur.execute(query)
    con.commit()

def addRole(roleid, rolename, rolesal):
    query = f"INSERT INTO roles VALUES({roleid}, '{rolename}', {rolesal})"
    cur.execute(query)
    con.commit()

def addRoomType(roomtypeid, bednum, ac, roomrate, desc):
    query = f"INSERT INTO roomtype VALUES({roomtypeid}, {bednum}, '{ac}', {roomrate}, '{desc}')"
    cur.execute(query)
    con.commit()

def addRoomService(itemid, quantity, rscid):
    query = 'SELECT orderid FROM roomservice ORDER BY orderid DESC LIMIT 1'
    cur.execute(query)
    for row in cur:
        orderid = int(row[0])
    orderid += 10
    query = f"INSERT INTO roomservice VALUES({orderid}, {itemid}, {quantity}, {rscid})"
    cur.execute(query)
    con.commit()

def addRoom(roomnum, roomid, size):
    query = f"INSERT INTO room VALUES({roomnum}, {roomid}, {size})"
    cur.execute(query)
    con.commit()

def addBookingDetails(cid, totalamt):
    query = 'SELECT bid FROM bookingdetails ORDER BY bid DESC LIMIT 1'
    cur.execute(query)
    for row in cur:
        bid = int(row[0])
    bid += 10
    query = f"SELECT checkin FROM customerdetails WHERE cid = {cid}"
    cur.execute(query)
    for row in cur:
        checkin = row[0]
    query = f"SELECT checkout FROM customerdetails WHERE cid = {cid}"
    cur.execute(query)
    for row in cur:
        checkout = row[0]
    query = f"INSERT INTO bookingdetails VALUES({bid}, {cid}, '{checkin}', '{checkout}', {totalamt})"
    cur.execute(query)
    con.commit()

# ✅ Fixed: Avoids ambiguous 'checkin' column
def getBookingHistory():
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT checkin FROM bookingdetails"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    df = pd.DataFrame(rows, columns=["BookingDate"])
    df["BookingDate"] = pd.to_datetime(df["BookingDate"])
    return df

def getRoomBaseRate(roomtype_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT Rate FROM roomtype WHERE RoomTypeID = %s"
    cursor.execute(query, (roomtype_id,))
    rate = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return rate

def getFinalAmount(cid):
    query1 = f"SELECT finalprice FROM customerdetails WHERE cid={cid}"
    cur.execute(query1)
    for row1 in cur:
        p1 = float(row1[0])
    query2 = f"""
        SELECT SUM(items.rate * roomservice.quantity) AS total_price
        FROM roomservice
        JOIN items ON roomservice.itemid = items.itemid
        WHERE roomservice.rscid = {cid}
    """
    cur.execute(query2)
    for row2 in cur:
        try:
            p2 = float(row2[0])
        except TypeError:
            p2 = 0
        else:
            p2 = float(row2[0])
    return p1 + p2

def getRoomType(roomtypeid):
    query = f"SELECT * FROM roomtype WHERE roomtypeid={roomtypeid}"
    cur.execute(query)
    for row in cur:
        return row

def selectRoom(roomtypeid, checkin, checkout):
    query = f"SELECT rate FROM roomtype WHERE roomtypeid={roomtypeid}"
    cur.execute(query)
    for row in cur:
        rate = int(row[0])
    delta = checkout - checkin
    totalprice = rate * delta.days
    return totalprice

def getCustDetails(cid):
    query = f"SELECT * FROM customerdetails WHERE cid={cid}"
    cur.execute(query)
    for row in cur:
        return row

def getAllItems():
    query = pd.read_sql_query('SELECT * FROM items', con)
    df = pd.DataFrame(query, columns=['itemid', 'itemname', 'rate'])
    return df

def getAllRoles():
    query = pd.read_sql_query('SELECT * FROM roles', con)
    df = pd.DataFrame(query, columns=['roleid', 'rolename', 'sal'])
    return df

def getAllEmployees():
    query = pd.read_sql_query('SELECT * FROM employees', con)
    df = pd.DataFrame(query, columns=['empid', 'ename', 'cnic', 'age', 'gender', 'roleid', 'sal'])
    return df

def getAllRooms():
    query = pd.read_sql_query('SELECT * FROM room', con)
    df = pd.DataFrame(query, columns=['roomnum', 'roomtypeid', 'size'])
    return df

def getAllRoomTypes():
    query = pd.read_sql_query('SELECT * FROM roomtype', con)
    df = pd.DataFrame(query, columns=['roomtypeid', 'bednum', 'ac', 'rate', 'description'])
    return df

def getAllBookingDetails():
    query = pd.read_sql_query('SELECT * FROM bookingdetails', con)
    df = pd.DataFrame(query, columns=['bid', 'cid', 'checkin', 'checkout', 'finalprice'])
    return df

def getAllCustomerDetails():
    query = pd.read_sql_query('SELECT * FROM customerdetails', con)
    df = pd.DataFrame(query, columns=['cid', 'cnic', 'cname', 'cage', 'phone', 'caddress', 'finalprice', 'checkin', 'checkout'])
    return df

def getAllOrders():
    query = pd.read_sql_query('SELECT * FROM roomservice', con)
    df = pd.DataFrame(query, columns=['orderid', 'itemid', 'quantity', 'rscid'])
    return df
