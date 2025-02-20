import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import CheckIn from "./pages/CheckIn";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/check-in" element={<CheckIn />} />
      </Routes>
    </Router>
  );
}

export default App;
