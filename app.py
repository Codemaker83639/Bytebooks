from flask import Flask, render_template, request, redirect, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__, static_folder='Images')
app.secret_key = "fibonacci"

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

@app.route('/Nosotros')
def Nosotros():
    return render_template('Bytebooks/Nosotros.html')

@app.route('/Ranking')
def Ranking():
    return render_template('Bytebooks/Ranking.html')


@app.route('/Login')
def Bytebooks_login():
    return render_template('Bytebooks/Login.html')

@app.route('/Registro')
def Bytebooks_registro():
    return render_template('Bytebooks/Registro.html')





@app.route('/User/Nosotros')
def User_Nosotros():
    return render_template('User/Nosotros.html')

@app.route('/User/Ranking')
def User_Ranking():
    return render_template('User/Ranking.html')

@app.route('/User/Libros')
def UserLibros():
    return render_template('User/Libros.html')

@app.route('/User/')
def User_Index():
    return render_template('User/Index.html')






@app.route('/Admin/')
def Admin_Index():
    return render_template('Admin/Index.html')

@app.route('/Admin/Ranking')
def Admin_Ranking():
    return render_template('Admin/Ranking.html')







##Captura de los datos de usuario en registro:

@app.route('/Bytebooks/Registro', methods=['POST'])
def admin_registro01():
    # Obtener los datos del formulario
    _usuario = request.form['txtUsuario']
    _correo = request.form['txtCorreo']
    _password = request.form['txtPassword']

    # Validar que los campos no estén vacíos
    if not _usuario or not _correo or not _password:
        return render_template("Bytebooks/Registro.html", error="Todos los campos son obligatorios.")
    
    # Hashear la contraseña antes de guardarla
    hashed_password = generate_password_hash(_password)

    try:
        # Insertar datos en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario (nombre_usuario, correo, contrasena) VALUES (%s, %s, %s)",
                    (_usuario, _correo, hashed_password))
        mysql.connection.commit()
        cur.close()
        return redirect('/Login')  # Redirigir al inicio de sesión tras el registro
    except Exception as e:
        return render_template("Bytebooks/Registro.html", error=f"Error al registrar usuario: {e}")


@app.route('/Bytebooks/Login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']

    print(f"Datos recibidos - Usuario: {_usuario}, Contraseña: {_password}")

    # Verificar en la base de datos primero
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE nombre_usuario = %s", [_usuario])
        user = cur.fetchone()
        cur.close()

        # Si el usuario existe en la base de datos
        if user and check_password_hash(user[3], _password):  # user[3] es el hash de la contraseña
            session["login"] = True
            session["usuario"] = user[1]  # Guardar el nombre de usuario
            print("Inicio de sesión exitoso (base de datos)")
            return redirect("/")
        
        # Verificar usuarios predefinidos para el área administrativa
        elif (_usuario == "Fran" and _password == "123") or (_usuario == "Albert" and _password == "123"):
            session["login"] = True
            session["usuario"] = "Administrador"
            print("Inicio de sesión exitoso (administrador)")
            return redirect("/Admin")
        
        # Si ninguna de las opciones coincide
        else:
            print("Usuario o contraseña incorrectos")
            return render_template("Bytebooks/Login.html", error="Usuario o contraseña incorrectos.")
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")
        return render_template("Bytebooks/Login.html", error=f"Error al iniciar sesión: {e}")


@app.route('/Admin/Libros')
def Admin_Libros():
    # Ejemplo de consulta para verificar la conexión
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `libros`")
    libros = cur.fetchall()
    print(f"Libros disponibles: {libros}")
    cur.close()
    return render_template("Admin/Libros.html", Libros=libros)

@app.route('/Admin/Libros/guardar', methods=['POST'])
def Admin_Libros_guardar():
    _nombre = request.form['txtNombre']
    _url = request.form['txtUrl']
    _archivo = request.files['txtImagen']
    _categoria = request.form['txtCategoria']

    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M%S')

    if _archivo.filename != "":
        nuevoNombre = horaActual + _archivo.filename
        _archivo.save("Templates/Images/" + nuevoNombre)

    print(_nombre)
    print(_url)
    print(_archivo)
    print(_categoria)

    # Guardar datos en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO libros (nombre_libro, url, imagen, categoria) VALUES (%s, %s, %s, %s)", 
                (_nombre, _url, nuevoNombre, _categoria))
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
