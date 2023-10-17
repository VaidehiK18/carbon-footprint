const form = document.getElementById('chat-form');
const mytextInput = document.getElementById('mytext');
const responseTextarea = document.getElementById('response');

const API_KEY = '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';

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const mytext = mytextInput.value.trim();

    if (mytext) {
        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${API_KEY}`,
                },
                body: JSON.stringify({
                    "model": "gpt-3.5-turbo",
                    "messages": [
                    {
                    "role": "system",
                    "content": "You will be given a python script Please remove any dead code if it exists."
                    },
                    {
                    "role": "user",
                    "content": "display the optimised python script"
                    }
                    ]
                }),
            });

            if (response.ok) {
                const data = await response.json();
                responseTextarea.value = data.choices[0].message.content;
            } else {
                responseTextarea.value = 'Error: Unable to process your request.';
            }
        } catch (error) {
            console.error(error);
            responseTextarea.value = 'Error: Unable to process your request.';
        }
    }
});