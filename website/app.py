from flask import Flask, render_template, request, session, redirect, url_for
from py2neo import Graph, Node




# Cấu hình Neo4j
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Neo4j connection
graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))
# Trang đăng nhập
@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')
# Xử lý đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def do_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        router = graph.nodes.match("Router", username=username, password=password).first()
        if router:
            # Lưu thông tin người dùng vào session
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login_fail.html')
    
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        username = session['username']
        info_wifi = []
        query = """
        MATCH (w:Wifi)-[:Locatted_at]->(c:Class)
        RETURN c.name AS name, w.ssid AS ssid, w.password AS password, w.ip_address AS ip_address, w.mac_address AS mac_address, w.speed AS speed

        """
        result = graph.run(query)
        for record in result:
            info_wifi.append(dict(record))
        return render_template('home.html',username=username, info_wifi=info_wifi)
    else:
        return redirect(url_for('login'))
@app.route('/wifi/<wifi_ip>')
def get_wifi_detail(wifi_ip):
    wifi_details = get_wifi(wifi_ip)
    if wifi_details:
        return render_template('wifi_detail.html', wifi_details=wifi_details )
    else:
        return "wifi not found"

def get_wifi(wifi_ip):
    query = """
    MATCH (w:Wifi)
    WHERE w.ip_address = $wifi_ip
    RETURN w.ssid AS ssid, w.password AS password, w.ip_address AS ip_address, w.mac_address AS mac_address, w.speed AS speed

    """
    result = graph.run(query, wifi_ip = wifi_ip).data()
    if result:
        wifi_details = result[0]
        return wifi_details
    else:
        return None
@app.route('/search', methods=['GET'])

def search_wifi():
    class_name = request.args.get('class_name', '').upper()
    wifi_details = get_wifi_class(class_name)
    if wifi_details:
        return render_template('info_search.html', wifi_details=wifi_details, class_name=class_name)
    else:
        return render_template('search_fail.html')

def get_wifi_class(class_name):
    query = """
    MATCH (w:Wifi)-[:Locatted_at]->(c:Class)
    WHERE c.name = $class_name
    RETURN w.ssid AS ssid, w.password AS password, w.ip_address AS ip_address, w.mac_address AS mac_address, w.speed AS speed

    """
    result = graph.run(query, class_name=class_name)
    wifi_details = [dict(record) for record in result]
    return wifi_details
#Thay đổi tên wifi
@app.route('/wifi/change_ssid/<wifi_ip>', methods=['GET','POST'])

def change_wifi_ssid(wifi_ip):
    if request.method == 'POST':
        new_ssid = request.form['new_ssid']

        query = """
        MATCH (w:Wifi)
        WHERE w.ip_address = $wifi_ip
        RETURN w
        """
        result = graph.run(query,wifi_ip=wifi_ip).data()

        if not result:
            return "wifi not found"
        
        query = """
        MATCH (w:Wifi)
        WHERE w.ip_address = $wifi_ip
        SET w.ssid=$new_ssid

        """
        graph.run(query, wifi_ip=wifi_ip, new_ssid=new_ssid)

        wifi_details = get_wifi_change_ssid(wifi_ip)
        if wifi_details:
            return render_template('wifi_detail.html', wifi_details=wifi_details, wifi_ip=wifi_ip)
        else:
            return "wifi not found"
    return render_template('change_ssid.html', wifi_ip=wifi_ip)

def get_wifi_change_ssid(wifi_ip):
    query = """
    MATCH (w:Wifi)
    WHERE w.ip_address= $wifi_ip
    RETURN w.ssid AS ssid, w.password AS password, w.ip_address AS ip_address, w.mac_address AS mac_address, w.speed AS speed

    """
    result = graph.run(query, wifi_ip = wifi_ip)
    record = result.data()
    if record:
        wifi_details = record[0]
        return wifi_details
    else:
        return None   
#thay đổi mật khẩu wifi
@app.route('/wifi/change_password/<wifi_ip>', methods=['GET', 'POST'])

def change_wifi_pass(wifi_ip):
    if request.method == 'POST':# xử lý dữ liệu đã được nhập từ form thay đổi mật khẩu
        new_password = request.form['new_password']

        query = """
        MATCH (w:Wifi)
        WHERE w.ip_address = $wifi_ip
        RETURN w
        """
        result = graph.run(query,wifi_ip=wifi_ip).data()

        if not result:
            return "wifi not found"
        
        query = """
        MATCH (w:Wifi)
        WHERE w.ip_address = $wifi_ip
        SET w.password = $new_password

        """
        graph.run(query, wifi_ip=wifi_ip, new_password=new_password)

        wifi_details = get_wifi_change_pass(wifi_ip)
        if wifi_details:
            return render_template('wifi_detail.html', wifi_details=wifi_details, wifi_ip=wifi_ip)
        else:
            return "wifi not found"
    return render_template('chang_pass.html', wifi_ip=wifi_ip)# yêu cầu không là post thì trả về form thay đổi mật khẩu 

def get_wifi_change_pass(wifi_ip):
    query = """
    MATCH (w:Wifi)
    WHERE w.ip_address= $wifi_ip
    RETURN w.ssid AS ssid, w.password AS password, w.ip_address AS ip_address, w.mac_address AS mac_address, w.speed AS speed

    """
    result = graph.run(query, wifi_ip = wifi_ip)
    record = result.data()
    if record:
        wifi_details = record[0]
        return wifi_details
    else:
        return None
