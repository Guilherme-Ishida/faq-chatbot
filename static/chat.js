const botSvg = `<svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="18" cy="18" r="18" fill="#003087"/>
    <path d="M18 8C15.2 8 13 10.2 13 13C13 15.8 15.2 18 18 18C20.8 18 23 15.8 23 13C23 10.2 20.8 8 18 8Z" fill="white"/>
    <path d="M28 28C28 22.5 23.5 18 18 18C12.5 18 8 22.5 8 28H28Z" fill="white"/>
</svg>`;

const userSvg = `<svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="18" cy="18" r="18" fill="#F5A800"/>
    <path d="M18 8C15.2 8 13 10.2 13 13C13 15.8 15.2 18 18 18C20.8 18 23 15.8 23 13C23 10.2 20.8 8 18 8Z" fill="white"/>
    <path d="M28 28C28 22.5 23.5 18 18 18C12.5 18 8 22.5 8 28H28Z" fill="white"/>
</svg>`;

$(document).ready(function() {
    $("#messageForm").on("submit", function(event) {
        event.preventDefault();

        const date = new Date();
        const str_time = date.getHours() + ":" + String(date.getMinutes()).padStart(2, '0');
        const rawText = $("#text").val().trim();

        if (!rawText) return;

        const $userMsg = $('<div class="message user-message">');
        const $userContent = $('<div class="message-content">');
        $userContent.append($('<div class="bubble">').text(rawText));
        $userContent.append($('<span class="time">').text(str_time));
        $userMsg.append($userContent);
        $userMsg.append($('<div class="msg-avatar">').html(userSvg));

        $("#text").val("");
        $("#messageArea").append($userMsg);
        scrollToBottom();

        const typingHtml = `
            <div class="message bot-message" id="typing">
                <div class="msg-avatar">${botSvg}</div>
                <div class="message-content">
                    <div class="bubble typing-bubble">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>`;
        $("#messageArea").append(typingHtml);
        scrollToBottom();

        $.ajax({
            data: { msg: rawText },
            type: "POST",
            url: "/get",
        }).done(function(data) {
            $("#typing").remove();
            const $botMsg = $('<div class="message bot-message">');
            $botMsg.append($('<div class="msg-avatar">').html(botSvg));
            const $botContent = $('<div class="message-content">');
            $botContent.append($('<div class="bubble">').text(data));
            $botContent.append($('<span class="time">').text(str_time));
            $botMsg.append($botContent);
            $("#messageArea").append($botMsg);
            scrollToBottom();
        });
    });

    function scrollToBottom() {
        const area = document.getElementById("messageArea");
        area.scrollTop = area.scrollHeight;
    }
});
