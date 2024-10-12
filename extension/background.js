//OAuth Flow for Browser Extensions:
//For a browser extension, we can use the Chrome Identity API, which provides a smoother OAuth flow without redirecting users to external pages.



chrome.identity.getAuthToken({ interactive: true }, function(token) {
    if (chrome.runtime.lastError) {
      console.error(chrome.runtime.lastError);
      return;
    }
    // Use the token to make API requests
    useToken(token);
  });
  
  function useToken(token) {
    // Make API requests to Google Calendar
    fetch('https://www.googleapis.com/calendar/v3/calendars/primary/events', {
      headers: {
        Authorization: 'Bearer ' + token
      }
    })
    .then(response => response.json())
    .then(data => {
      // Process calendar data
      console.log(data);
    })
    .catch(error => console.error('Error:', error));
  }