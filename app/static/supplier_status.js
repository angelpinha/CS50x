// Fetch supplier name from server
let input = document.querySelector('input');
input.addEventListener('input', async function () {
    fetch('/search?supplier_q=' + input.value)
        .then(response => response.json())
        .then(data => {
            let html = '';
            for (let Name in data) {
                let name = data[Name].name;

                html += '<li><input id="option" name="items" type="radio">';
                html += '<label for="items">' + name + '</label></li>';
            }
            document.getElementById('options').innerHTML = html;

            document.querySelectorAll('#option').forEach(function (option) {
                option.onchange = () => {
                    document.querySelector('#supplier_name').value = option.nextSibling.textContent.trim();
                    document.querySelector("#supplier_to_send").value = option.nextSibling.textContent.trim();
                };
            });
        });
});

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#supplier_name").oninput = () => {
        if (document.querySelector('#supplier_name').value === '') {
            document.querySelector("#supplier_to_send").value = '';
        }

        if (document.querySelector("#supplier_to_send").value != '' && document.querySelector("#status_to_send").value != '') {
            document.querySelector("#supplier").removeAttribute("disabled");
        } else {
            document.querySelector("#supplier").setAttribute("disabled", "true");
        }
    };
    document.querySelector("#status").onchange = () => {
        document.querySelector("#status_to_send").value = document.querySelector("#status").value;

        if (document.querySelector("#supplier_to_send").value != '' && document.querySelector("#status_to_send").value != '') {
            document.querySelector("#supplier").removeAttribute("disabled");
        } else {
            document.querySelector("#supplier").setAttribute("disabled", "true");
        }
    };
});