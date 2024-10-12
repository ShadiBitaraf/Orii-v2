///
// This setup ensures that:

// Your client ID is securely stored in the extension.
// Each user goes through their own OAuth flow, managed by Chrome.
// User tokens are securely handled by Chrome, not your extension's code.
// Your backend receives user-specific tokens for API requests.

// Remember, the client ID is public information and is the same for all users of your extension. The security comes from the OAuth flow itself and the proper handling of user-specific tokens.


function getAuthToken(callback) {
    chrome.identity.getAuthToken({ interactive: true }, function(token) {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
        return;
      }
      callback(token);
    });
  }
  
  function makeApiRequest(token) {
    fetch('https://your-backend-api.com/query', { //TODO?
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query: 'Your query here' })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
  }
  
  // Usage
  getAuthToken(function(token) {
    makeApiRequest(token);
  });