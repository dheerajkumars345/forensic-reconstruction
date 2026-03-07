import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Chip,
} from "@mui/material";
import { Gavel, Security, Notifications } from "@mui/icons-material";

function Header() {
  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        background:
          "linear-gradient(135deg, #0d1b2a 0%, #1a365d 50%, #2c5282 100%)",
        borderBottom: "3px solid #c69749",
      }}
    >
      <Toolbar sx={{ py: 1 }}>
        {/* Logo/Badge Section */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 2,
            mr: 3,
          }}
        >
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #c69749 0%, #d4a85a 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 2px 8px rgba(198, 151, 73, 0.4)",
            }}
          >
            <Gavel sx={{ color: "#0d1b2a", fontSize: 24 }} />
          </Box>
          <Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                letterSpacing: "0.5px",
                lineHeight: 1.2,
                fontSize: "1.1rem",
              }}
            >
              FORENSIC RECONSTRUCTION
            </Typography>
            <Typography
              variant="caption"
              sx={{
                opacity: 0.85,
                letterSpacing: "2px",
                textTransform: "uppercase",
                fontSize: "0.65rem",
                fontWeight: 500,
              }}
            >
              Crime Scene Analysis System
            </Typography>
          </Box>
        </Box>

        {/* Spacer */}
        <Box sx={{ flexGrow: 1 }} />

        {/* Status Badge */}
        <Chip
          icon={<Security sx={{ color: "#2d6a4f !important", fontSize: 16 }} />}
          label="Section 65B Compliant"
          size="small"
          sx={{
            bgcolor: "rgba(45, 106, 79, 0.15)",
            color: "#86efac",
            border: "1px solid rgba(134, 239, 172, 0.3)",
            fontWeight: 600,
            fontSize: "0.7rem",
            mr: 2,
            "& .MuiChip-icon": {
              color: "#86efac",
            },
          }}
        />

        {/* Notification Icon */}
        <IconButton
          size="small"
          sx={{
            color: "rgba(255,255,255,0.7)",
            "&:hover": {
              color: "#c69749",
              bgcolor: "rgba(198, 151, 73, 0.1)",
            },
          }}
        >
          <Notifications />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
