document.addEventListener('DOMContentLoaded', function () {
    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {

            const cookies = document.cookie.split(';');

            for (let i = 0; i < cookies.length; i++) {

                const cookie = cookies[i].trim();

                if (cookie.substring(0, name.length + 1) === (name + '=')) {

                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }

    const deleteButtons = document.querySelectorAll(".delete-email-btn");
    const csrftoken = getCookie('csrftoken');

    deleteButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();

            const analysisId = button.dataset.analysisId;

            const oldPopup = document.querySelector(".delete-popup-overlay");

            if (oldPopup) {
                oldPopup.remove();
            }

            const popup = document.createElement("div");

            popup.className = "delete-popup-overlay";

            popup.innerHTML = `
                <div class="delete-popup">
                    <p>
                        Do you want to delete analysis
                        <b>${analysisId}</b>?
                    </p>

                    <div class="delete-popup-buttons">

                        <form action="/delete_analysis/${analysisId}/" method="POST">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                            <button type="submit" class="popup-btn confirm-btn">
                                Yes
                            </button>
                        </form>

                        <button class="popup-btn cancel-btn">
                            Cancel
                        </button>

                    </div>
                </div>
            `;

            document.body.appendChild(popup);

            popup.querySelector(".cancel-btn")
                .addEventListener("click", function () {
                    popup.remove();
                });
        });
    });
});