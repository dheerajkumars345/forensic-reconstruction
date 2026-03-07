import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Chip,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { Gavel, Security, Notifications } from "@mui/icons-material";

function Header() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.down("md"));

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
      <Toolbar sx={{ py: isMobile ? 0.5 : 1, minHeight: { xs: 56, sm: 64 } }}>
        {/* Logo/Badge Section */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: { xs: 1, sm: 2 },
            mr: { xs: 1, sm: 3 },
          }}
        >
          <Box
            sx={{
              width: { xs: 36, sm: 44 },
              height: { xs: 36, sm: 44 },
              borderRadius: "50%",
              background: "linear-gradient(135deg, #c69749 0%, #d4a85a 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 2px 8px rgba(198, 151, 73, 0.4)",
              flexShrink: 0,
            }}
          >
            <Gavel sx={{ color: "#0d1b2a", fontSize: { xs: 18, sm: 24 } }} />
          </Box>
          <Box sx={{ minWidth: 0 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                letterSpacing: "0.5px",
                lineHeight: 1.2,
                fontSize: { xs: "0.85rem", sm: "1rem", md: "1.1rem" },
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {isMobile ? "FORENSIC" : "FORENSIC RECONSTRUCTION"}
            </Typography>
            {!isMobile && (
              <Typography
                variant="caption"
                sx={{
                  opacity: 0.85,
                  letterSpacing: { xs: "1px", sm: "2px" },
                  textTransform: "uppercase",
                  fontSize: { xs: "0.55rem", sm: "0.65rem" },
                  fontWeight: 500,
                  display: "block",
                }}
              >
                Crime Scene Analysis System
              </Typography>
            )}
          </Box>
        </Box>

        {/* Spacer */}
        <Box sx={{ flexGrow: 1 }} />

        {/* Status Badge - Hide on very small screens */}
        {!isMobile && (
          <Chip
            icon={
              <Security sx={{ color: "#2d6a4f !important", fontSize: 16 }} />
            }
            label={isTablet ? "65B Compliant" : "Section 65B Compliant"}
            size="small"
            sx={{
              bgcolor: "rgba(45, 106, 79, 0.15)",
              color: "#86efac",
              border: "1px solid rgba(134, 239, 172, 0.3)",
              fontWeight: 600,
              fontSize: { xs: "0.6rem", sm: "0.7rem" },
              mr: { xs: 1, sm: 2 },
              "& .MuiChip-icon": {
                color: "#86efac",
              },
            }}
          />
        )}

        {/* Mobile compliance indicator */}
        {isMobile && (
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              bgcolor: "#86efac",
              mr: 1.5,
              boxShadow: "0 0 6px rgba(134, 239, 172, 0.5)",
            }}
            title="Section 65B Compliant"
          />
        )}

        {/* Notification Icon */}
        <IconButton
          size="small"
          sx={{
            color: "rgba(255,255,255,0.7)",
            p: { xs: 0.75, sm: 1 },
            "&:hover": {
              color: "#c69749",
              bgcolor: "rgba(198, 151, 73, 0.1)",
            },
          }}
        >
          <Notifications sx={{ fontSize: { xs: 20, sm: 24 } }} />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
