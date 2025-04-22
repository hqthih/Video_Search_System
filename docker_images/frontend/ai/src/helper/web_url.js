//BACKEND
export const web_url = "/backend";

//SOCKET | DB SERVER
export const socket_url = "/db";

//COMPETITION SUBMISSION SEVER
export const server = "";

//SESSION ID FOR COMPETITION SUBMISSION SEVER
export const session = "";

// Socket.IO configuration
export const socketConfig = {
  // path: "/socket.io",
  // transports: ["websocket", "polling"],
  // reconnection: true,
  // reconnectionAttempts: 5,
  // reconnectionDelay: 1000,
  withCredentials: true,
  extraHeaders: {
    "ngrok-skip-browser-warning": "69420",
  }
};