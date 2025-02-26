import { useState, useEffect } from "react";
import { Container, Typography, Button, List, ListItem, ListItemText } from "@mui/material";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

const ManageAttendance = () => {
  const [attendanceRequests, setAttendanceRequests] = useState<{ id: number; student_email: string; status: string; timestamp: string }[]>([]);
  const token = localStorage.getItem("token");

  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        const response = await axios.get(`${API_URL}/attendance/all`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAttendanceRequests(response.data);
      } catch (error) {
        console.error("Failed to fetch attendance requests", error);
      }
    };

    fetchAttendance();
  }, [token]);

  const updateAttendanceStatus = async (id: number, status: "approved" | "rejected") => {
    try {
      await axios.post(
        `${API_URL}/attendance/update`,
        { id, status },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`Attendance ${status}!`);
      setAttendanceRequests((prev) =>
        prev.map((item) => (item.id === id ? { ...item, status } : item))
      );
    } catch (error) {
      alert("Failed to update attendance");
    }
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom>
        Manage Attendance
      </Typography>
      <List>
        {attendanceRequests.map((request) => (
          <ListItem key={request.id}>
            <ListItemText
              primary={`Student: ${request.student_email}`}
              secondary={`Status: ${request.status} | Time: ${new Date(request.timestamp).toLocaleString()}`}
            />
            {request.status === "pending" && (
              <>
                <Button color="success" onClick={() => updateAttendanceStatus(request.id, "approved")}>
                  Approve
                </Button>
                <Button color="error" onClick={() => updateAttendanceStatus(request.id, "rejected")}>
                  Reject
                </Button>
              </>
            )}
          </ListItem>
        ))}
      </List>
    </Container>
  );
};

export default ManageAttendance;
