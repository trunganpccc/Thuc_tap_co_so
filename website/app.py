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