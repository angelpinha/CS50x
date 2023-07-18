let productName = document.querySelector("#name");
productName.addEventListener('input', async function () {
	fetch('/search?product_q=' + productName.value)
		.then(response => response.json())
		.then(data => {
			let html = '';
			if (data.length > 0) {
				document.querySelector("#product_options").size = data.length;
				for (let Product in data) {
					var name = data[Product].name;
					var price = data[Product]["price"];

					html += '<option><input class="product_option" name="product" type="radio">';
					html += '<label class="name_value" for="product">' + name + '</label></option>';
				}
				document.getElementById("product_options").innerHTML = html;

				const events = ['keydown', 'change'];
				events.forEach(event => {
					document.querySelector("#product_options").addEventListener(event, function (event) {

						document.querySelector("#name").value = document.getElementById("product_options").value;

						for (let Product in data) {
							if (data[Product].name === document.querySelector("#name").value) {
								document.querySelector("#unit_price").value = `$${data[Product].price}`;
								document.querySelector("#total").value = `$${String(document.querySelector("#unit_price").value.slice(1) *
                                        document.querySelector("#quantity").value)}`;
							}
						}
						if (event.key === 'Enter' || event === 'change') {
							document.querySelector("#product_options").size = 1;
						};

					})
				});
				// If an option is selected
				document.querySelector("#product_options").onmousedown = function (event) {
					if (event.button === 0 || event.key === 'Tab' && document.getElementById("product_options").value != 'Select') {
						document.querySelector("#name").value = document.getElementById("product_options").value;
						// Enable "Add to ticket" button if quantity greater than 0
						if (document.querySelector("#quantity").value > 0) {
							document.querySelector("#save_product").removeAttribute("disabled");
						}
						// Get product option size to 1 
						if (document.querySelector("#name").value != '') {
							document.querySelector("#product_options").size = 1;
							// Find product price in json
							for (let Product in data) {
								if (data[Product].name === document.querySelector("#name").value) {
									document.querySelector("#unit_price").value = `$${data[Product].price}`;
									document.querySelector("#total").value = `$${String(document.querySelector("#unit_price").value.slice(1) *
                                    document.querySelector("#quantity").value)}`;
								}
							}
						}
					}
				};


			} else {
				document.querySelector("#product_options").innerHTML = '';
				document.querySelector("#unit_price").value = '';
				document.querySelector("#quantity").value = '';
				document.querySelector("#total").value = '$';
				let selectOption = document.createElement("option");
				selectOption.innerHTML = 'Select';
				selectOption.setAttribute("disabled", "true");
				selectOption.setAttribute("selected", "true");
				document.querySelector("#product_options").append(selectOption);
				document.querySelector("#product_options").size = 1;
			}
		})
})

