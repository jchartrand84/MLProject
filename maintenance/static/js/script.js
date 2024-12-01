document.addEventListener("DOMContentLoaded", function() {
    const fetchDataBtn = document.getElementById("fetchDataBtn");
    const calculateBtn = document.getElementById("calculateBtn");

    fetchDataBtn.addEventListener("click", function() {
        // For now, we will just log the latitude and longitude
        const latitude = document.getElementById("latitude").value;
        const longitude = document.getElementById("longitude").value;
        console.log(`Fetching data for Latitude: ${latitude}, Longitude: ${longitude}`);

        // Enable further form interactions for demo purposes
        document.getElementById("annualKwh").disabled = false;
        document.getElementById("maxAnnual").disabled = false;
        document.getElementById("minAnnual").disabled = false;
        document.getElementById("meanAnnual").disabled = false;
        calculateBtn.disabled = false;
    });

    calculateBtn.addEventListener("click", function() {
        console.log("Calculating solar panel requirements...");
        // Here we will add AJAX logic later to process the form data
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const fetchDataBtn = document.getElementById("fetchDataBtn");
    const spinner = document.getElementById('spinner');
    const form = document.querySelector('form');
    form.addEventListener('submit', function() {
        // Show the spinner
        spinner.classList.remove('d-none');
        // Update the button
        fetchDataBtn.disabled = true;
        fetchDataBtn.textContent = 'Loading...';
        fetchDataBtn.classList.add('loading');
    });
});
