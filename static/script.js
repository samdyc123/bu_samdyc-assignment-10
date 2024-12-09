document.getElementById("search-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const imageFile = document.getElementById("image_query").files[0];
    const textQuery = document.getElementById("text_query").value;
    const lam = parseFloat(document.getElementById("lam").value);
    const queryType = document.getElementById("query_type").value;

    if (isNaN(lam) || lam < 0 || lam > 1) {
        alert("Please enter a valid hybrid query weight (λ) between 0.0 and 1.0.");
        return;
    }

    if (!textQuery) {
        alert("Please enter a text query.");
        return;
    }

    const formData = new FormData();
    if (imageFile) {
        formData.append("image_query", imageFile);
    }
    formData.append("text_query", textQuery);
    formData.append("lam", lam);
    formData.append("query_type", queryType);

    fetch("/search", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById("results");
        const resultsContainer = document.getElementById("results_container");

        // Clear previous results if any
        resultsContainer.innerHTML = "";

        if (data.results && data.results.length > 0) {
            resultsDiv.style.display = "block";

            // Loop through each result and display it
            data.results.forEach(item => {
                const resultItem = document.createElement("div");
                resultItem.className = "result-item";

                const img = document.createElement("img");
                img.src = `/${item.image_path}`;
                img.alt = "Result image";
                img.style.display = "block";

                const scoreP = document.createElement("p");
                scoreP.textContent = `Similarity: ${item.similarity_score.toFixed(3)}`;

                resultItem.appendChild(img);
                resultItem.appendChild(scoreP);
                resultsContainer.appendChild(resultItem);
            });
        } else {
            resultsDiv.style.display = "none";
            alert("No results found.");
        }
    })
    .catch(error => {
        console.error("Error running the search:", error);
        alert("An error occurred while running the search.");
    });
});