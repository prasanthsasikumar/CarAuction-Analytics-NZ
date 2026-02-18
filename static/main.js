const socket = io('/console');

socket.on('connect', () => {
  console.log('Connected to console namespace');
});

socket.on('console_output', (data) => {
  // Update the webpage with the console output
  const outputContainer = document.getElementById('console-output');
  outputContainer.innerText += data.output + '\n';
});

socket.on('console_connected', (data) => {
  console.log('Console connected:', data.data);
});

socket.on('disconnect', () => {
  console.log('Disconnected from console namespace');
});

function runScript() {
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/run_script', true);
  xhr.onload = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      // Start running the script
      console.log(xhr.responseText);
    }
  };
  xhr.send();
}
