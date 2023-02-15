window.addEventListener("load", function () {
    const search_form = document.getElementById("search_form");
    search_form.onsubmit = (e) => {
        const fields = document.querySelectorAll(".read-value");
        const json = { fields: {} };
        jsonFields = json["fields"];
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
        // console.log(JSON.stringify(json));
        // Invio della query
        fetch('./data/response.json')
            .then((response) => response.json())
            .then((json) => buildMoviesList(json))
            .catch(err => {
                this.alert("C'è stato un errore! Vedere la console per ulteriori informazioni");
                console.log(err)
            });
        return false;
    }

    // Show/hide advanced params onclick function
    this.document.getElementById("advanced_params").onclick = () => {
        const paramsDiv = document.querySelector("#advanced_params + div");
        paramsDiv.classList.toggle("hide");
        const icon = document.querySelector("#advanced_params i");
        icon.classList.toggle("fa-arrow-up");
        icon.classList.toggle("fa-arrow-down");
    }
});

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
 * Build movies list by json movies 
 * @param json corresponding to json movies
 */
function buildMoviesList(json) {
    // Save json in session storage
    sessionStorage.setItem("result", JSON.stringify(json));
    // update #search results
    document.querySelector(".w3ls-news-result span").textContent = json.length;
    // Remove hidden div
    document.querySelector("#home").classList.remove("hide");
    const tbody = document.querySelector("#table-breakpoint tbody");
    let no = 1;
    for (const serie of json) {
        // No
        const tr = document.createElement("tr");
        let td = document.createElement("td");
        td.textContent = no++;
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
        const stars = 4.24; // Qui ci andrà il numero di stelle dal nuovo field
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
            li.addEventListener("click", () => sendRating(serie.docID, (iLi + 1)));
            ul.appendChild(li);
        }
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
        li.appendChild(i);
        // Aggiunge la funzione che invia il like
        li.addEventListener("click", () => sendLike(serie.docID, true, i));
        ul.appendChild(li);
        li = document.createElement("li");
        i = document.createElement("i");
        i.classList.add("fa");
        i.classList.add("fa-thumbs-down");
        i.classList.add("fa-2x");
        li.appendChild(i);
        // Aggiunge la funzione che invia il dislike
        li.addEventListener("click", () => sendLike(serie.docID, false, i));
        ul.appendChild(li);
        blockLike.appendChild(ul);
        td.appendChild(blockLike);
        tr.appendChild(td);
        tbody.appendChild(tr);
    }
}

/**
 * Send rating feedback
 * @param {Number} docID 
 * @param {Number} rating 
 * @param {HTMLElement} i optional, indicates the clicked i HTMLElement.
 */
function sendRating(docID, rating, i) {
    if (window.confirm(`Sei sicuro di voler valutare questa serie con ${rating} stelle?`)) {
        const url = "<ip>/<pagina>?docID=" + docID + "&stars=" + rating;
        // alert(url);
        alert("Grazie per aver espresso la tua opinione!");
        // Coloro la stella selezionata e le precedenti
        i = 0;
        document.querySelectorAll(`.block-stars ul`)[docID].childNodes.forEach(li => {
            if (i++ < rating)
                li.firstChild.classList.add("active");
        });
    }
}

/**
 * Send like feedback
 * @param {Number} docID 
 * @param {Boolean} like 
 * @param {HTMLElement} i optional, indicates the clicked i HTMLElement.
 */
function sendLike(docID, like, i) {
    if (window.confirm(`Sei sicuro di voler valutare questa serie ${like ? "positivamente" : "negativamente"}?`)) {
        const url = "<ip>/<pagina>?docID=" + docID + "&like=" + like;
        // alert(url);
        alert("Grazie per aver espresso la tua opinione!");
        document.querySelectorAll(".block-like ul")[docID][like ? "firstChild" : "lastChild"].firstChild.classList.add("active");
    }
}