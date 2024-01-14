const getArtworks = async (artist) => {
    try {
        const response = await fetch(`http://127.0.0.1:5000/artworks?artist=${artist}`);

        // 받아온 ZIP 파일을 ArrayBuffer로 변환
        const zipBuffer = await response.arrayBuffer();

        // JSZip 라이브러리를 사용하여 ZIP 파일을 해제
        const zip = new JSZip();
        const zipFile = await zip.loadAsync(zipBuffer);

        // 각 이미지 파일의 Blob을 생성하고, Blob을 URL로 변환하여 저장할 배열
        const urls = [];

        // ZIP 파일 내의 각 파일에 대해 반복
        for (const file in zipFile.files) {
            // 디렉토리가 아닌 경우에만 처리
            if (!zipFile.files[file].dir) {
                // 각 이미지 파일을 Blob으로 변환하고, Blob을 URL로 생성
                const blob = await zipFile.files[file].async("blob");
                const url = await URL.createObjectURL(blob);
                urls.push(url);
            }
        }
        // console.log("test", urls)
        return urls
    } catch (error) {
        console.error('이미지를 가져오는 중 오류 발생', error);
    }
}

// 공백이 %20으로 처리되기 때문에 디코딩
let temp = decodeURIComponent(location.href).split("?");
let artist = temp[1]
// console.log(artist);
console.log(`assets/images/${artist}/${artist}.jpg`);
document.getElementsByClassName("img-fluid")[0].src = `assets/images/${artist}/${artist}.jpg`
document.getElementById("artistName").innerText = artist;


const imageContainer = document.getElementById("artworks");

getArtworks(artist)
    .then(blobUrls => {
        blobUrls.forEach(blobUrl => {
            const imgElement = document.createElement('img');
            imgElement.src = blobUrl;
            imgElement.className = "artwork";
            imgElement.style.minHeight = "80%";
            imgElement.style.marginRight = "2%";
            imageContainer.appendChild(imgElement);
        })
        console.log(blobUrls[0]);
})