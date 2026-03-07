import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { Box, CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import ProjectsPage from "./pages/ProjectsPage";
import ProjectDetailPage from "./pages/ProjectDetailPage";
import Header from "./components/Header";

// Professional Forensic Theme
const forensicTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1a365d", // Deep navy blue
      light: "#2c5282",
      dark: "#0d1b2a",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#c69749", // Professional gold
      light: "#d4a85a",
      dark: "#9a7735",
      contrastText: "#000000",
    },
    success: {
      main: "#2d6a4f",
      light: "#40916c",
      dark: "#1b4332",
    },
    error: {
      main: "#9d0208",
      light: "#c1121f",
      dark: "#6a040f",
    },
    warning: {
      main: "#e07b00",
      light: "#f59e0b",
      dark: "#b45309",
    },
    background: {
      default: "#f1f5f9",
      paper: "#ffffff",
    },
    text: {
      primary: "#1e293b",
      secondary: "#64748b",
    },
    divider: "rgba(26, 54, 93, 0.12)",
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: "-0.025em",
    },
    h2: {
      fontWeight: 700,
      letterSpacing: "-0.025em",
    },
    h3: {
      fontWeight: 600,
      letterSpacing: "-0.015em",
    },
    h4: {
      fontWeight: 600,
      letterSpacing: "-0.01em",
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    subtitle1: {
      fontWeight: 500,
    },
    button: {
      fontWeight: 600,
      textTransform: "none",
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "6px",
          padding: "8px 20px",
          boxShadow: "none",
          "&:hover": {
            boxShadow: "0 4px 12px rgba(26, 54, 93, 0.15)",
          },
        },
        contained: {
          "&:hover": {
            transform: "translateY(-1px)",
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
        elevation1: {
          boxShadow: "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)",
        },
        elevation2: {
          boxShadow:
            "0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.04)",
        },
        elevation3: {
          boxShadow:
            "0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04)",
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: "12px",
          border: "1px solid rgba(26, 54, 93, 0.08)",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 500,
          minHeight: "56px",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={forensicTheme}>
      <CssBaseline />
      <Router>
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            minHeight: "100vh",
            bgcolor: "background.default",
          }}
        >
          <Header />
          <Box component="main" sx={{ flexGrow: 1 }}>
            <Routes>
              <Route path="/" element={<Navigate to="/projects" replace />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route
                path="/projects/:projectId"
                element={<ProjectDetailPage />}
              />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
