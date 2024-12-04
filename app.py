from flask import Flask, render_template, request, redirect, session, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from datetime import datetime
import os
import re

app = Flask(__name__, static_folder='Images')
app.secret_key = "fibonacci"

# Configuración de conexión a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bytebooks'

# Inicializar la extensión MySQL
mysql = MySQL(app)

# --- Función para validar nombres de archivo seguros ---
def secure_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_.-]', '', filename)

# --- Rutas para servir archivos estáticos ---
@app.route('/Templates/Books/<path:filename>')
def download_file(filename):
    return send_from_directory('Templates/Books', filename)

@app.route('/Templates/Images/<path:filename>')
def serve_images(filename):
    return send_from_directory('Templates/Images', filename)

# --- Rutas Públicas ---
@app.route('/')
def inicio():
    return render_template('Bytebooks/index.html')

@app.route('/Nosotros')
def nosotros():
    return render_template('Bytebooks/Nosotros.html')

@app.route('/Ranking')
def ranking():
    return render_template('Bytebooks/Ranking.html')

@app.route('/Login')
def bytebooks_login():
    return render_template('Bytebooks/Login.html')

@app.route('/Registro')
def bytebooks_registro():
    return render_template('Bytebooks/Registro.html')

# --- Registro de nuevos usuarios ---
@app.route('/Bytebooks/Registro', methods=['POST'])
def admin_registro():
    _usuario = request.form['txtUsuario']
    _correo = request.form['txtCorreo']
    _password = request.form['txtPassword']

    if not _usuario or not _correo or not _password:
        return render_template("Bytebooks/Registro.html", error="Todos los campos son obligatorios.")

    hashed_password = generate_password_hash(_password)

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre_usuario, correo, contrasena) VALUES (%s, %s, %s)",
                    (_usuario, _correo, hashed_password))
        mysql.connection.commit()
        cur.close()
        return redirect('/Login')
    except Exception as e:
        return render_template("Bytebooks/Registro.html", error=f"Error al registrar usuario: {e}")

# --- Inicio de Sesión ---
@app.route('/Bytebooks/Login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usuario, nombre_usuario, correo, contrasena FROM usuario WHERE nombre_usuario = %s", [_usuario])
        user = cur.fetchone()
        cur.close()

        if user:
            user_id, nombre_usuario, correo, hashed_password = user
            if check_password_hash(hashed_password, _password):
                session["login"] = True
                session["usuario"] = nombre_usuario
                return redirect("/User/")
            else:
                return render_template("Bytebooks/Login.html", error="Usuario o contraseña incorrectos.")
        elif _usuario in ["Fran", "Albert"] and _password == "123":
            session["login"] = True
            session["usuario"] = "Administrador"
            return redirect("/Admin/")
        else:
            return render_template("Bytebooks/Login.html", error="Usuario o contraseña incorrectos.")
    except Exception as e:
        return render_template("Bytebooks/Login.html", error=f"Error al iniciar sesión: {e}")

# --- Rutas para Usuarios Registrados ---
@app.route('/User/')
def user_index():
    if not session.get("login"):
        return redirect("/Login")
    return render_template('User/Index.html')

@app.route('/User/Nosotros')
def user_nosotros():
    if not session.get("login"):
        return redirect("/Login")
    return render_template('User/Nosotros.html')

@app.route('/User/Ranking')
def user_ranking():
    if not session.get("login"):
        return redirect("/Login")
    return render_template('User/Ranking.html')

@app.route('/User/Libros')
def user_libros():
    if not session.get("login"):
        return redirect("/Login")
    return render_template('User/Libros.html')

# --- Rutas para Administradores ---
@app.route('/Admin/')
def admin_index():
    if not session.get("login") or session["usuario"] != "Administrador":
        return redirect("/Login")
    return render_template('Admin/Index.html')

@app.route('/Admin/Ranking')
def admin_ranking():
    if not session.get("login") or session["usuario"] != "Administrador":
        return redirect("/Login")
    return render_template('Admin/Ranking.html')

@app.route('/Admin/Libros')
def admin_libros():
    if not session.get("login") or session["usuario"] != "Administrador":
        return redirect("/Login")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM libros")
    libros = cur.fetchall()
    cur.close()
    return render_template("Admin/Libros.html", Libros=libros)

@app.route('/Admin/Libros/guardar', methods=['POST'])
def admin_libros_guardar():
    _nombre = request.form['txtNombre']
    _url = request.form['txtUrl']
    _archivo = request.files['txtImagen']
    _categoria = request.form['txtCategoria']

    if _archivo and _archivo.filename:
        filename = secure_filename(_archivo.filename)
        tiempo = datetime.now().strftime('%Y%H%M%S')
        nuevo_nombre = tiempo + '_' + filename
        _archivo.save(os.path.join("Templates/Images", nuevo_nombre))
    else:
        nuevo_nombre = None

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO libros (nombre_libro, url, imagen, categoria) VALUES (%s, %s, %s, %s)",
                (_nombre, _url, nuevo_nombre, _categoria))
    mysql.connection.commit()
    cur.close()
    return redirect('/Admin/Libros')

@app.route('/Admin/Libros/borrar', methods=['POST'])
def admin_libros_borrar():
    _id = request.form.get('txtID')

    if _id:
        cur = mysql.connection.cursor()
        cur.execute("SELECT imagen FROM libros WHERE id_libro = %s", (_id,))
        libro = cur.fetchone()

        if libro and libro[0]:
            imagen_path = os.path.join("Templates/Images", libro[0])
            if os.path.exists(imagen_path):
                os.remove(imagen_path)

        cur.execute("DELETE FROM libros WHERE id_libro = %s", (_id,))
        mysql.connection.commit()
        cur.close()
    return redirect('/Admin/Libros')

if __name__ == '__main__':
    app.run(debug=True)
