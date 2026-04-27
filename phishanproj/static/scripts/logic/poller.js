document.addEventListener('DOMContentLoaded', function () {
    var links = document.getElementsByClassName('block-type-link');
    var attachments = document.getElementsByClassName('block-type-attachment');
    
    async function pollStatus() {
        console.log('Poll')
        const res = await fetch(`/api/get-status/${EMAIL_ID}`);
        const data = await res.json();

        updateEmail(data.analysis_status);
        updateLinks(data.link_statuses);
        updateAttachments(data.attachment_statuses);

        if (data.analysis_status.status !== 'FN') {
            setTimeout(pollStatus, 3000);
        }
    }

    function updateEmail(data) {
        statbar = document.getElementById('status-bar');
        riskbar = document.getElementById('score-bar');

        if (data.status == 'UP') {
            statbar.innerHTML = 'Status: pending...';
        } else {
            statbar.innerHTML = 'Status: analysis finished';
            if (data.score == 0) {
                riskbar.innerHTML = `Risk score: <a style="color:green">${data.score} | safe</a>`;
            } else if (data.score < 5) {
                riskbar.innerHTML = `Risk score: <a style="color:yellow">${data.score} | suspicious</a>`;
            } else {
                riskbar.innerHTML = `Risk score: <a style="color:red">${data.score} | dangerous</a>`;
            };
        };
    }

    function updateLinks(data) {
        links = document.querySelectorAll('.block-type-link');

        links.forEach(link => {
            link_id = link.getAttribute('link-id');
            
            link_data = data[link_id];

            if (link_data.status == 'FN') {
                if (link_data.score == 0) {
                    link.innerHTML = `<div class="detail-decoration" style="background-color:green"></div>
                            <p>Risk score: <a style="color:green">0 | safe</a></p>`;
                } else if (link_data.score < 5) {
                    link.innerHTML = `<div class="detail-decoration" style="background-color:yellow"></div>
                            <p>Risk score: <a style="color:yellow">${link_data.score} | suspicious</a></p>`;
                } else {
                    link.innerHTML = `<div class="detail-decoration" style="background-color:red"></div>
                            <p>Risk score: <a style="color:red">${link_data.score} | dangerous</a></p>`;
                }
            };
        });
    }

    function updateAttachments(data) {
        atts = document.querySelectorAll('.block-type-attachment');

        atts.forEach(attachment => {
            attachment_id = attachment.getAttribute('attachment-id');
            
            att_data = data[attachment_id];

            if (att_data.status == 'FN') {
                if (att_data.score == 0) {
                    attachment.innerHTML = `<div class="detail-decoration" style="background-color:green"></div>
                            <p>Risk score: <a style="color:green">0 | safe</a></p>`;
                } else if (att_data.score < 5) {
                    attachment.innerHTML = `<div class="detail-decoration" style="background-color:yellow"></div>
                            <p>Risk score: <a style="color:yellow">${att_data.score} | suspicious</a></p>`;
                } else {
                    attachment.innerHTML = `<div class="detail-decoration" style="background-color:red"></div>
                            <p>Risk score: <a style="color:red">${att_data.score} | dangerous</a></p>`;
                }
            };
        });
    }

    pollStatus();
});