@app.route('/wifi/delete_password/<wifi_ip>', methods=['GET','POST'])

def delete_wifi_password(wifi_ip):
    query = """
    MATCH (w:Wifi)
    WHERE w.ip_address = $wifi_ip
    RETURN w
    """
    result = graph.run(query, wifi_ip=wifi_ip).data()

    if not result:
        return "wifi not found"
    query ="""
    MATCH (w:Wifi)
    WHERE w.ip_address = $wifi_ip
    REMOVE w.password
    """

    graph.run(query, wifi_ip=wifi_ip)

    wifi_details = get_wifi_delete_pass(wifi_ip)
    if wifi_details:
        return render_template('wifi_detail.html', wifi_details=wifi_details, wifi_ip=wifi_ip)
    else:
        return "wifi not found"

def get_wifi_delete_pass(wifi_ip):
    query = """
    MATCH (w:Wifi)
    WHERE w.ip_address= $wifi_ip
    RETURN w.ssid AS ssid, w.password AS password, w.ip_address AS ip_address, w.mac_address AS mac_address, w.speed AS speed

    """
    result = graph.run(query, wifi_ip = wifi_ip)
    record = result.data()
    if record:
        wifi_details = record[0]
        return wifi_details
    else:
        return None
@app.route('/wifi/add', methods=['GET', 'POST'])

def add_wifi():
    if request.method == 'POST':#gửi yêu cầu post cập nhật dữ liệu 
        name_class = request.form['name_class']
        ssid = request.form['ssid']
        wifi_type = request.form['wifi_type']  # Loại Wi-Fi (wifi_pass hoặc wifi_free)

        if wifi_type == 'wifi_pass':
            password = request.form['password']  # Chỉ lấy mật khẩu nếu là Wi-Fi có mật khẩu
        else:
            password = None
        ip_address = request.form['ip_address']
        mac_address = request.form['mac_address']
        speed = request.form['speed']
        
        
        # Thêm Wi-Fi mới vào cơ sở dữ liệu Neo4j
        query_wifi = """
        CREATE (w:Wifi {
        ssid: $ssid,
        password: $password,
        ip_address: $ip_address,
        mac_address: $mac_address,
        speed: $speed })
        """
        graph.run(query_wifi, ssid=ssid, password=password, ip_address=ip_address, mac_address=mac_address, speed=speed)
        query_class ="""
        CREATE (:Class{name: $name_class})
        """
        graph.run(query_class, name_class=name_class)

        # Tạo mối quan hệ CONNECTED_TO giữa Wi-Fi và router (trong đây mình sẽ gán router cố định với mã 'router01', bạn có thể sửa thành router cụ thể)
        connect_query = """
        MATCH (w:Wifi {mac_address: $mac_address})
        MATCH (r:Router)
        CREATE (w)-[:Connect]->(r)
        """
        graph.run(connect_query, mac_address=mac_address)

        # Tạo mối quan hệ INSTALLED_IN giữa Wi-Fi và lớp học (trong đây mình sẽ gán lớp học cố định với tên 'Lớp học A', bạn có thể sửa thành tên lớp học cụ thể)
        Locatted_query = """
        MATCH (w:Wifi {mac_address: $mac_address})
        MATCH (c:Class {name: $name_class})
        CREATE (w)-[:Locatted_at]->(c)
        """
        graph.run(Locatted_query,name_class=name_class, mac_address=mac_address)

        return redirect(url_for('home'))  # Chuyển hướng về trang home sau khi cập nhật thành công

    return render_template('wifi_config.html')
@app.route('/wifi/<wifi_ip>/delete', methods=['GET', 'POST'])
def delete_wifi_and_class(wifi_ip):
    if request.method == 'POST':# yêu cầu cập nhật dữ liệu gửi đi là post

        # Xóa wifi và mối quan hệ CONNECTED_TO trong cơ sở dữ liệu Neo4j
        delete_connect_query = """
        MATCH (w:Wifi {ip_address: $wifi_ip})-[c:Connect]->(r:Router)
        DELETE c
        """
        graph.run(delete_connect_query, wifi_ip=wifi_ip)

        # Xóa lớp học chứa wifi và mối quan hệ INSTALLED_IN trong cơ sở dữ liệu Neo4j
        delete_loccated_query = """
        MATCH (w:Wifi {ip_address: $wifi_ip})-[r:Locatted_at]->(c:Class)
        DELETE r
        """
        graph.run(delete_loccated_query, wifi_ip=wifi_ip)

        # Xóa wifi trong cơ sở dữ liệu Neo4j
        delete_wifi_query = """
        MATCH (w:Wifi {ip_address: $wifi_ip})
        DELETE w
        """
        graph.run(delete_wifi_query, wifi_ip=wifi_ip)

        delete_class_query = """
        MATCH (c:Class)
        WHERE NOT (c)--()
        DELETE c
        """
        graph.run(delete_class_query)
        return redirect(url_for('home'))  
    return render_template('delete.html', wifi_ip=wifi_ip)
        
@app.route('/delete/<wifi_ip>')
def delete(wifi_ip):
    # Trả về trang delete.html và truyền thông tin wifi_ip cho trang đó
    return render_template('delete.html', wifi_ip=wifi_ip)
# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True ,port=5001)