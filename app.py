from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from flask import Flask, send_from_directory
from datetime import datetime



app = Flask(__name__,static_folder='Images')
app.secret_key="fibonacci"

@app.route('/Templates/Books/<path:filename>')
def download_file(filename):
    return send_from_directory('Templates/Books', filename)

# Ruta para servir imágenes desde Templates/Images
@app.route('/Templates/Images/<path:filename>')
def serve_images(filename):
    return send_from_directory('Templates/Images', filename)


# Configuración de conexión a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bytebooks'

# Inicializar la extensión MySQL
mysql = MySQL(app)

@app.route('/')
def inicio():
    return render_template('Bytebooks/index.html')

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
def admin_login():
    return render_template('Admin/Login.html')

@app.route('/Admin/Login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)


    if (_usuario=="Fran" and _password=="123") or (_usuario=="Albert" and _password=="123") :

        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/Admin")

    return render_template("Admin/Login.html")









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

    tiempo=datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _archivo.filename!="":
        nuevoNombre=horaActual+_archivo.filename
        _archivo.save("Templates/Images/"+nuevoNombre)
   
    print(_nombre)
    print(_url)
    print(_archivo)
    print(_categoria)

    # Guardar datos en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO libros (nombre_libro, url, imagen, categoria) VALUES (%s, %s, %s, %s)", (_nombre, _url, nuevoNombre,  _categoria))
    mysql.connection.commit()
    cur.close()

    return redirect('/Admin/Libros')


@app.route('/Admin/Libros/borrar', methods=['POST'])
def Admin_Libros_borrar():
    _id = request.form.get('txtID')  # ID recibido del formulario
    print(f"ID recibido para eliminar: {_id}")  # Para depuración

    if _id:
        cur = mysql.connection.cursor()
        try:
            # Cambia 'id' por 'id_libro' en las consultas
            cur.execute("SELECT * FROM `libros` WHERE id_libro=%s", (_id,))
            libro = cur.fetchone()
            if libro:
                # Si el libro existe, elimínalo
                cur.execute("DELETE FROM `libros` WHERE id_libro=%s", (_id,))
                mysql.connection.commit()
                print(f"Libro eliminado: {libro}")
            else:
                print("El libro no existe o ya fue eliminado.")
        except Exception as e:
            print(f"Error al eliminar el libro: {e}")
        finally:
            cur.close()
    return redirect('/Admin/Libros')

if __name__ == '__main__':
    app.run(debug=True)