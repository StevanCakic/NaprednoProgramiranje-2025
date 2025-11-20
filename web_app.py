from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

def get_db_data():
    conn = sqlite3.connect('troskovi.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT T.naziv, T.iznos, T.tip, T.namjena, L.naziv 
        FROM Troskovi T
        JOIN Lokacije L ON T.lokacija_id = L.id
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

# Jednostavan HTML template unutar stringa
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Pregled Troškova Web</title>
    <style>
        body { font-family: sans-serif; background-color: #f0f2f5; padding: 20px; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
        th { background-color: #3B8ED0; color: white; }
        tr:hover { background-color: #f5f5f5; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>📊 Online Menadžment Troškova</h1>
    <table>
        <thead>
            <tr>
                <th>Naziv</th>
                <th>Iznos (€)</th>
                <th>Tip</th>
                <th>Namjena</th>
                <th>Lokacija</th>
            </tr>
        </thead>
        <tbody>
            {% for row in rows %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    troskovi = get_db_data()
    return render_template_string(HTML_TEMPLATE, rows=troskovi)

if __name__ == '__main__':
    print("Pokrećem Web Server na http://127.0.0.1:5000")
    app.run(debug=True, port=5000)