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
# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True ,port=5001)