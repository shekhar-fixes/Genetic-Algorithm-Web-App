let chartInstance = null;

function renderChart(labels, data) {
    const ctx = document.getElementById("fitnessChart").getContext("2d");

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Best Fitness",
                data: data,
                borderWidth: 2,
                tension: 0.3,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

document.getElementById("gaForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const payload = {
        target: document.getElementById("target").value.trim(),
        population_size: parseInt(document.getElementById("population_size").value),
        generations: parseInt(document.getElementById("generations").value),
        crossover_rate: parseFloat(document.getElementById("crossover_rate").value),
        mutation_rate: parseFloat(document.getElementById("mutation_rate").value)
    };

    const output = document.getElementById("output");
    output.innerHTML = "Running...";

    try {
        const response = await fetch("/api/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            output.innerHTML = `<span class="error">${result.error || "Something went wrong."}</span>`;
            return;
        }

        output.innerHTML = `
            <strong>Target:</strong> ${result.target}<br>
            <strong>Best Solution:</strong> ${result.best_solution}<br>
            <strong>Best Fitness:</strong> ${result.best_fitness} / ${result.max_fitness}<br>
            <strong>Generations Ran:</strong> ${result.generations_ran}
        `;

        const labels = result.history.map((_, i) => `G${i + 1}`);
        renderChart(labels, result.history);

    } catch (err) {
        output.innerHTML = `<span class="error">Error: ${err.message}</span>`;
    }
});