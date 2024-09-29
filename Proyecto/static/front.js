const chatLog = document.getElementById("chat-log");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const voiceBtn = document.getElementById("voice-btn");


window.onload = function() {
    addMessage("Tunja", "Hola, soy Tunja Mural. ¿Qué quieres preguntarme?");
    speak("Hola, soy Tunja Mural. ¿Qué quieres preguntarme?");
};


sendBtn.addEventListener("click", () => {
    const question = userInput.value;
    if (question) {
        addMessage("Usuario", question);
        sendToBackend(question);
        userInput.value = "";
    }
});

voiceBtn.addEventListener("click", () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "es-ES";
    recognition.start();
    recognition.onresult = (event) => {
        const question = event.results[0][0].transcript;
        addMessage("Usuario", question);
        sendToBackend(question);
    };
});

function addMessage(sender, message) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message");
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatLog.appendChild(msgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function sendToBackend(question) {
    axios.post("/ask", { question })
        .then(response => {
            const answer = response.data.answer;
            addMessage("Tunja", answer);
            speak(answer);

            // Verifica si hay que recargar la página
            if (response.data.reload) {
                location.reload(); // Recarga la página
            }
        })
        .catch(error => {
            addMessage("Tunja", "Lo siento, no pude procesar tu pregunta.");
            speak("Lo siento, no pude procesar tu pregunta.");
        });
}


function speak(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "es-ES";
    synth.speak(utterance);
}