var PRODUCTS = new Object();
document.addEventListener("DOMContentLoaded", () => {
	document.querySelector("#check_out").setAttribute("disabled", "true");
	document.querySelector("#save_product").setAttribute("disabled", "true");

	document.querySelector("#quantity").oninput = () => {
		document.querySelector("#total").value = `$${String(document.querySelector("#unit_price").value.slice(1) *
		document.querySelector("#quantity").value)}`;

		if (document.querySelector("#total").value.slice(1) > 0) {
			document.querySelector("#save_product").removeAttribute("disabled");
		} else {
			document.querySelector("#save_product").setAttribute("disabled", "true");
		}
	};
	document.addEventListener("keydown", (event) => {
		if (document.querySelector("#name").value === 'Select') {
			document.querySelector("#name").value = '';
		}
	})
	document.addEventListener("mousedown", (event) => {
		if (document.querySelector("#name").value === 'Select') {
			document.querySelector("#name").value = '';
		}
	})

	document.querySelector("#name").onkeydown = (event) => {
		if (event.key === 'Backspace' || event.key === 'Delete') {
			document.querySelector("#check_out").setAttribute("disabled", "true");
			document.querySelector("#save_product").setAttribute("disabled", "true");
			document.querySelector("#unit_price").value = '$';
			document.querySelector("#quantity").value = '';
			document.querySelector("#total").value = '$';
		}
	};


	document.querySelector("#save_product").onclick = () => {
		document.querySelector("#save_product").setAttribute("disabled", "true");
		document.querySelector("#check_out").removeAttribute("disabled");
		if (!PRODUCTS[document.querySelector("#name").value]) {
			PRODUCTS[document.querySelector("#name").value] = {};
			PRODUCTS[document.querySelector("#name").value]["quantity"] = document.querySelector("#quantity").value;
			PRODUCTS[document.querySelector("#name").value]["total"] = document.querySelector("#total").value.slice(1);

			// Show table of products
			const productName = document.createElement("td");
			productName.innerHTML = document.querySelector("#name").value;
			const productQuantity = document.createElement("td");
			productQuantity.setAttribute("id", `${document.querySelector("#name").value}_quantity`);
			productQuantity.innerHTML = PRODUCTS[document.querySelector("#name").value]["quantity"];
			const productTotal = document.createElement("td");
			productTotal.setAttribute("id", `${document.querySelector("#name").value}_total`)
			productTotal.innerHTML = PRODUCTS[document.querySelector("#name").value]["total"];
			const productRow = document.createElement("tr");
			productRow.append(productName, productQuantity, productTotal);
			document.querySelector("#ticket").append(productRow);

			// Save products into form
			const productFormName = document.createElement("input");
			productFormName.setAttribute("hidden", "true");
			productFormName.value = document.querySelector("#name").value;
			productFormName.name = `name_${Object.keys(PRODUCTS).length}`;
			const productFormQuantity = document.createElement("input");
			productFormQuantity.setAttribute("hidden", "true");
			productFormQuantity.id = `q_${document.querySelector("#name").value}`;
			productFormQuantity.name = `quantity_${Object.keys(PRODUCTS).length}`;
			productFormQuantity.value = PRODUCTS[document.querySelector("#name").value]["quantity"];
			const productFormTotal = document.createElement("input");
			productFormTotal.setAttribute("hidden", "true");
			productFormTotal.id = `t_${document.querySelector("#name").value}`;
			productFormTotal.name = `total_${Object.keys(PRODUCTS).length}`;
			productFormTotal.value = PRODUCTS[document.querySelector("#name").value]["total"];
			document.querySelector("form").append(productFormName, productFormQuantity, productFormTotal);

		} else {
			// Update PRODUCTS object
			let newQuantity = Number(PRODUCTS[document.querySelector("#name").value]["quantity"]) +
				Number(document.querySelector("#quantity").value);
			let newTotal = Number(PRODUCTS[document.querySelector("#name").value]["total"]) +
				Number(document.querySelector("#total").value.slice(1));
			PRODUCTS[document.querySelector("#name").value]["quantity"] = newQuantity;
			PRODUCTS[document.querySelector("#name").value]["total"] = newTotal;
			// Update table of products
			document.getElementById(`${document.querySelector("#name").value}_quantity`).innerHTML = newQuantity;
			document.getElementById(`${document.querySelector("#name").value}_total`).innerHTML = newTotal;
			// Update products within form
			if (document.querySelector(`#q_${document.querySelector("#name").value}`)) {
				document.querySelector(`#q_${document.querySelector("#name").value}`).value = newQuantity;
			}
			if (document.querySelector(`#t_${document.querySelector("#name").value}`)) {
				document.querySelector(`#t_${document.querySelector("#name").value}`).value = newTotal;
			}
		}
		document.querySelector("#product_number").value = Object.keys(PRODUCTS).length;
		let toPay = 0;
		const keys = Object.keys(PRODUCTS);
		for (let i = 0; i < keys.length; i++) {
			const key = keys[i];
			toPay += Number(PRODUCTS[key]["total"]);
		}
		document.querySelector("#to_pay").value = `$${toPay}`;

		document.querySelector("#name").value = '';
		document.querySelector("#product_options").innerHTML = '';
		let selectOption = document.createElement("option");
		selectOption.innerHTML = 'Select';
		selectOption.setAttribute("disabled", "true");
		selectOption.setAttribute("selected", "true");
		document.querySelector("#product_options").append(selectOption);
		document.querySelector("#product_options").size = 1;
		document.querySelector("#unit_price").value = '';
		document.querySelector("#quantity").value = '';
		document.querySelector("#total").value = '$';
	};
});