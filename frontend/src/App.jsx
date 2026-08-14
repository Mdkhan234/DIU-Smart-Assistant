import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import ChatPage from "./pages/ChatPage";
import AdminDashboard from "./pages/AdminDashboard";
import AdminDocuments from "./pages/AdminDocuments";

import "./App.css";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* USER */}

        <Route
          path="/"
          element={<ChatPage />}
        />

        <Route
          path="/chat"
          element={<ChatPage />}
        />


        {/* ADMIN */}

        <Route
          path="/admin"
          element={<AdminDashboard />}
        />

        <Route
          path="/admin/documents"
          element={<AdminDocuments />}
        />


        {/* FALLBACK */}

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;