const defaultHeaders = {
  "Content-Type": "application/json",
  "ngrok-skip-browser-warning": "69420",
};

export const fetchWithRetry = async (url, options = {}, retries = 3) => {
  const finalOptions = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, finalOptions);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};

export const get = (url) => {
  return fetchWithRetry(url, {
    method: "GET",
  });
};

export const post = (url, data) => {
  return fetchWithRetry(url, {
    method: "POST",
    body: JSON.stringify(data),
  });
}; 