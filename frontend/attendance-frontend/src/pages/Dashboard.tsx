import { useEffect, useState } from "react";
import { Container, Typography, Button } from "@mui/material";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const API_URL = "http://127.0.0.1:5000";

const Dashboard = () => {
  const [user, setUser] = useState<{ email: string; role: string } | null>(null);
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(response.data);
      } catch (error) {
        console.error("Failed to fetch user data", error);
        navigate("/"); // 失敗則導回登入頁
      }
    };

    fetchUser();
  }, [token, navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4">Welcome, {user?.email || "User"}!</Typography>
      <Typography variant="h6">Role: {user?.role}</Typography>
      
      {user?.role === "student" && (
        <Button variant="contained" color="primary" fullWidth onClick={() => navigate("/check-in")}>
          Go to Check-In
        </Button>
      )}
      
      {user?.role === "teacher" && (
        <Button variant="contained" color="secondary" fullWidth onClick={() => navigate("/manage-attendance")}>
          Manage Attendance
        </Button>
      )}
      
      <Button variant="outlined" color="error" fullWidth onClick={handleLogout} style={{ marginTop: 10 }}>
        Logout
      </Button>
    </Container>
  );
};

export default Dashboard;
