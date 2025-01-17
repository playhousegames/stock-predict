document.getElementById('predictForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let symbol = document.getElementById('symbol').value.trim();

    if (symbol === "") {
        alert("Please enter a stock symbol.");
        return;
    }

    fetch(`/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symbol: symbol })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('error').style.display = 'block';
            document.getElementById('error').innerText = `Error: ${data.error}`;
        } else {
            document.getElementById('error').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            document.getElementById('yesterdayPrice').innerText = data.yesterday_price;
            document.getElementById('currentPrice').innerText = data.current_price;
            document.getElementById('todayPredictedPrice').innerText = data.predicted_price_today;
            document.getElementById('tomorrowPredictedPrice').innerText = data.predicted_price_tomorrow;
        }
    })
    .catch(error => {
        document.getElementById('error').style.display = 'block';
        document.getElementById('error').innerText = `An error occurred: ${error.message}`;
    });

    // Update ticker data dynamically
    updateTicker();
});

// Function to fetch and display ticker data
function updateTicker() {
    fetch('/ticker-data')
        .then(response => response.json())
        .then(data => {
            const ticker = document.getElementById('ticker');
            ticker.innerHTML = ''; // Clear existing ticker content

            data.forEach(stock => {
                const stockElement = document.createElement('div');
                stockElement.innerText = `${stock.name}: $${stock.price}`;
                ticker.appendChild(stockElement);
            });
        })
        .catch(error => {
            console.error("Error fetching ticker data:", error);
        });
}
