let refreshTimer;

async function fetchDiagram() {
    const status = document.getElementById('status');
    const container = document.getElementById('diagramContainer');

    try {
        status.textContent = 'Updating...';

        const response = await fetch('/api/diagram');
        const data = await response.json();

        if (data.success) {
            container.innerHTML = data.svg;
            status.textContent = `Last updated: ${new Date().toLocaleTimeString()} (${data.count} automations)`;
        } else {
            container.innerHTML = `<p class="loading">${data.message}</p>`;
            status.textContent = 'Error';
        }
    } catch (error) {
        console.error('Error fetching diagram:', error);
        container.innerHTML = '<p class="loading">Failed to load diagram</p>';
        status.textContent = 'Error';
    }
}

function startAutoRefresh() {
    fetchDiagram();
    refreshTimer = setInterval(fetchDiagram, REFRESH_INTERVAL);
}

document.getElementById('manualRefresh').addEventListener('click', () => {
    clearInterval(refreshTimer);
    fetchDiagram();
    refreshTimer = setInterval(fetchDiagram, REFRESH_INTERVAL);
});

window.addEventListener('load', startAutoRefresh);