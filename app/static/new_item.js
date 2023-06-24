document.addEventListener("DOMContentLoaded", () => {

	document.querySelector("#save_item").setAttribute("disabled", "true");

	document.querySelector(".values").onkeyup = () => {
		if (document.querySelector("form").childElementCount === 6) {
			document.querySelector("#save_item").removeAttribute("disabled");
		} else {
			document.querySelector("#save_item").setAttribute("disabled", "true");
		}
	};
	document.querySelector(".values").onclick = () => {
		if (document.querySelector("form").childElementCount === 6) {
			document.querySelector("#save_item").removeAttribute("disabled");
		} else {
			document.querySelector("#save_item").setAttribute("disabled", "true");
		}
	};



	// Save item name into Session Storage and form
	const name = document.createElement("input");
	document.querySelector("#name").oninput = () => {
		if (document.querySelector("#name").value != '' && isNaN(document.querySelector("#name").value)) {
			name.setAttribute("name", "name");
			name.setAttribute("value", document.querySelector("#name").value);
			name.setAttribute("id", "name_to_send");
			name.setAttribute("hidden", "true");

			document.querySelector("form").append(name);

		} else if (document.querySelector("#name_to_send")) {
			document.querySelector("form").removeChild(name);

		}
	};

	// Save Cost Center into Session Storage and form
	const costCenter = document.createElement("input");
	document.querySelector("#cost_center").onclick = () => {
		if (document.querySelector("#cost_center").value != '') {
			costCenter.setAttribute("name", "cost_center");
			costCenter.setAttribute("value", document.querySelector("#cost_center").value);
			costCenter.setAttribute("id", "cost_center_to_send");
			costCenter.setAttribute("hidden", "true");

			if (document.querySelector("#cost_center").value && document.querySelector("#cost_center").value != 'Cost Center') {
				document.querySelector("form").append(costCenter);
			}
		} else if (document.querySelector("#cost_center_to_send")) {
			document.querySelector("form").removeChild(costCenter);
		}
	};

	// Save Item Format into Session Storage and form
	const format = document.createElement("input");
	document.querySelector("#format").oninput = () => {
		if (document.querySelector("#format").value != '' && !isNaN(document.querySelector("#format").value)) {
			format.setAttribute("name", "format");
			format.setAttribute("value", document.querySelector("#format").value);
			format.setAttribute("id", "format_to_send");
			format.setAttribute("hidden", "true");

			if (document.querySelector("#format").value) {
				document.querySelector("form").append(format);
			}
		} else if (document.querySelector("#format_to_send")) {
			document.querySelector("form").removeChild(format);
		}
	};

	// Save Item unit into Session Storage and form
	const unit = document.createElement("input");
	document.querySelector("#unit").onclick = () => {
		if (document.querySelector("#unit").value != '') {
			unit.setAttribute("name", "unit");
			unit.setAttribute("value", document.querySelector("#unit").value);
			unit.setAttribute("id", "unit_to_send");
			unit.setAttribute("hidden", "true");

			if (document.querySelector("#unit").value) {
				document.querySelector("form").append(unit);
			}
		} else if (document.querySelector("#unit_to_send")) {
			document.querySelector("form").removeChild(unit);
		}
	};

	// Save Item format value into Session Storage and form
	const formatValue = document.createElement("input");
	document.querySelector("#format_value").oninput = () => {
		if (document.querySelector("#format_value").value != '' && !isNaN(document.querySelector("#format_value").value)) {
			formatValue.setAttribute("name", "value");
			formatValue.setAttribute("value", document.querySelector("#format_value").value);
			formatValue.setAttribute("id", "value");
			formatValue.setAttribute("hidden", "true");

			document.querySelector("form").append(formatValue);
		} else if (document.querySelector("#value")) {
			document.querySelector("form").removeChild(formatValue);
		}
	};
});