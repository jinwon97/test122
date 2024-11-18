// 서버 상태 새로고침
document.getElementById("refresh-status").addEventListener("click", () => {
    const statusDiv = document.getElementById("system-status");

    // 서버의 /status 엔드포인트에서 데이터 가져오기
    fetch("http://<server-ip>:5000/status")
        .then((response) => response.text())
        .then((data) => {
            statusDiv.textContent = data;
        })
        .catch((error) => {
            statusDiv.textContent = "Error fetching system status.";
            console.error("Error:", error);
        });
});
