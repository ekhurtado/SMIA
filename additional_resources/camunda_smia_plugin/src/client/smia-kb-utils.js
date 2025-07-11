/**
 * Default request timeout in milliseconds
 */
const DEFAULT_TIMEOUT = 3000;

/**
 * Checks if a server endpoint is available
 *
 * @param {string} url - The URL of the endpoint to check
 * @param {number} [timeout=DEFAULT_TIMEOUT] - Timeout in milliseconds
 * @returns {Promise<{available: boolean, reason?: string}>} - Promise that resolves to an object containing:
 *   - available: boolean indicating if the server is available
 *   - reason: string explaining why the server is not available (only present when available is false)
 */
export function checkServerAvailability(url, timeout = DEFAULT_TIMEOUT) {
  return new Promise((resolve) => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        resolve({
          available: false,
          reason: `Request timed out after ${timeout}ms`
        });
      }, timeout);

      fetch(url, {
        method: 'HEAD',  // Using HEAD to minimize data transfer
        signal: controller.signal,
        mode: 'cors',
        cache: 'no-cache'
      })
      .then(response => {
        clearTimeout(timeoutId);
        if (response.ok) {
          resolve({
            available: true
          });
        } else {
          resolve({
            available: false,
            reason: `Server responded with status: ${response.status} ${response.statusText}`
          });
        }
      })
      .catch(error => {
        // Catch and handle any fetch errors (network issues, CORS, etc.)
        clearTimeout(timeoutId);
        let reason = 'Unknown network error';

        if (error.name === 'AbortError') {
          reason = `Request aborted after ${timeout}ms timeout`;
        } else if (error instanceof TypeError) {
          reason = 'Network error or CORS issue';
        } else {
          reason = error.message || 'Fetch operation failed';
        }

        console.warn(`Server availability check failed: ${reason}`);
        resolve({
          available: false,
          reason: reason
        });
      });
    } catch (error) {
      // Catch any synchronous errors that might occur
      const reason = error.message || 'Unexpected error occurred';
      console.error(`Unexpected error in server availability check: ${reason}`);
      resolve({
        available: false,
        reason: reason
      });
    }
  });
}

/**
 * Makes a GET request to fetch data from the server
 *
 * @param {string} url - The URL to fetch data from
 * @param {Object} [options={}] - Additional fetch options
 * @param {number} [timeout=DEFAULT_TIMEOUT] - Timeout in milliseconds
 * @returns {Promise<Object>} - Promise that resolves with the response data
 */
export function httpGetData(url, options = {}, timeout = DEFAULT_TIMEOUT) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeout);

  const fetchOptions = {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
      ...options.headers
    },
    signal: controller.signal,
    ...options
  };

  return fetch(url, fetchOptions)
    .then(response => {
      clearTimeout(timeoutId);
      if (!response.ok) {
        return `ERROR: HTTP request failed with status: ${response.status} ${response.statusText}`;
        // throw new Error(`HTTP request failed with status: ${response.status} ${response.statusText}`);
      }

      // const data = response.text();
      // console.log('Response Body:', data);
      // return data;
      return response.text();
      // return response.json();
    })
    .finally(() => {
      clearTimeout(timeoutId);
    });
}
