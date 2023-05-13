document.addEventListener("DOMContentLoaded", () => {

    document.querySelector(".grid").oninput = () => {
        if (sessionStorage.length === 5) {
            document.querySelector("#save_item").removeAttribute("disabled");
        } else {
            document.querySelector("#save_item").setAttribute("disabled", "true");
        }
    };
    document.querySelector(".grid").onclick = () => {
        if (sessionStorage.length === 5) {
            document.querySelector("#save_item").removeAttribute("disabled");
        } else {
            document.querySelector("#save_item").setAttribute("disabled", "true");
        }
    };

    document.querySelector("#save_item").setAttribute("disabled", "true");

    // Save item name into Session Storage and form
    const name = document.createElement("input");
    document.querySelector("#name").oninput = () => {
        if (document.querySelector("#name").value != '' && isNaN(document.querySelector("#name").value)) {
            sessionStorage.setItem("NAME", document.querySelector("#name").value);
            name.setAttribute("name", "name");
            name.setAttribute("value", sessionStorage.getItem("NAME"));
            name.setAttribute("id", "name");
            name.setAttribute("hidden", "true");

            document.querySelector("form").append(name);

        } else {
            sessionStorage.removeItem("NAME");

        }
    };

    // Save Cost Center into Session Storage and form
    const costCenter = document.createElement("input");
    document.querySelector("#cost_center").onclick = () => {
        if (document.querySelector("#cost_center").value != '') {
            sessionStorage.setItem("COST CENTER", document.querySelector("#cost_center").value);
            costCenter.setAttribute("name", "cost_center");
            costCenter.setAttribute("value", sessionStorage.getItem("COST CENTER"));
            costCenter.setAttribute("id", "cost_center");
            costCenter.setAttribute("hidden", "true");

            if (document.querySelector("#cost_center").value && document.querySelector("#cost_center").value != 'Cost Center') {
                document.querySelector("form").append(costCenter);
            }
        } else {
            sessionStorage.removeItem("COST CENTER");
        }
    };

    // Save Item Format into Session Storage and form
    const format = document.createElement("input");
    document.querySelector("#format").oninput = () => {
        if (document.querySelector("#format").value != '' && !isNaN(document.querySelector("#format").value)) {
            sessionStorage.setItem("FORMAT", document.querySelector("#format").value);
            format.setAttribute("name", "format");
            format.setAttribute("value", sessionStorage.getItem("FORMAT"));
            format.setAttribute("id", "format");
            format.setAttribute("hidden", "true");

            if (document.querySelector("#format").value) {
                document.querySelector("form").append(format);
                if (sessionStorage.length === 5) {
                    document.querySelector("#save_item").removeAttribute("disabled");
                }
            }
        } else {
            sessionStorage.removeItem("FORMAT");
        }
    };

    // Save Item unit into Session Storage and form
    const unit = document.createElement("input");
    document.querySelector("#unit").onclick = () => {
        if (document.querySelector("#unit").value != '') {
            sessionStorage.setItem("UNIT", document.querySelector("#unit").value);
            unit.setAttribute("name", "unit");
            unit.setAttribute("value", sessionStorage.getItem("UNIT"));
            unit.setAttribute("id", "unit");
            unit.setAttribute("hidden", "true");

            if (document.querySelector("#unit").value) {
                document.querySelector("form").append(unit);
            }
        } else {
            sessionStorage.removeItem("UNIT");
        }
    };

    // Save Item format value into Session Storage and form
    const formatValue = document.createElement("input");
    document.querySelector("#format_value").oninput = () => {
        if (document.querySelector("#format_value").value != '' && !isNaN(document.querySelector("#format_value").value)) {
            sessionStorage.setItem("VALUE", document.querySelector("#format_value").value);
            formatValue.setAttribute("name", "value");
            formatValue.setAttribute("value", sessionStorage.getItem("VALUE"));
            formatValue.setAttribute("id", "value");
            formatValue.setAttribute("hidden", "true");

            document.querySelector("form").append(formatValue);
        } else {
            sessionStorage.removeItem("VALUE");
        }
    };
});