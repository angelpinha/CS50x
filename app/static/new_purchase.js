// Fetch supplier name from server
let supplier = document.querySelector("#supplier");
supplier.addEventListener('input', async function () {
	fetch('/search?supplier_q=' + supplier.value)
		.then(response => response.json())
		.then(data => {
			let html = '';
			for (let Name in data) {
				let name = data[Name].name;

				html += '<li><input class="supplier_option" name="supplier" type="radio">';
				html += '<label for="supplier">' + name + '</label></li>';
			}
			document.getElementById("supplier_options").innerHTML = html;

			// Save supplier name into form
			const supplierName = document.createElement("input");
			document.querySelectorAll(".supplier_option").forEach(function (option) {
				option.onchange = () => {
					if (document.querySelector("#supplier_input")) {
						document.querySelector("#supplier_input").remove();
					}

					document.querySelector("#supplier").value = option.nextSibling.textContent.trim();
					//supplierName.value = option.nextSibling.textContent.trim();
					supplierName.setAttribute("name", "supplier_name");
					supplierName.setAttribute("id", "supplier_input");
					supplierName.setAttribute("hidden", "true");
					supplierName.setAttribute("value", option.nextSibling.textContent.trim())
					document.querySelector("form").append(supplierName);

				};
			});
			document.querySelector("#supplier").oninput = () => {
				if (document.querySelector("#supplier").value === '' && supplierName) {
					supplierName.remove();
				}
			};
		});
});

