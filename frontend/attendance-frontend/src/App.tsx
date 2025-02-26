import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import CheckIn from "./pages/CheckIn";
import ManageAttendance from "./pages/ManageAttendance";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/check-in" element={<CheckIn />} />
        <Route path="/manage-attendance" element={<ManageAttendance />} />
      </Routes>
    </Router>
  );
}

export default App;
