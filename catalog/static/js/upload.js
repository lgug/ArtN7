function setNewRating(n) {
    document.getElementById('user_rating').innerHTML = "<strong>" + n + "/10</strong>";
    document.getElementById('rating').value = n;
    document.getElementsByName('star').forEach(value => {
        if (value.value <= n) {
            value.children[0].src = STAR_FILLED_URL;
        } else {
            value.children[0].src = STAR_EMPTY_URL;
        }
    });
}

function imdbAutoFill() {
    showSpinner();

    let imdbId = document.getElementById('imdb_id').value;

    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        hideSpinner();

        let json_response = JSON.parse(this.response)
        document.getElementById("title").value = json_response.title;
        document.getElementById("original_title").value = json_response.original_title;
        document.getElementById("year").value = json_response.year;

        // fill director fields
        let current_directors_tags = document.getElementsByName('directors');
        while (current_directors_tags.length > 0) {
            removeDiv(current_directors_tags[0].parentElement.parentElement.getElementsByTagName('button')[0]);
        }
        json_response.directors.forEach(() => addInput('directors', 'directors_div'));
        let directors_tags = document.getElementsByName('directors');
        for (let i = 0; i < json_response.directors.length; i++) {
            directors_tags[i].value = json_response.directors[i];
        }

        // fill screenwriter fields
        let current_writers_tags = document.getElementsByName('screenwriters');
        while (current_writers_tags.length > 0) {
            removeDiv(current_writers_tags[0].parentElement.parentElement.getElementsByTagName('button')[0]);
        }
        json_response.screenwriters.forEach(() => addInput('screenwriters', 'screenwriters_div'));
        let screenwriters_tags = document.getElementsByName('screenwriters');
        for (let i = 0; i < json_response.screenwriters.length; i++) {
            screenwriters_tags[i].value = json_response.screenwriters[i];
        }

        // fill actor fields
        let current_actor_tags = document.getElementsByName('actors');
        while (current_actor_tags.length > 0) {
            removeDiv(current_actor_tags[0].parentElement.parentElement.getElementsByTagName('button')[0]);
        }
        json_response.actors.forEach(() => addInput('actors', 'actors_div'));
        let actors_tags = document.getElementsByName('actors');
        for (let i = 0; i < json_response.actors.length; i++) {
            actors_tags[i].value = json_response.actors[i];
        }

        // fill country fields
        let current_country_tags = document.getElementsByName('countries');
        while (current_country_tags.length > 0) {
            removeDiv(current_country_tags[0].parentElement.parentElement.getElementsByTagName('button')[0]);
        }
        json_response.countries.forEach(() => addSelect('countries', 'countries_div'));
        let countries_tags = document.getElementsByName('countries');
        for (let i = 0; i < json_response.countries.length; i++) {
            countries_tags[i].value = all_countries_code[json_response.countries[i]];
        }

        // fill genre fields
        let current_genre_tags = document.getElementsByName('genres');
        while (current_genre_tags.length > 0) {
            removeDiv(current_genre_tags[0].parentElement.parentElement.getElementsByTagName('button')[0]);
        }
        json_response.genres.forEach(() => addSelect('genres', 'genres_div'));
        let genres_tags = document.getElementsByName('genres');
        for (let i = 0; i < json_response.genres.length; i++) {
            genres_tags[i].value = json_response.genres[i];
        }

        // simulate the drop of the imdb poster
        const dropArea = document.getElementById('drop-area');
        const dataTransfer = new DataTransfer();
        const file = base64toFile(json_response.poster, "poster.jpg", "image/jpeg")
        dataTransfer.items.add(file);

        const dropEvent = new DragEvent('drop', {
            dataTransfer: dataTransfer,
            bubbles: true,
            cancelable: true
        });
        dropArea.dispatchEvent(dropEvent);
    }
    xhttp.open("GET", "/catalog/imdb_search/" + imdbId);
    xhttp.send();
}

function insertOptionInSelect(value, select) {
    const option = document.createElement('option');
    option.text = value;
    select.add(option);
}

function addInput(name, div_name, placeholder) {
    let container = document.getElementById(div_name);

    let divRow = document.createElement("div");
    divRow.classList.add("row", "my-1");
    let divCol = document.createElement("div");
    divCol.classList.add("col");
    let divColAuto = document.createElement("div");
    divColAuto.classList.add("col-auto");

    let input = document.createElement("input");
    input.type = "text";
    input.name = name;
    input.required = true;
    input.placeholder = placeholder;
    input.classList.add("form-control")

    let removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "Elimina";
    removeButton.classList.add("btn", "btn-danger")
    removeButton.onclick = function () {
        removeDiv(this);
    };

    divCol.appendChild(input);
    divCol.append("\n");
    divColAuto.appendChild(removeButton);

    divRow.appendChild(divCol);
    divRow.appendChild(divColAuto);

    container.appendChild(divRow);
}

