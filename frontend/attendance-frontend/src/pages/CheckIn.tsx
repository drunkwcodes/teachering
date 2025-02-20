import { useState, useEffect } from "react";
import { Container, Typography, Button, List, ListItem, ListItemText } from "@mui/material";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

const CheckIn = () => {
  const [attendanceRecords, setAttendanceRecords] = useState<{ id: number; status: string; timestamp: string }[]>([]);
  
  // 取得 JWT Token
  const token = localStorage.getItem("token");

  // 取得學生的點名紀錄
  useEffect(() => {
    const fetchAttendance = async () => {
      try {
        const response = await axios.get(`${API_URL}/attendance/list`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAttendanceRecords(response.data);
      } catch (error) {
        console.error("Failed to fetch attendance records", error);
      }
    };

    fetchAttendance();
  }, [token]);

  // 提交簽到
  const handleCheckIn = async () => {
    try {
      await axios.post(`${API_URL}/attendance/check-in`, {}, { headers: { Authorization: `Bearer ${token}` } });
      alert("Check-in successful!");
      window.location.reload(); // 重新載入以更新紀錄
    } catch (error) {
      alert("Check-in failed");
    }
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom>
        Student Check-In
      </Typography>
      <Button variant="contained" color="primary" fullWidth onClick={handleCheckIn}>
        Check In
      </Button>

      <Typography variant="h6" marginTop={2}>
        Your Attendance Records:
      </Typography>
      <List>
        {attendanceRecords.map((record) => (
          <ListItem key={record.id}>
            <ListItemText primary={`Status: ${record.status}`} secondary={`Time: ${new Date(record.timestamp).toLocaleString()}`} />
          </ListItem>
        ))}
      </List>
    </Container>
  );
};

export default CheckIn;
