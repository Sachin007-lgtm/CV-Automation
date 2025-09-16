# Frontend Setup

This guide provides instructions for setting up and running the React-based frontend for the CV Automation application.

## Prerequisites

-   Node.js (LTS version recommended)
-   npm or yarn

## 1. Clone the Repository

If you haven't already, clone the project repository to your local machine.

## 2. Install Dependencies

Navigate to the `Frontend` directory and install the required npm packages.

```bash
cd Frontend
npm install
```

## 3. Configure Environment Variables

Create a `.env` file in the `Frontend` directory. This file will store the URL of the backend API.

```env
# The URL of the running backend service
VITE_API_URL=http://localhost:8000
```

Replace `http://localhost:8000` if your backend is running on a different address.

## 4. Run the Development Server

Once the setup is complete, you can start the Vite development server.

```bash
npm run dev
```

This command will start the frontend application, typically on `http://localhost:5173`, and will automatically reload the page when you make changes to the source code.

## 5. Build for Production

When you are ready to deploy the application, you can create a production-ready build.

```bash
npm run build
```

This will create an optimized build of the application in the `dist` directory, which can then be deployed to a static file server or hosting service.