function addSelect(name, div_name) {
    let container = document.getElementById(div_name);

    let divRow = document.createElement("div");
    divRow.classList.add("row", "my-1");
    let divCol = document.createElement("div");
    divCol.classList.add("col");
    let divColAuto = document.createElement("div");
    divColAuto.classList.add("col-auto");

    let select = document.createElement("select");
    let removeButton = document.createElement("button");

    select.name = name;
    select.required = true;
    select.classList.add("form-select");
    if (name === "countries") {
        all_countries.forEach(value => insertOptionInSelect(value, select));
    } else if (name === "genres") {
        all_genres.forEach(value => insertOptionInSelect(value, select));
    }

    removeButton.type = "button";
    removeButton.textContent = "Elimina";
    removeButton.classList.add("btn", "btn-danger");
    removeButton.onclick = function () {
        removeDiv(this);
    };

    divCol.appendChild(select);
    divCol.append("\n");
    divColAuto.appendChild(removeButton);

    divRow.appendChild(divCol);
    divRow.appendChild(divColAuto);

    container.appendChild(divRow);
}

function removeDiv(button) {
    button.parentNode.parentNode.parentNode.removeChild(button.parentNode.parentNode);
}

function base64toFile(base64Image, filename, mimeType) {
    const byteCharacters = atob(base64Image);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], {type: mimeType});

    return new File([blob], filename, {type: mimeType});
}


function dragOverHandler(event) {
    event.preventDefault();
}

function dropHandler(event) {
    event.preventDefault();

    const files = event.dataTransfer.files;
    const file = files[0];

    if (file.type.startsWith('image/')) {
        const reader = new FileReader();

        reader.onload = function (e) {
            const previewImage = document.getElementById('preview-image');
            const inputBase64 = document.getElementById('poster');

            previewImage.src = e.target.result;
            inputBase64.value = e.target.result;
            previewImage.classList.remove('hidden');
        };

        reader.readAsDataURL(file);
    }
}

function updateTable(file_name, file_size, file_type) {
    var table = document.getElementById('file-table-tbody');
    var row = table.insertRow(-1);
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);

    cell1.innerHTML = file_name;
    cell1.classList.add("align-middle");

    cell2.innerHTML = file_size;
    cell2.classList.add("align-middle");

    cell3.innerHTML = file_type;
    cell3.classList.add("align-middle");

    var deleteBtn = document.createElement('button');
    deleteBtn.innerHTML = 'Elimina';
    deleteBtn.classList.add("btn", "btn-danger")
    deleteBtn.addEventListener('click', function (event) {
        event.preventDefault();
        var xhttp = new XMLHttpRequest();
        xhttp.onload = function () {
            var row = deleteBtn.parentNode.parentNode;
            row.parentNode.removeChild(row);
        }
        xhttp.open("GET", "/catalog/remove_temp_file/" + file_name);
        xhttp.send();
    });
    cell4.appendChild(deleteBtn);
    cell4.classList.add("align-middle");
}


// Common code functions
function getCookie(c_name) {
    let c_start;
    let c_end;
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start !== -1) {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end === -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

function showSpinner() {
    document.getElementById("pageSpinner").hidden = false;
}

function hideSpinner() {
    document.getElementById("pageSpinner").hidden = true;
}


function sendForm(action) {
    console.log(action);
    let title = document.mUpload.title.value;
    let original_title = document.mUpload.original_title.value;
    let saga = document.mUpload.saga.value;
    let year = document.mUpload.year.value;
    let poster = document.mUpload.poster.value;
    let imdbId = document.mUpload.imdb_id.value;
    let rating = document.mUpload.rating.value;

    let directors = getFormValues(document.mUpload.directors);
    let actors = getFormValues(document.mUpload.actors);
    let screenwriters = getFormValues(document.mUpload.screenwriters);
    let genres = getFormValues(document.mUpload.genres);
    
    console.log(imdbId);
    document.mUpload.action = action;
    document.mUpload.submit();
}

function getFormValues(element) {
    let result = [];
    if (element.value) {
        result.push(element.value);
    } else if (element.values) {
        result = [...element.values()].map(v => v.value);
    }

    return result;
}