document.addEventListener("DOMContentLoaded", () => {
    // Checking if page was reloaded
    const pageAccessedByReload = (
        (window.performance.navigation && window.performance.navigation.type === 1) ||
        window.performance
        .getEntriesByType('navigation')
        .map((nav) => nav.type)
        .includes('reload')
    );
    // If page was reloaded, clear session Storage
    if (pageAccessedByReload == true) {
        sessionStorage.clear();
    }

    // Save name of product into session storage each time user types in
    document.querySelector('#name').oninput = () => {
        sessionStorage.setItem('NAME', document.querySelector('#name').value);
    }

    // Number of components provided by user:
    const N_components = document.querySelector("#n_components");
    N_components.setAttribute('disabled', 'true');
    // Future List of components
    const components = document.querySelector('#components');
    // Save product button initially disabled
    document.querySelector('#save_product').setAttribute("disabled", "true");

    // Force to give a product name
    document.querySelector('#name').onkeyup = () => {
        if (document.querySelector('#name').value.length > 0 && sessionStorage.length > 1) {
            document.querySelector('#save_product').removeAttribute("disabled");

        } else {
            document.querySelector('#save_product').setAttribute("disabled", "true");
        }
        if (sessionStorage.getItem('NAME') && sessionStorage.getItem('NAME').length > 0) {
            N_components.removeAttribute('disabled');
        } else {
            N_components.setAttribute('disabled', 'true');
        }
    };

    // Event handler, each time user types in the number of components
    N_components.onkeyup = () => {
        // Prevent from change name already given
        document.querySelector('#name').setAttribute('disabled', 'true');

        // Ensuring user types a number, and five is the maximum number of components
        if (N_components.value.length > 0 && N_components.value <= 5 && !N_components.value.includes(' ')) {
            document.querySelector('#component_status').textContent = 'Select Component';

            // Enable reset button
            document.querySelector('#reset').removeAttribute("disabled");

            // Event handler, to reset all values
            document.querySelector('#reset').onclick = () => {
                components.innerHTML = '';
                document.querySelector('#name').removeAttribute('disabled');
                document.querySelector('#name').value = '';
                N_components.removeAttribute("disabled");
                N_components.value = '';
                sessionStorage.clear();
                document.querySelector('#component_status').textContent = '';
            };


            // Prevent from change number of components without reset values
            N_components.setAttribute("disabled", "true");

            // Create fields of components, according to number provided earlier
            for (let i = 0; i < parseInt(N_components.value); i++) {
                // Search element
                const search = document.createElement('input');
                search.setAttribute("type", "search");
                search.setAttribute("placeholder", `Component ${i+1}`);

                // Select element
                const select = document.createElement('select');

                // Save button
                const save_component = document.createElement('button');
                save_component.setAttribute('type', 'button');
                save_component.innerHTML = 'Save';

                // Discard button
                const discard_component = document.createElement('button');
                discard_component.setAttribute('class', 'secondary');
                discard_component.setAttribute('type', 'button');
                discard_component.innerHTML = 'Discard';

                // Append elements into the DOM
                components.append(search);
                components.append(select);
                components.append(save_component);
                components.append(discard_component);

                // Fetch names of components from back-end
                search.addEventListener("input", async function () {
                    fetch('/search?q=' + search.value)
                        // Handling response as Json
                        .then(response => response.json())
                        .then(data => {
                            let html = '';
                            let select = search.nextElementSibling;

                            // Display results into select's element
                            for (let Name in data) {
                                let name = data[Name].name;
                                html += '<option value="' + name + '">' + name + '</option>';
                            }
                            select.innerHTML = html;

                            // Event handler of selected option 
                            select.onclick = () => {
                                search.value = select.value.trim();

                                // Save component locally  
                                save_component.onclick = () => {
                                    if (!sessionStorage.getItem(search.value)) {
                                        sessionStorage.setItem(`component${i+1}`, search.value);
                                        document.querySelector('#component_status').textContent = 'Component Added.'
                                        search.setAttribute("disabled", "true");
                                        select.setAttribute("disabled", "true");

                                        // Ensuring the name of the product is stored already into session
                                        if (sessionStorage.getItem('NAME') &&
                                            sessionStorage.getItem('NAME') != '' &&
                                            sessionStorage.length > parseInt(N_components.value)) {
                                            document.querySelector('#save_product').removeAttribute("disabled");
                                        } else {
                                            document.querySelector('#save_product').setAttribute('disabled', 'true');
                                        }

                                        // Set the input of components and name of the product
                                        if (sessionStorage.length > 0) {
                                            const length = sessionStorage.length;
                                            //const values_to_send = document.createElement('input');

                                            //let list = '';
                                            for (let i = 0; i <= length; i++) {
                                                if (document.querySelector('.to_send')) {
                                                    document.querySelector('.to_send').remove();
                                                }
                                            }

                                            const quantity = document.createElement('input');
                                            quantity.setAttribute('name', 'quantity');
                                            quantity.setAttribute('value', length);
                                            quantity.setAttribute('class', 'to_send');
                                            quantity.setAttribute('hidden', 'true');
                                            document.querySelector('form').append(quantity);

                                            // Iterate over session storage
                                            for (let i = 0; i < length; i++) {

                                                const values_to_send = document.createElement('input');
                                                const key = sessionStorage.key(i);
                                                const value = sessionStorage.getItem(key);

                                                values_to_send.setAttribute('class', 'to_send');
                                                values_to_send.setAttribute('value', value);
                                                values_to_send.setAttribute('hidden', 'true');
                                                if (key != 'NAME') {
                                                    values_to_send.setAttribute('name', `component${i}`);
                                                } else {
                                                    values_to_send.setAttribute('name', key);
                                                }
                                                document.querySelector('form').append(values_to_send);
                                            }
                                        }
                                    }
                                };
                                // Remove component locally
                                discard_component.onclick = () => {
                                    if (sessionStorage.getItem(search.value)) {
                                        search.removeAttribute("disabled");
                                        select.removeAttribute("disabled");
                                        sessionStorage.removeItem(search.value);
                                        document.querySelector('#save_product').setAttribute('disabled', 'true');
                                        document.querySelector('#component_status').textContent = 'Select Component';
                                    }
                                };

                            };
                        })
                });
            }
        }
    };
    return false;
});