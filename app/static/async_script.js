let input = document.querySelector('input');
input.addEventListener('input', async function () {
  fetch('/search?q=' + input.value)
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
          document.querySelector('#search').value = option.nextSibling.textContent.trim();
        };
      });
    });
  //let result = await response.json();
  //let html = '';
  //for (let Name in result) {
  //  let name = result[Name].name;
  //  html += '<li><input name="items" type="radio">' + name + '</input></li>';
  //}

  //document.getElementById('options').innerHTML = html;
});