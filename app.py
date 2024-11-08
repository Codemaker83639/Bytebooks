from flask import Flask
from flask import render_template

app=Flask (__name__) 

@app.route('/') 
def inicio():
    return render_template('Bytebooks/index.html')

@app.route('/Libros')
def Libros():
    return render_template('Bytebooks/Libros.html')

@app.route('/Nosotros')
def Nosotros():
    return render_template('Bytebooks/Nosotros.html')

if __name__ =='__main__':
    app.run(debug=True)