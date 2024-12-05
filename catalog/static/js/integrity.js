async function startHashCheck(movies) {
    await showAllMovies(movies);

    document.getElementById("integrityCheckStart").disabled = true;

    for (let i = 0; i < movies.length; i++) {
        let movie_s = JSON.parse(movies[i]);

        let response = await fetch('/catalog/check_movie_hash/' + movie_s['movie_id'], {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=UTF-8',
                'X-CSRFToken': getCookie("csrftoken")
            },
            body: JSON.stringify(movie_s)
        });

        if (response.ok) {
            let data = await response.json();
            let result = true;
            for (let i = 0; i < data.length; i++) {
                let file = data[i];
                let fileResultTag = document.getElementById(file['expected_hash']);

                fileResultTag.innerHTML = file['whole'] ? VALID : CORRUPTED;
                result = result && file['whole'];
            }

            let movieResultTag = document.getElementById("accordionMovieState" + data[0]['movie_id']);
            movieResultTag.innerHTML = result ? VALID : CORRUPTED;
        } else {
            console.error("Error during the request: " + response.statusText);
        }

        let progressBar = document.getElementById("integrityProgressBar");
        if ((i + 1) / movies.length >= 0.99) {
            progressBar.classList.add("w-100");
        } else if ((i + 1) / movies.length >= 0.75) {
            progressBar.classList.add("w-75");
        } else if ((i + 1) / movies.length >= 0.50) {
            progressBar.classList.add("w-50");
        } else if ((i + 1) / movies.length >= 0.25) {
            progressBar.classList.add("w-25");
        } else {
            progressBar.classList.add("w-0");
        }
    }

    document.getElementById("integrityCheckStart").disabled = false;
    let modal = new bootstrap.Modal(document.getElementById('integrityModal'), {
        keyboard: false
    });
    modal.show();
}

async function loadAccordionRow() {
    let response = await fetch(ACCORDION_ROW);
    return await response.text();
}

async function showAllMovies(movies) {
    let accordionItems = document.getElementById("accordionFlushExample");
    while (accordionItems.firstChild) {
        accordionItems.removeChild(accordionItems.firstChild);
    }

    for (let i = 0; i < movies.length; i++) {
        let movie = JSON.parse(movies[i]);

        let accordion = await loadAccordionRow();
        accordionItems.innerHTML += accordion;
        let accordionTag = accordionItems.children[accordionItems.children.length - 1];

        let accordionHeader = accordionTag.querySelector(".accordion-button");
        let accordionBody = accordionTag.querySelector(".accordion-collapse")

        let movieTitleTag = accordionTag.querySelector("#accordionMovieTitle");
        let movieStateTag = accordionTag.querySelector("#accordionMovieState");
        let movieFilesTag = accordionTag.querySelector("#accordionMovieFiles");

        let targetName = "flush-collapse" + movie['movie_id'];
        accordionHeader.setAttribute("data-bs-target", "#" + targetName);
        accordionHeader.setAttribute("aria-controls", targetName);
        accordionBody.id = targetName;

        movieTitleTag.id = "accordionMovieTitle" + movie['movie_id'];
        movieStateTag.id = "accordionMovieState" + movie['movie_id'];
        movieFilesTag.id = "accordionMovieFiles" + movie['movie_id'];

        movieTitleTag.innerHTML = movie['title'];
        movieStateTag.innerHTML = CHECKING;

        for (let j = 0; j < movie['files'].length; j++) {
            let file = movie['files'][j];

            let fileRow = '<div class="row my-3">' +
                '<div class="col">' + file['file_name'] + '</div>' +
                '<div class="col-auto" id="' + file['file_hash'] + '">' + CHECKING + '</div>' +
                '</div>';

            movieFilesTag.innerHTML += fileRow;
        }
    }
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