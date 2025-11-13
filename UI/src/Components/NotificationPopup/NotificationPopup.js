import React from "react";
import { Snackbar, Alert, Box, CircularProgress } from "@mui/material";
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

/**
 * NotificationPopup
 * - A small, friendly green popup used for transient status messages.
 * - Shows a spinner while `loading` is true, otherwise shows a check icon.
 * - Auto-hides after `autoHideDuration` (defaults to 20000 ms). Also supports manual close via `onClose`.
 */
const NotificationPopup = ({ open, message, loading = false, onClose = () => {}, autoHideDuration = 20000 }) => {
  return (
    <Snackbar
      open={open}
      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      onClose={onClose}
      autoHideDuration={autoHideDuration}
    >
      <Alert
        onClose={onClose}
        severity="success"
        sx={{
          backgroundColor: "#e6f4ea",
          color: "#1b5e20",
          boxShadow: 3,
          borderRadius: 2,
          display: "flex",
          alignItems: "center",
          minWidth: 280,
        }}
        icon={loading ? <CircularProgress size={20} color="success" /> : <CheckCircleIcon fontSize="small" />}
      >
        <Box sx={{ fontWeight: 600 }}>{message}</Box>
      </Alert>
    </Snackbar>
  );
};

export default NotificationPopup;
