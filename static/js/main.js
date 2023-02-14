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
        console.log(json);
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