let file = null;
let imgSrc = null;

function handleFileChange(event) {
    file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function () {
    imgSrc = reader.result || null;
    document.getElementById("previewImageContainer").innerHTML = `<img src="${imgSrc}" alt="업로드 이미지 미리보기" style="min-width: 25vw; max-width: 30vw;" />`;
    };

    reader.readAsDataURL(file);
    console.log("파일 선택");
}

async function handleUpload() {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://127.0.0.1:5000/artist', {
            method: 'POST',
            body: formData,
        });
        const result = await response.json();
        const artist = result["class_name"];
        console.log(artist);
        // a 태그 없이 페이지 이동
        location.href = './projects.html?' + artist;
    } catch (error) {
        console.error('Error uploading file', error);
    }
}