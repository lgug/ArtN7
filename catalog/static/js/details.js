window.checkFileHash = checkFileHash;
window.getFileInfo = getFileInfo;
window.showSpinner = showSpinner;
window.hideSpinner = hideSpinner;

window.onload = function () {
    let rating = parseInt(document.getElementById('rating').value);
    updateRating(rating);
}

function checkFileHash(file_hash, movie_id) {
    showSpinner();
    document.getElementById(file_hash).disabled = true;

    const body = {
        hash: file_hash,
        "movie_id": movie_id
    }

    let xhttp = new XMLHttpRequest();
    xhttp.onload = function (e) {
        console.log(e.target.response);

        let modal = new bootstrap.Modal(document.getElementById('integrityModal'), {
            keyboard: false
        });
        let modalLabel = document.getElementById("integrityModalLabel");
        let modalText = document.getElementById("integrityResultText");

        hideSpinner();
        let result = JSON.parse(e.target.response);
        if (result['whole']) {
            modalLabel.innerHTML = "File is OK!";
            modalLabel.classList.remove("text-danger");
            modalLabel.classList.add("text-success");
            modalText.innerHTML = "This file has passed the integrity check.";
        } else {
            modalLabel.innerHTML = "File is damaged!!!";
            modalLabel.classList.remove("text-success");
            modalLabel.classList.add("text-danger");
            modalText.innerHTML = "The file has a different hash code and could be corrupted.";
        }
        modal.show();

        document.getElementById(file_hash).disabled = false;
    }
    xhttp.open('POST', "/catalog/check_file_hash")
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send(JSON.stringify(body));
}

function getFileInfo(file_id) {
    showSpinner();
    let xhttp = new XMLHttpRequest();
    xhttp.onload = function (e) {
        let modal = new bootstrap.Modal(document.getElementById('fileInfoModal'), {
            keyboard: false
        });
        hideSpinner();

        const data = JSON.parse(e.target.response);

        let fileSize = document.getElementById("fileInfoFileSize");
        let fileType = document.getElementById("fileInfoFileType");
        let creationDate = document.getElementById("fileInfoCreationDate");
        let lastModifiedDate = document.getElementById("fileInfoLastModifiedDate");
        let resolution = document.getElementById("fileInfoResolution");
        let aspectRatio = document.getElementById("fileInfoAspectRatio");
        let bitrate = document.getElementById("fileInfoBitrate");
        let duration = document.getElementById("fileInfoDuration");
        let frame_rate = document.getElementById("fileInfoFrameRate");
        let codec = document.getElementById("fileInfoCodec");

        fileSize.innerHTML = formatFileSize(data['size']);
        fileType.innerHTML = data['type'];
        creationDate.innerHTML = formatDate(data['created']);
        lastModifiedDate.innerHTML = formatDate(data['last_modified']);
        if (data['weight'] && data['height']) {
            resolution.innerHTML = data['width'] + ' x ' + data['height'];
            resolution.parentElement.hidden = false;
        } else {
            resolution.parentElement.hidden = true;
        }
        if (data['aspectRatio']) {
            aspectRatio.innerHTML = data['aspect_ratio'];
            aspectRatio.parentElement.hidden = false;
        } else {
            aspectRatio.parentElement.hidden = true;
        }
        if (data['bitrate']) {
            bitrate.innerHTML = data['bitrate'] + ' bit/s';
            bitrate.parentElement.hidden = false;
        } else {
            bitrate.parentElement.hidden = true;
        }
        if (data['duration']) {
            duration.innerHTML = formatDuration(data['duration']);
            duration.parentElement.hidden = false;
        } else {
            duration.parentElement.hidden = true;
        }
        if (data['frame_rate']) {
            frame_rate.innerHTML = data['frame_rate']
            frame_rate.parentElement.hidden = false;
        } else {
            frame_rate.parentElement.hidden = true;
        }
        if (data['codec']) {
            codec.innerHTML = data['codec'];
            codec.parentElement.hidden = false;
        } else {
            codec.parentElement.hidden = true;
        }

        modal.show()
    }
    xhttp.open('GET', "/catalog/file_info/" + file_id)
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send();
}

function updateRating(n) {
    document.getElementById('rating').value = n;
    document.getElementsByName('star').forEach(value => {
        if (value.value <= n) {
            value.children[0].src = STAR_FILLED_URL;
        } else {
            value.children[0].src = STAR_EMPTY_URL;
        }
    });
}

function updateRatingAndSave(n, movieId) {
    updateRating(n);

    var formData = new FormData();
    formData.set("rating", n)

    var xhttp = new XMLHttpRequest();
    xhttp.open('POST', "/catalog/update_rating/" + movieId)
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send(formData);
}

function formatDuration(time) {
    let h = "0" + ((time / 3600) | 0);
    let m = "0" + (((time % 3600) / 60) | 0);
    let s = "0" + (((time % 3600) % 60) | 0);
    return h.substr(-2) + ':' + m.substr(-2) + ':' + s.substr(-2);
}

function formatDate(timeFromEpoch) {
    let date = new Date(timeFromEpoch * 1000);
    let month = "0" + (date.getMonth() + 1);
    let hours = "0" + date.getHours();
    let minutes = "0" + date.getMinutes();
    let seconds = "0" + date.getSeconds();
    return date.getDate() + '/' + month.substr(-2) + '/' + date.getFullYear() + ' ' + hours.substr(-2) + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
}

function formatFileSize(size) {
    if (size > Math.pow(1024, 3)) {
        return (size / Math.pow(1024, 3)).toFixed(2) + " GB";
    } else if (size > Math.pow(1024, 2)) {
        return (size / Math.pow(1024, 2)).toFixed(2) + " MB";
    } else if (size > 1024) {
        return (size / 1024).toFixed(2) + " KB";
    } else {
        return (size | 0) + " B";
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