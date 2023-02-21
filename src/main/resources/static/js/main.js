window.addEventListener("load", function () {
    const search_form = document.getElementById("search_form");
    search_form.onsubmit = (e) => {
        e.preventDefault();
        const req = buildRequest();
        // Salva la query per il relevance feedback
        sessionStorage.setItem("query", JSON.stringify(req));
        console.log(JSON.stringify(req));
        // Invio della query
        // Uncomment the following lines for fetching to spring server
        fetch('http://localhost:8088/', { //http://locahost:8088/ //https://cat-fact.herokuapp.com/facts
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(req) // body data type must match "Content-Type" header
        }).then((response) => response.json())//response.json())
            .then((json) => buildMoviesList(json))
            .catch(err => {
                this.alert("C'è stato un errore! Vedere la console per ulteriori informazioni");
                console.log(err)
            });

        // Comment the following lines after decomment the previous 
        // this.fetch("./data/response.json").then((response) => response.json())
        //     .then((json) => buildMoviesList(json))
        //     .catch(err => {
        //         this.alert("C'è stato un errore! Vedere la console per ulteriori informazioni");
        //         console.log(err)
        //     });
    }

    // Show/hide advanced params onclick function
    this.document.getElementById("advanced_params").onclick = () => {
        const paramsDiv = document.querySelector("#advanced_params + div");
        paramsDiv.classList.toggle("hide");
        const icon = document.querySelector("#advanced_params i");
        icon.classList.toggle("fa-arrow-up");
        icon.classList.toggle("fa-arrow-down");
    }

    // Send relevance feedback on refresh click
    this.document.querySelector("#refresh").addEventListener("click", sendLikes);
});

/**
 * Read form inputs and build req request
 * @returns JSON req format
 */
function buildRequest() {
    const fields = document.querySelectorAll(".read-value");
    const req = { fields: {} };
    jsonFields = req["fields"];
    // Fields with read-value class
    fields.forEach(field => jsonFields[field.name] = getValue(field));
    // Fields with Genre class
    jsonFields["Genre"] = {
        "op": document.querySelector('input[class="Genre"]:checked').value,
        "values": getSelectValues(document.querySelector('select.Genre'))
    }
    jsonFields["Actors"] = {
        "op": document.querySelector('input[class="Genre"]:checked').value,
        "values": getSelectValues(document.querySelector('select.Actors'))
    }
    jsonFields["boost"] = {};
    this.document.querySelectorAll("input.boost").forEach(
        boost => {
            jsonFields["boost"][boost.name] = getValue(boost);
        }
    );
    return req;
}

// Return an array of the selected opion values
// select is an HTML select element
function getSelectValues(select) {
    var result = [];
    var options = select && select.options;
    var opt;

    for (var i = 0, iLen = options.length; i < iLen; i++) {
        opt = options[i];

        if (opt.selected) {
            result.push(opt.value || opt.text);
        }
    }
    return result;
}

/**
 * 
 * @param {*} input 
 * @returns wanted value for each type of input.
 */
function getValue(input) {
    switch (input.type) {
        case "text":
            return input.value;
        case "select-multiple":
            return getSelectValues(input);
        case "checkbox":
            return input.checked;
        default:
            break;
    }
}

/**
 * Build series list by server response series 
 * @param res corresponding to res series
 */
