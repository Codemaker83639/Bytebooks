from flask import Flask
from flask import render_template, request, redirect

app=Flask (__name__) 

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
    return render_template('Admin/Libros.html')

@app.route('/Admin/Libros/guardar', methods=['POST']) 
def Admin_Libros_guardar():
    _nombre=request.form['txtNombre']
    _url=request.form['txtUrl']
    _archivo=request.files['txtImagen']   

    print (_nombre)
    print (_url)
    print (_archivo)

    return redirect('/Admin/Libros')

if __name__ =='__main__':
    app.run(debug=True)