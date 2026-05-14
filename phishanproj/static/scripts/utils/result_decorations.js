document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById("copy-analysis-btn");
    btn.addEventListener("click", function () {
        const text = document
            .getElementById("analysis-id")
            .innerText;
        copyText(text)
            .then(() => {
                const popup = document.createElement("div");
                popup.className = "copy-popup";
                popup.innerText = "Copied!";

                document.body.appendChild(popup);
                setTimeout(() => {
                    popup.classList.add("show");
                }, 10);
                setTimeout(() => {
                    popup.classList.remove("show");
                    setTimeout(() => {
                        popup.remove();
                    }, 1000);
                }, 2000);
            })
            .catch(err => {
                console.error("Copy failed:", err);
            });
    });

    const spoilerBtn = document.getElementById("email-spoiler-btn");
    const emailInfo = document.getElementById("email-info");

    const spoilers = document.querySelectorAll(".spoiler-text");

    spoilers.forEach(spoiler => {
        spoiler.addEventListener("click", function () {
            spoiler.classList.add("revealed");
        });
    });
    
    function copyText(text) {

        if (navigator.clipboard && window.isSecureContext) {

            return navigator.clipboard.writeText(text);

        } else {

            return new Promise((resolve, reject) => {

                const textArea = document.createElement("textarea");

                textArea.value = text;

                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";

                document.body.appendChild(textArea);

                textArea.focus();
                textArea.select();

                try {

                    document.execCommand("copy");

                    textArea.remove();

                    resolve();

                } catch (err) {

                    textArea.remove();

                    reject(err);

                }

            });

        }

    }
});