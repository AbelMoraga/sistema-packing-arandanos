function loadSection(event, url) {
    if (event) event.preventDefault();

    const container = document.getElementById("main-section");

    if (!container) {
        console.error("❌ ERROR: No existe el contenedor #main-section");
        return;
    }

    // Mostrar cargando
    container.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Cargando...</p>
        </div>
    `;

    fetch(url, {
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Error en la respuesta del servidor");
        }
        return response.text();
    })
    .then(html => {
        container.innerHTML = html;
    })
    .catch(err => {
        container.innerHTML = `
            <div class="alert alert-danger">
                Error cargando sección: ${err}
            </div>
        `;
        console.error(err);
    });
}
