document.addEventListener("DOMContentLoaded", function () {
    const timerElement = document.getElementById("timer");
    const quizForm = document.getElementById("quiz-form");
    if (!timerElement || !quizForm) {
        return;
    }

    // Read timer seconds from the element's data attribute if provided
    const dataSeconds = parseInt(timerElement.dataset.seconds, 10);
    let secondsLeft = Number.isFinite(dataSeconds) ? dataSeconds : 120;
    timerElement.textContent = formatTime(secondsLeft);

    const countdown = setInterval(() => {
        secondsLeft -= 1;
        timerElement.textContent = formatTime(secondsLeft);
        if (secondsLeft <= 0) {
            clearInterval(countdown);
            timerElement.textContent = "00:00";
            quizForm.submit();
        }
    }, 1000);

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainder = seconds % 60;
        return `${minutes.toString().padStart(2, "0")}:${remainder.toString().padStart(2, "0")}`;
    }
});
