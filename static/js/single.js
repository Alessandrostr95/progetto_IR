window.addEventListener("load", function () {
    const json = JSON.parse(this.sessionStorage.getItem("result"));
    const urlParams = new URLSearchParams(document.location.search);
    const docID = urlParams.get("docID");
    buildSingleSerie(json.filter(serie => serie.docID == docID)[0]);
    buildRelatedSeries(json.filter(serie => serie.docID != docID));
});

/**
 * Build serie information view by serie JSON
 * @param {JSON} serie JSON information about serie
 */
function buildSingleSerie(serie) {
    // Set serie title as page title
    document.title = serie.Series_Title;
    // Set serie title
    const h3 = document.querySelector(".song-info>h3");
    h3.textContent = serie.Series_Title;
    // img
    const img = document.querySelector("#video>img");
    img.src = serie.Poster_Link;
    // IMDB_Rating
    const rating = document.querySelector(".single-agile-shar-buttons span");
    rating.textContent += serie.IMDB_Rating;
    // Stars
    const ul = document.querySelector(".w3l-ratings");
    const stars = 4.25; // Qui ci andrà il numero di stelle dal nuovo field
    for (let iLi = 0; iLi < 5; iLi++) {
        const li = document.createElement("li");
        const i = document.createElement("i");
        i.classList.add("fa");
        i["aria-hidden"] = "true";
        if ((iLi + 0.5) == (Math.round(stars * 2) / 2))
            i.classList.add("fa-star-half-o");
        else if (iLi < Math.round(stars))
            i.classList.add("fa-star");
        else
            i.classList.add("fa-star-o");
        li.appendChild(i);
        ul.appendChild(li);
    }
    // Overview
    const overview = document.querySelector(".agile-info-wthree-box>p");
    overview.textContent = serie.Overview;
}

/**
 * Build related series view from JSON series
 * @param {JSON} series series JSON information.
 */
function buildRelatedSeries(series) {
    // Right grid div
    const grid = document.querySelector(".single-grid-right");
    for (serie of series) {
        // Single serie div
        const single = document.createElement("div");
        single.classList.add("single-right-grids");
        // Single left sub-div
        const singleLeft = document.createElement("div");
        singleLeft.classList.add("col-md-4", "single-right-grid-left");
        // a 
        let a = document.createElement("a");
        a.href = "single.html?docID=" + serie.docID;
        // img
        const img = document.createElement("img");
        img.src = serie.Poster_Link;
        a.appendChild(img);
        singleLeft.appendChild(a);
        single.appendChild(singleLeft);
        // Single right sub-div
        const singleRight = document.createElement("div");
        singleRight.classList.add("col-md-8", "single-right-grid-right");
        // a
        a = document.createElement("a");
        a.href = "single.html?docID=" + serie.docID;
        a.classList.add("title");
        a.textContent = serie.Series_Title;
        singleRight.appendChild(a);
        // p actor
        let p = document.createElement("p");
        p.classList.add("author");
        p.textContent = serie.Actors[0];
        singleRight.appendChild(p);
        // p votes
        p = document.createElement("p");
        p.classList.add("views");
        p.textContent = serie.No_of_Votes.toLocaleString()+ " votes";
        singleRight.appendChild(p);
        // Append right div to single
        single.appendChild(singleRight);
        // Div clearfix
        const clearfix = document.createElement("div");
        clearfix.classList.add("clearfix");
        single.appendChild(clearfix);
        grid.appendChild(single);
    }
}