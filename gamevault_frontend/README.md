# GameVault Frontend

React frontend for the GameVault digital game marketplace.

## Features

- Browse game catalog
- User authentication (login/register)
- JWT token management with auto-refresh
- Responsive design
- Order management (coming soon)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
# .env file already exists with defaults
REACT_APP_API_URL=http://localhost:8000/api
```

3. Start development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Project Structure

```
src/
├── components/       # Reusable components
│   └── Navbar.js
├── context/          # React Context providers
│   └── AuthContext.js
├── pages/            # Page components
│   ├── GameList.js
│   ├── Login.js
│   └── Register.js
├── services/         # API services
│   └── api.js
├── App.js            # Main app component
└── App.css           # Styles
```

## API Integration

The frontend connects to the Django backend API. Make sure the backend is running at `http://localhost:8000`.

See `src/services/api.js` for API endpoints.

## Authentication

JWT tokens are stored in localStorage and automatically included in API requests. The app handles token refresh automatically.

---

## Available Scripts (Create React App)

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

