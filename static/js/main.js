window.addEventListener("load", function () {
    const search_form = document.getElementById("search_form");
    search_form.onsubmit = (e) => {
        const fields = document.querySelectorAll(".read-value");
        const j = {};
        /*fields.forEach(field =>
            console.log(field.name + " " + getValue(field))
        );*/
        fields.forEach(field => j[field.name] = getValue(field));
        console.log(j);
        // const select = fields[2];
        // console.log(getSelectValues(select));
        return false;
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