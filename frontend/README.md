# Thoughts Frontend

Lightweight, vanilla JavaScript Single Page Application (SPA) for the Thoughts API.

## 🛠️ Technology stack
| Technology | Usage |
|-|-|
| HTML5 | Semantic markup |
| CSS3 | Custom styling |
| Vanilla JavaScript | ES6+ with native ES Modules (no build tools like Webpack/Vite) |
| Fetch API | For all network requests to the backend |
| LocalStorage | For secure JWT access and refresh token management |

## 🏗️ Architecture
The frontend is organized by responsibility:
- `index.html`: The main entry point and modal structures.
- `css/style.css`: Global styles and component styling.
- `js/main.js`: Core application logic, DOM manipulation, and routing-like state management.
- `js/auth.js`: Authentication flows (login, registration, email verification).
- `js/api.js`: Centralized API communication layer (handles headers, token injection, and error parsing).

## 🚀 How to Run

Since the project uses ES Modules (`type="module"`), it **cannot** be opened directly via the `file://` protocol. You must serve it via a local HTTP server.

**Option 1: VS Code Live Server (Recommended)**
1. Open the `frontend` folder in VS Code.
2. Install the "Live Server" extension.
3. Right-click `index.html` and select "Open with Live Server".

**Option 2: Python (from the project root)**
```bash
python -m http.server 5500 --directory frontend
```

Then open http://localhost:5500 in your browser.

# 🔐 Authentication Flow

1. User registers via POST /auth/register.
2. Backend sends a verification email. 
3. User verifies email via the link. 
4. User logs in, receiving access_token and refresh_token. 
5. Tokens are stored in localStorage. The access_token is automatically attached to all protected requests via the getAuthHeaders() helper in api.js.