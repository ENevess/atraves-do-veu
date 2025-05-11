
async function enviarMensagem() {
    const input = document.getElementById("mensagem").value;
    const respostaDiv = document.getElementById("resposta");
    respostaDiv.innerText = "Consultando o Oráculo...";

    try {
        const resposta = await fetch("/oraculo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensagem: input })
        });

        const data = await resposta.json();
        const texto = data.resposta || "O Oráculo não respondeu.";
        respostaDiv.innerText = texto;

        // Leitura em voz alta
        const utterance = new SpeechSynthesisUtterance(texto);
        utterance.lang = 'pt-BR';
        speechSynthesis.speak(utterance);

    } catch (error) {
        respostaDiv.innerText = "Erro ao consultar o Oráculo.";
    }
}