var ITEMS = new Object();
document.addEventListener("DOMContentLoaded", () => {
	document.querySelector("#item_number").value = 0;

	// Check if purchase is ready to save
	document.querySelector("#to_send").oninput = () => {
		if (document.querySelector("form").childElementCount > 5) {
			document.querySelector("#save_invoice").removeAttribute("disabled");
		} else {
			document.querySelector("#save_invoice").setAttribute("disabled", "true");
		}
	};
	document.querySelector("#to_send").onkeyup = () => {
		if (document.querySelector("form").childElementCount > 5) {
			document.querySelector("#save_invoice").removeAttribute("disabled");
		} else {
			document.querySelector("#save_invoice").setAttribute("disabled", "true");
		}
	};
	document.querySelector("#to_send").onchange = () => {
		if (document.querySelector("form").childElementCount > 5) {
			document.querySelector("#save_invoice").removeAttribute("disabled");
		} else {
			document.querySelector("#save_invoice").setAttribute("disabled", "true");
		}
	};


	// Add invoice number into form
	const invoiceNumber = document.createElement("input");
	document.querySelector("#invoice_n").oninput = () => {
		if (document.querySelector("#invoice_n").value != '' && !isNaN(document.querySelector("#invoice_n").value)) {
			invoiceNumber.setAttribute("name", "invoice_number");
			invoiceNumber.setAttribute("hidden", "true");
			invoiceNumber.setAttribute("value", document.querySelector("#invoice_n").value);
			document.querySelector("form").append(invoiceNumber);

		} else {
			if (invoiceNumber) {
				invoiceNumber.remove();
			}
		}
	};

	// Add date into form
	const invoiceDate = document.createElement("input");
	document.querySelector("#date").onkeyup = () => {
		let date = new Date();
		if (document.querySelector("#date").value.length === 10 &&
			document.querySelector("#date").value.slice(0, 4) == date.getFullYear()) {
			invoiceDate.setAttribute("name", "invoice_date");
			invoiceDate.setAttribute("hidden", "true");
			invoiceDate.setAttribute("value", document.querySelector("#date").value);
			document.querySelector("form").append(invoiceDate);
		} else if (invoiceDate) {
			invoiceDate.remove();
		}
	};

	// Create item field dinamically
	let nField = 0;
	let n_Selection = 0;
	document.querySelector("#add_item").onclick = () => {
		document.querySelector("#add_item").setAttribute("disabled", "true");
		document.querySelector("#save_invoice").setAttribute("disabled", "true");
		// Name field
		nField++;

		ITEMS[`item_${nField}`] = {};

		const itemName = document.createElement("aside");

		const nameTitle = document.createElement("div");
		const itemInput = document.createElement("input");
		const NameDetails = document.createElement("details");
		const summaryName = document.createElement("summary");
		const nameList = document.createElement("ul");

		nameTitle.innerHTML = "Item Name";

		itemInput.setAttribute("autocomplete", "off");
		itemInput.setAttribute("placeholder", "Item name");
		itemInput.setAttribute("type", "search");
		itemInput.setAttribute("id", `item_input${nField}`);

		summaryName.setAttribute("aria-haspopup", "listbox");

		nameList.setAttribute("id", "item_options");
		nameList.setAttribute("role", "listbox");
		NameDetails.setAttribute("open", "true");

		NameDetails.append(summaryName, nameList);

		itemName.append(nameTitle, itemInput, NameDetails);

		//Quantity field
		const quantityTitle = document.createElement("div");
		const itemQuantity = document.createElement("input");

		itemQuantity.setAttribute("autocomplete", "off");
		itemQuantity.setAttribute("placeholder", "Quantity");
		itemQuantity.setAttribute("type", "number");
		itemQuantity.setAttribute("id", `quantity${nField}`);
		itemQuantity.setAttribute("min", "0");

		quantityTitle.innerHTML = "Quantity";

		const quantityDiv = document.createElement("div");
		quantityDiv.append(quantityTitle, itemQuantity);


		// Unit value field
		const unitValueTitle = document.createElement("div");
		const unitValue = document.createElement("input");
		unitValue.setAttribute("autocomplete", "off");
		unitValue.setAttribute("placeholder", "Unit Value");
		unitValue.setAttribute("type", "text");
		unitValue.setAttribute("id", `unit_value${nField}`)

		unitValueTitle.innerHTML = "Unit Value";

		const unitValueDiv = document.createElement("div");
		unitValueDiv.append(unitValueTitle, unitValue);

		// Subtotal field
		const totalTitle = document.createElement("div");
		const totalValue = document.createElement("input");
		totalValue.setAttribute("autocomplete", "off");
		totalValue.setAttribute("placeholder", "Total");
		totalValue.setAttribute("type", "text");
		totalValue.setAttribute("readonly", "true");
		totalValue.setAttribute("disabled", "true");
		totalValue.setAttribute("id", `total_value${nField}`);

		totalTitle.innerHTML = "Subtotal";

		const totalDiv = document.createElement("div");
		totalDiv.append(totalTitle, totalValue);

		// Save item button
		const saveDiv = document.createElement("div");
		const saveItem = document.createElement("button");
		saveItem.innerHTML = 'Save';
		saveItem.setAttribute("disabled", "true");
		saveItem.setAttribute("id", `save_item${nField}`);
		saveDiv.style.padding = "25px";
		saveDiv.style.marginTop = "5px"
		saveDiv.append(saveItem);

		// Division per item
		const itemGrid = document.createElement("div");
		itemGrid.setAttribute("class", "grid");
		itemGrid.append(itemName, quantityDiv, unitValueDiv, totalDiv, saveDiv);
		document.querySelector("#item_fields").append(itemGrid);


		// Unit value event
		unitValue.onkeyup = () => {
			if (!isNaN(unitValue.value)) {
				totalValue.value = `$ ${String(Number(itemQuantity.value) * 
			Number(unitValue.value))}`;
			}

			if (unitValue.value != '' && unitValue.value > 0) {
				ITEMS[`item_${nField}`]["unit_value"] = unitValue.value;
			} else if (ITEMS[`item_${nField}`]["unit_value"]) {
				delete ITEMS[`item_${nField}`]["unit_value"];
			}
			if (totalValue.value != '' && totalValue.value.slice(2) > 0) {
				ITEMS[`item_${nField}`]["subtotal"] = totalValue.value.slice(2);
			} else if (ITEMS[`item_${nField}`]["subtotal"]) {
				delete ITEMS[`item_${nField}`]["subtotal"];
			}
		};
		// Quantity input events
		const events = ['input', 'change'];
		events.forEach(event => {
			itemQuantity.addEventListener(event, () => {
				totalValue.value = `$ ${String(Number(itemQuantity.value)) * 
					String(Number(unitValue.value))}`;

				if (totalValue.value != '' && totalValue.value.slice(2) > 0) {
					ITEMS[`item_${nField}`]["subtotal"] = totalValue.value.slice(2);
				} else if (ITEMS[`item_${nField}`]["subtotal"]) {
					delete ITEMS[`item_${nField}`]["subtotal"];
				}

				if (itemQuantity.value != '' && itemQuantity.value > 0) {
					ITEMS[`item_${nField}`]["quantity"] = itemQuantity.value;
				} else if (ITEMS[`item_${nField}`]["quantity"]) {
					delete ITEMS[`item_${nField}`]["quantity"];
				}

			})
		});

		itemGrid.onkeyup = () => {
			if (ITEMS[`item_${nField}`] && Object.keys(ITEMS[`item_${nField}`]).length === 4) {
				saveItem.removeAttribute("disabled");

				saveItem.onclick = () => {
					// Create new item purchase into form
					const formLabel = document.createElement("label");
					const formName = document.createElement("input");
					const formQuantity = document.createElement("input");
					const formValue = document.createElement("input");
					const formTotal = document.createElement("input");
					formLabel.setAttribute("for", `item_${nField}`);
					formLabel.setAttribute("hidden", "true");
					formName.setAttribute("name", `name_${nField}`);
					formName.value = ITEMS[`item_${nField}`]["name"];
					formQuantity.setAttribute("name", `quantity_${nField}`);
					formQuantity.value = ITEMS[`item_${nField}`]["quantity"];
					formValue.setAttribute("name", `value_${nField}`);
					formValue.value = ITEMS[`item_${nField}`]["unit_value"];
					formTotal.setAttribute("name", `total_${nField}`);
					formTotal.value = ITEMS[`item_${nField}`]["subtotal"];

					// Append new item purchase into form
					formLabel.append(formName, formQuantity, formValue, formTotal);
					document.querySelector("form").append(formLabel);

					document.querySelector("#item_number").value++;

					// Update Total
					document.querySelector('#total').value = `Total: $${String(
						Number(document.querySelector('#total').value.slice(8)) +
						Number(formTotal.value))}`;

					// Disable current save button
					saveItem.setAttribute("disabled", "true");
					// Enable add item button and save invoice button
					document.querySelector("#add_item").removeAttribute("disabled");

					if (document.querySelector("form").childElementCount > 5) {
						document.querySelector("#save_invoice").removeAttribute("disabled");
					} else {
						document.querySelector("#save_invoice").setAttribute("disabled", "true");
					}

					// Disable inputs after save item
					itemInput.setAttribute("disabled", "true");
					itemQuantity.setAttribute("disabled", "true");
					unitValue.setAttribute("disabled", "true");
				};
				// Disable save button if any input is not filled
				itemInput.addEventListener("keydown", function (event) {
					if (event.key === 'Backspace') {
						saveItem.setAttribute("disabled", "true");
					}
				});
				itemQuantity.addEventListener("keyup", function (event) {
					if (event.key === 'Backspace' || event.key === 'ArrowDown' && itemQuantity.value < 1) {
						saveItem.setAttribute("disabled", "true");
					}
				});
				unitValue.addEventListener("keyup", function (event) {
					if (event.key === 'Backspace' && unitValue.value < 1) {
						saveItem.setAttribute("disabled", "true");
					}
				});
			}
		};

		// Fetch item name from server
		itemInput.addEventListener("input", async function () {
			if (ITEMS[`item_${nField}`]["name"]) {
				delete ITEMS[`item_${nField}`]["name"];
			}
			fetch('/search?item_q=' + itemInput.value)
				.then(response => response.json())
				.then(data => {
					n_Selection++;
					let html = '';
					for (let Name in data) {
						let name = data[Name].name;

						html += `<li><input class="item_option" name="items${n_Selection}" type="radio">`;
						html += `<label">` + name + '</label></li>';
					}
					nameList.innerHTML = html;

					// Visualize item selected
					const itemForm = document.createElement("input");
					document.querySelectorAll(".item_option").forEach(function (option) {
						option.onchange = () => {
							itemInput.value = option.nextSibling.textContent.trim();
							ITEMS[`item_${nField}`]["name"] = itemInput.value;

							if (ITEMS[`item_${nField}`] && Object.keys(ITEMS[`item_${nField}`]).length === 4) {
								saveItem.removeAttribute("disabled");
							}


						};
					});
				})
		});
	};
});