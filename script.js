document.addEventListener("DOMContentLoaded", function () {
    fetch('/list')
        .then(response => response.json())
        .then(data => {
            const listContainer = document.getElementById('list-container');

            data.forEach(item => {
                const listItem = document.createElement('li');
                listItem.textContent = item;
                listContainer.appendChild(listItem);
            });
        })
        .catch(error => console.log(error));
});
