from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuración de conexión a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bytebooks'

# Inicializar la extensión MySQL
mysql = MySQL(app)

@app.route('/')
def inicio():
    return render_template('Bytebooks/Index.html')

@app.route('/Libros')
def Libros():
    return render_template('Bytebooks/Libros.html')

@app.route('/Nosotros')
def Nosotros():
    return render_template('Bytebooks/Nosotros.html')

@app.route('/Admin/')
def Admin_Index():
    return render_template('Admin/Index.html')

@app.route('/Login')
def Admin_Login():
    return render_template('Admin/Login.html')

@app.route('/Admin/Libros')
def Admin_Libros():

    # Ejemplo de consulta para verificar la conexión
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `libros`")
    libros = cur.fetchall()
    print(f"MySQL version: {libros[0]}")
    cur.close()
    return render_template("Admin/Libros.html", Libros=libros)


@app.route('/Admin/Libros/guardar', methods=['POST'])
def Admin_Libros_guardar():
    _nombre = request.form['txtNombre']
    _url = request.form['txtUrl']
    _archivo = request.files['txtImagen']
    _categoria = request.form['txtCategoria']
   
    print(_nombre)
    print(_url)
    print(_archivo)
    print(_categoria)

    # Guardar datos en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO libros (nombre_libro, url, imagen, categoria) VALUES (%s, %s, %s, %s)", (_nombre, _url, _archivo.filename,  _categoria))
    mysql.connection.commit()
    cur.close()

    return redirect('/Admin/Libros')

@app.route('/Admin/Libros/borrar', methods=['POST'])
def Admin_Libros_borrar():
    _id = request.form['txtId']
    print(_id)

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `libros`  WHERE id=%s",(_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id=%s",(_id))
    conexion.commit()

    return redirect('/Admin/Libros')

if __name__ == '__main__':
    app.run(debug=True)
