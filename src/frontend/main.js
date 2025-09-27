const apiUrl = 'http://petl-load-balancer-117145253.us-east-1.elb.amazonaws.com:80';

const editorTextArea = document.getElementById('editorTextArea');
const csvTextArea = document.getElementById('currentCsvTextArea');
const historySelect = document.getElementById('historySelect');
const runButton = document.getElementById('runButton');
const outputTextArea = document.getElementById('outputTextArea');


runButton.addEventListener('click', async () => {
    submitButton.disabled = true;
    statusMessage.textContent = 'Loading...';

    const interpretPostRequest = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({input: editorTextArea.value})
    };

    try {
        const response = await fetch(interpretPostRequest);
        const data = await response.json();
        outputTextArea.value = data.result;
    } catch (error) {
        outputTextArea.value = error.message;
    } finally {
        submitButton.disabled = false;
    }
});

