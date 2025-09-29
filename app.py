from flask import Flask, render_template, request, redirect, url_for
from biblioteca import Biblioteca
import time, random, string

app = Flask(__name__)
biblioteca = Biblioteca()

class Libro:
    def __init__(self, id, titulo, autor, genero, año):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.año = año
        self.prestado = False
    def __str__(self):
        estado = " (Prestado)" if self.prestado else " (Disponible)"
        return f"Código: {self.id}, Título: {self.titulo}, Autor: {self.autor}, Año: {self.año}{estado}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_libro():
    resultado = ""
    if request.method == 'POST':
        id = request.form['id']
        titulo = request.form['titulo']
        autor = request.form['autor']
        genero = request.form['genero']
        año = request.form['año']
        libro = Libro(id, titulo, autor, genero, año)
        exito = biblioteca.agregar_libro(libro)
        resultado = "Libro agregado exitosamente." if exito else "Error: El ID ya existe."
    return render_template('agregar.html', resultado=resultado)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar_libro():
    libro = None
    if request.method == 'POST':
        id = request.form['id']
        libro = biblioteca.buscar_libro_id(id)
    return render_template('buscar.html', libro=libro)

@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar_libro():
    resultado = ""
    if request.method == 'POST':
        id = request.form['id']
        libro = biblioteca.buscar_libro_id(id)
        if libro:
            biblioteca.eliminar_libro(id)
            resultado = "Libro eliminado correctamente."
        else:
            resultado = "Libro no encontrado."
    return render_template('eliminar.html', resultado=resultado)

@app.route('/mostrar')
def mostrar_libros():
    libros = list(biblioteca.libros_por_id.values())
    return render_template('mostrar.html', libros=libros)

@app.route('/prestamo', methods=['GET', 'POST'])
def prestamo_libro():
    resultado = ""
    tiempo = None
    if request.method == 'POST':
        id = request.form['id']
        start = time.time()
        exito = biblioteca.marcar_como_prestado(id)
        end = time.time()
        tiempo = round(end - start, 6)
        resultado = "Libro prestado exitosamente." if exito else "No se pudo prestar el libro (quizá ya está prestado o no existe)."
    disponibles = [libro for libro in biblioteca.libros_por_id.values() if not libro.prestado]
    return render_template('prestamo.html', resultado=resultado, disponibles=disponibles, tiempo=tiempo)

@app.route('/devolver', methods=['GET', 'POST'])
def devolver_libro():
    resultado = ""
    tiempo = None
    if request.method == 'POST':
        id = request.form['id']
        start = time.time()
        exito = biblioteca.marcar_como_devuelto(id)
        end = time.time()
        tiempo = round(end - start, 6)
        resultado = "Libro devuelto exitosamente." if exito else "No se pudo devolver el libro (quizá no está prestado o no existe)."
    prestados = [libro for libro in biblioteca.libros_por_id.values() if libro.prestado]
    return render_template('devolver.html', resultado=resultado, prestados=prestados, tiempo=tiempo)

@app.route('/prestados')
def libros_prestados():
    prestados = [libro for libro in biblioteca.libros_por_id.values() if libro.prestado]
    return render_template('prestados.html', prestados=prestados)

@app.route('/benchmark', methods=['GET', 'POST'])
def benchmark():
    resultado = ""
    n_libros = 10000
    if request.method == 'POST':
        n_libros = int(request.form.get('n_libros', 10000))
        biblioteca.libros_por_id.clear()
        biblioteca.libros_por_genero.clear()
        biblioteca.libros_por_autor.clear()
        start = time.time()
        for i in range(1, n_libros + 1):
            id = str(i)
            titulo = f"Libro {i}"
            autor = f"Autor_{random.choice(string.ascii_uppercase)}"
            genero = random.choice(["Novela", "Cuento", "Ensayo", "Poesía", "Drama"])
            año = str(random.randint(1900, 2025))
            libro = Libro(id, titulo, autor, genero, año)
            biblioteca.agregar_libro(libro)
        end = time.time()
        tiempo_agregar = round(end - start, 4)

        start = time.time()
        libros = list(biblioteca.libros_por_id.values())
        end = time.time()
        tiempo_mostrar = round(end - start, 4)

        id_buscar = str(random.randint(1, n_libros))
        start = time.time()
        libro_encontrado = biblioteca.buscar_libro_id(id_buscar)
        end = time.time()
        tiempo_buscar_id = round(end - start, 8)

        genero_buscar = random.choice(["Novela", "Cuento", "Ensayo", "Poesía", "Drama"])
        start = time.time()
        libros_genero = biblioteca.buscar_libro_genero(genero_buscar)
        end = time.time()
        tiempo_buscar_genero = round(end - start, 8)

        resultado = f"""
        <b>Benchmark realizado con {n_libros} libros:</b><br>
        Tiempo en agregar libros: {tiempo_agregar} segundos<br>
        Tiempo en obtener lista de todos los libros: {tiempo_mostrar} segundos<br>
        Tiempo en buscar por ID: {tiempo_buscar_id} segundos<br>
        Tiempo en buscar por género: {tiempo_buscar_genero} segundos<br>
        Ejemplo libro encontrado por ID: {libro_encontrado if libro_encontrado else 'No encontrado'}<br>
        Ejemplo libros encontrados por género '{genero_buscar}': {len(libros_genero)}<br>
        """
    return render_template('benchmark.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)