document.addEventListener("DOMContentLoaded", () => {

	// Save name of product into session storage each time user types in
	document.querySelector("#name").oninput = () => {
		sessionStorage.setItem("NAME", document.querySelector("#name").value);
	}
	document.querySelector("#category").onchange = () => {
		sessionStorage.setItem("CATEGORY", document.querySelector("#category").value);
	};
	document.querySelector("#sell_value").oninput = () => {
		sessionStorage.setItem("VALUE", document.querySelector("#sell_value").value);
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
		if (document.querySelector('#name').value.length > 0 && sessionStorage.length > 3) {
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

	// Force to give a category
	document.querySelector("#category").onkeyup = () => {
		if (document.querySelector("#category").value.length > 0 && sessionStorage.length > 3) {
			document.querySelector('#save_product').removeAttribute("disabled");
		} else {
			document.querySelector('#save_product').setAttribute("disabled", "true");
		}
		if (sessionStorage.getItem('CATEGORY') && sessionStorage.getItem('CATEGORY').length > 0) {
			N_components.removeAttribute('disabled');
		} else {
			N_components.setAttribute('disabled', 'true');
		}
	};

	// Force to give a purchase value
	document.querySelector("#sell_value").onkeyup = () => {
		if (document.querySelector("#sell_value").value.length > 0 && sessionStorage.length > 3) {
			document.querySelector('#save_product').removeAttribute("disabled");
		} else {
			document.querySelector('#save_product').setAttribute("disabled", "true");
		}
		if (sessionStorage.getItem('VALUE') && sessionStorage.getItem('VALUE').length > 0) {
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
				select.id = `select_${i}`;

				// Save button
				const save_component = document.createElement('button');
				save_component.setAttribute('type', 'button');
				//save_component.setAttribute('class', 'secondary');
				save_component.innerHTML = 'Save';

				// Discard button
				const discard_component = document.createElement('button');
				discard_component.setAttribute('class', 'outline');
				discard_component.setAttribute('type', 'button');
				discard_component.innerHTML = 'Discard';

				const div_component = document.createElement('div');
				div_component.setAttribute("class", "grid");
				const label_1 = document.createElement('label');
				const label_2 = document.createElement('label');
				const label_3 = document.createElement('label');
				const label_4 = document.createElement('label');
				// Append elements into the DOM
				label_1.append(search);
				label_2.append(select);
				label_3.append(save_component);
				label_4.append(discard_component);

				div_component.append(label_1, label_2, label_3, label_4);
				components.append(div_component);

				// Fetch names of components from back-end
				search.addEventListener("input", async function () {
					fetch('/search?item_q=' + search.value)
						// Handling response as Json
						.then(response => response.json())
						.then(data => {
							let html = '';
							let select = document.getElementById(`select_${i}`);

							// Display results into select's element
							for (let Name in data) {
								let name = data[Name].name;
								html += '<option value="' + name + '">' + name + '</option>';
							}
							select.innerHTML = html;

							// Selected option event handler
							select.onclick = () => {
								search.value = select.value.trim();

								// Checking if the component is already in use
								let found = false;
								const keys = Object.keys(sessionStorage);

								for (let i = 0; i < keys.length; i++) {
									const key = keys[i];
									if (sessionStorage.getItem(key) === search.value) {
										found = true;
										break;
									}
								}

								// Save button event handler 
								save_component.onclick = () => {
									// Save component locally
									if (found === false) {
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
												if (key === 'NAME' || key === 'CATEGORY' || key === 'VALUE') {
													values_to_send.setAttribute('name', key);
												} else {
													values_to_send.setAttribute('name', `component${i}`);
												}
												document.querySelector('form').append(values_to_send);
											}
										}
									} else {
										alert("Component already in use");
									}
									// Remove component locally
									discard_component.onclick = () => {
										if (sessionStorage.getItem(`component${i+1}`)) {
											search.removeAttribute("disabled");
											select.removeAttribute("disabled");
											sessionStorage.removeItem(`component${i+1}`);
											document.querySelector('#save_product').setAttribute('disabled', 'true');
											document.querySelector('#component_status').textContent = 'Select Component';
										}
									};
								};

							};
						})
				});
			}
		}
	};
	return false;
});