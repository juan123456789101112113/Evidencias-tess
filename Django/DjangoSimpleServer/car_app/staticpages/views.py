from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def about(_):
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>📋 Acerca de - Contenido Estático</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f8ff; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            nav a { margin-right: 15px; text-decoration: none; color: #007cba; }
        </style>
    </head>
    <body>
        <div class="container">
            <nav>
                <a href="/static-pages/">🏠 Home</a>
                <a href="/static-pages/about/">ℹ️ About</a>
                <a href="/static-pages/contact/">📧 Contact</a>
            </nav>
            
            <h1>📋 Acerca de Mi Blog Django</h1>
            <p>Esta es una página estática que demuestra cómo Django puede servir contenido HTML fijo.</p>
            
            <h2>🎓 Proyecto Educativo</h2>
            <p>Este blog demuestra 3 enfoques diferentes en Django:</p>
            <ol>
                <li><strong>📄 Contenido Estático</strong> - HTML fijo (esta página)</li>
                <li><strong>🎨 Templates Dinámicos</strong> - HTML generado desde BD</li>
                <li><strong>🔌 API JSON</strong> - Datos en formato JSON</li>
            </ol>
            
            <p><em>Página generada estáticamente el: $(date)</em></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)