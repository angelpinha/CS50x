document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#supplier_name").oninput = () => {
        document.querySelector("#supplier_to_send").value = document.querySelector("#supplier_name").value;

        if (document.querySelector("#supplier_to_send").value != '' && document.querySelector("#status_to_send").value != '') {
            document.querySelector("#save_supplier").removeAttribute("disabled");
        } else {
            document.querySelector("#save_supplier").setAttribute("disabled", "true");
        }
    };
    document.querySelector("#status").onchange = () => {
        document.querySelector("#status_to_send").value = document.querySelector("#status").value;

        if (document.querySelector("#supplier_to_send").value != '' && document.querySelector("#status_to_send").value != '') {
            document.querySelector("#save_supplier").removeAttribute("disabled");
        } else {
            document.querySelector("#save_supplier").setAttribute("disabled", "true");
        }
    };
});