async function buildMoviesList(res) {
    // Pulisci le vecchia richiesta
    document.querySelector("#table-breakpoint tbody").innerHTML = "";
    // Save res in session storage
    sessionStorage.setItem("result", JSON.stringify(res));
    // update #search results
    document.querySelector(".w3ls-news-result span").textContent = res.length;
    // Remove hidden div
    document.querySelector("#home").classList.remove("hide");
    const tbody = document.querySelector("#table-breakpoint tbody");
    let no = 1;
    for (const serie of res) {
        // No
        const tr = document.createElement("tr");
        let td = document.createElement("td");
        td.textContent = no;
        tr.appendChild(td);
        // Img & Title
        td = document.createElement("td");
        td.classList.add("w3-list-img");
        const a = document.createElement("a");
        a.href = "single.html?docID=" + serie.docID;
        td.appendChild(a);
        const img = document.createElement("img");
        img.src = serie.Poster_Link;
        img.alt = "img not available";
        const span = document.createElement("span");
        span.textContent = serie.Series_Title;
        a.append(img, span);
        tr.appendChild(td);
        // Years
        td = document.createElement("td");
        td.textContent = serie.Runtime_of_Series;
        tr.appendChild(td);
        // Certificate
        td = document.createElement("td");
        td.textContent = serie.Certificate;
        tr.appendChild(td);
        // Genre
        td = document.createElement("td");
        td.textContent = serie.Genre.join(", ");
        tr.appendChild(td);
        // Actors
        td = document.createElement("td");
        td.textContent = serie.Actors.join(", ");
        tr.appendChild(td);
        // Rating
        td = document.createElement("td");
        td.textContent = serie.IMDB_Rating;
        tr.appendChild(td);
        // Stars
        td = document.createElement("td");
        const blockStars = document.createElement("div");
        blockStars.classList.add("block-stars");
        let ul = document.createElement("ul");
        ul.classList.add("w3l-ratings");
        // Fetch serie avg stars from server
        const stars = (await (await fetch(`http://localhost:8088/docID/${serie.docID}/stars`)).json())[serie.docID];
        buildStars(ul, serie.docID, stars);
        blockStars.appendChild(ul);
        td.appendChild(blockStars);
        tr.appendChild(td);
        // Like
        td = document.createElement("td");
        const blockLike = document.createElement("div");
        blockLike.classList.add("block-like");
        ul = document.createElement("ul");
        ul.classList.add("w3l-ratings");
        li = document.createElement("li");
        i = document.createElement("i");
        i.classList.add("fa");
        i.classList.add("fa-thumbs-up");
        i.classList.add("fa-2x");
        i.dataset.docId = serie.docID;
        // Aggiunge la funzione che invia il like
        li.addEventListener("click", (e) => e.target.classList.toggle("active"));
        li.appendChild(i);
        // li.addEventListener("click", () => like(no-1, true, i));
        ul.appendChild(li);
        li = document.createElement("li");
        i = document.createElement("i");
        i.classList.add("fa");
        i.classList.add("fa-thumbs-down");
        i.classList.add("fa-2x");
        i.dataset.docId = serie.docID;
        li.appendChild(i);
        // Aggiunge la funzione che invia il dislike
        li.addEventListener("click", (e) => e.target.classList.toggle("active"));
        ul.appendChild(li);
        blockLike.appendChild(ul);
        td.appendChild(blockLike);
        tr.appendChild(td);
        tbody.appendChild(tr);
        no++;
    }
}

/**
 * Build stars HTML elements 
 * @param {HTMLElement} ul parent element of stars
 * @param {number} docID
 * @param {number} stars number of stars
 */
function buildStars(ul, docID, stars) {
    ul.innerHTML = "";
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
        // Send star feedback
        li.addEventListener("click", (e) => sendRating(docID, (iLi + 1), e));
        ul.appendChild(li);
    }
}

/**
 * Send rating feedback
 * @param {number} docID 
 * @param {number} rating 
 * @param {HTMLElement} e n-th block stars element 
 */
function sendRating(docID, rating, e) {
    if (window.confirm(`Sei sicuro di voler valutare questa serie con ${rating} stelle?`)) {
        // Coloro la stella selezionata e le precedenti
        i = 0;
        e.target.classList.add("active");
        // document.querySelectorAll(`.block-stars ul`)[i].childNodes.forEach(li => {
        e.target.parentElement.parentElement.childNodes.forEach(li => {
            if (i++ < rating)
                li.firstChild.classList.add("active");
        });
        fetch("http://localhost:8088/rating?" + new URLSearchParams({
            "docID": docID,
            "stars": rating
        })).then((response) => response.json())//response.json())
            .then((res) => {
                if (res.status == 200) {
                    console.log(res);
                    alert("Grazie per aver espresso la tua opinione!");// const stars = (await (await fetch(`http://localhost:8088/docID/${docID}/stars`)).json())[docID];
                    buildStars(e.target.parentElement.parentElement, docID, res["avgStars"]);
                }
            })
            .catch(err => {
                this.alert("C'è stato un errore! Vedere la console per ulteriori informazioni");
                console.log(err)
            });
    }
}

/**
 * Send selected like and dislike when refresh is clicked
 */
function sendLikes() {
    if (window.confirm("Sei sicuro di inviare queste valutazioni di rilevanza?")) {
        const relevants = [];
        const nonRelevants = [];
        // Selects every i that has active class
        document.querySelectorAll(".block-like i.fa-thumbs-up.active").forEach(i => relevants.push(Number.parseInt(i.dataset.docId)));
        document.querySelectorAll(".block-like i.fa-thumbs-down.active").forEach(i => nonRelevants.push(Number.parseInt(i.dataset.docId)));
        const req = {
            "relevants": relevants,
            "non-relevants": nonRelevants,
            "fields": JSON.parse(sessionStorage.getItem("query"))["fields"]
        }
        // Remove active class from every i element
        document.querySelectorAll(".block-like i.active").forEach(i => i.classList.remove("active"));
        fetch("http://localhost:8088/rf", {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(req) // body data type must match "Content-Type" header
        }).then((response) => response.json())//response.json())
            .then((data) => buildMoviesList(data))
            .catch(err => {
                this.alert("C'è stato un errore! Vedere la console per ulteriori informazioni");
                console.log(err)
            });
        alert("Grazie per aver espresso la tua preferenza!");
    }
}