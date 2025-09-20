import React from "react";

const Notification = ({ notifications }) => {
  return (
    <div
      style={{
        position: "fixed",
        bottom: "10px",
        right: "10px",
        zIndex: 1000,
        width: "300px",
        display: "flex",
        flexDirection: "column-reverse",
        gap: "10px",
      }}
    >
      {notifications.map((notification) => (
        <div
          key={notification.id}
          style={{
            backgroundColor: notification.type === "success" ? "#4caf50" : "#f44336",
            color: "#fff",
            padding: "10px",
            borderRadius: "5px",
            boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
          }}
        >
          {notification.message}
        </div>
      ))}
    </div>
  );
};

export default Notification;
