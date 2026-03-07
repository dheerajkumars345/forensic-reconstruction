import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Button,
  Breadcrumbs,
  Link,
  Chip,
  CircularProgress,
  Avatar,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  Home,
  CloudUpload,
  ViewInAr,
  Map,
  Straighten,
  Description,
  LocationOn,
  Person,
  Science,
  CalendarMonth,
} from "@mui/icons-material";
import { projectsAPI, Project } from "../api/client";
import ImageUploadPanel from "../components/ImageUploadPanel";
import ModelViewer from "../components/ModelViewer";
import MapView from "../components/MapView";
import MeasurementsPanel from "../components/MeasurementsPanel";
import ReportPanel from "../components/ReportPanel";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
      style={{ display: value === index ? "block" : "none" }}
      {...other}
    >
      {/* Always render children to preserve state */}
      <Box sx={{ p: { xs: 1.5, sm: 3 } }}>{children}</Box>
    </div>
  );
}

function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState(0);

  // Get demo mode from navigation state or localStorage
  const demoMode =
    (location.state as { demoMode?: boolean })?.demoMode ??
    localStorage.getItem("forensic_demo_mode") === "true";

  useEffect(() => {
    if (projectId) {
      loadProject();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const response = await projectsAPI.get(parseInt(projectId!));
      setProject(response.data);
    } catch (error) {
      console.error("Error loading project:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ py: 4, textAlign: "center" }}>
        <CircularProgress />
      </Container>
    );
  }

  if (!project) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography variant="h5" color="error">
          Project not found
        </Typography>
        <Button onClick={() => navigate("/projects")} sx={{ mt: 2 }}>
          Back to Projects
        </Button>
      </Container>
    );
  }

  return (
    <Box sx={{ bgcolor: "background.default", minHeight: "100%" }}>
      {/* Header Section */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #1a365d 0%, #2c5282 100%)",
          color: "white",
          pt: { xs: 1.5, sm: 2 },
          pb: { xs: 3, sm: 4 },
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3 } }}>
          {/* Breadcrumbs */}
          <Breadcrumbs
            sx={{
              mb: { xs: 2, sm: 3 },
              "& .MuiBreadcrumbs-separator": { color: "rgba(255,255,255,0.5)" },
            }}
          >
            <Link
              underline="hover"
              sx={{
                display: "flex",
                alignItems: "center",
                cursor: "pointer",
                color: "rgba(255,255,255,0.7)",
                fontSize: { xs: "0.85rem", sm: "1rem" },
                "&:hover": { color: "#c69749" },
              }}
              onClick={() => navigate("/projects")}
            >
              <Home sx={{ mr: 0.5, fontSize: { xs: 16, sm: 18 } }} />
              Cases
            </Link>
            <Typography
              sx={{
                color: "#c69749",
                fontWeight: 600,
                fontSize: { xs: "0.85rem", sm: "1rem" },
              }}
            >
              {project.case_number}
            </Typography>
          </Breadcrumbs>

          {/* Project Header */}
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              justifyContent: "space-between",
              alignItems: { xs: "flex-start", md: "start" },
              gap: { xs: 2, md: 0 },
            }}
          >
            <Box sx={{ width: "100%" }}>
              <Box
                sx={{
                  display: "flex",
                  gap: 1,
                  mb: 2,
                  alignItems: "center",
                  flexWrap: "wrap",
                }}
              >
                <Chip
                  label={project.case_number}
                  sx={{
                    bgcolor: "rgba(198, 151, 73, 0.2)",
                    color: "#c69749",
                    fontWeight: 700,
                    border: "1px solid rgba(198, 151, 73, 0.4)",
                    fontSize: { xs: "0.75rem", sm: "0.85rem" },
                  }}
                />
                <Chip
                  label={project.status.toUpperCase()}
                  size="small"
                  sx={{
                    bgcolor:
                      project.status === "completed"
                        ? "rgba(45, 106, 79, 0.3)"
                        : "rgba(255,255,255,0.15)",
                    color:
                      project.status === "completed"
                        ? "#86efac"
                        : "rgba(255,255,255,0.9)",
                    fontWeight: 600,
                    fontSize: { xs: "0.65rem", sm: "0.75rem" },
                  }}
                />
              </Box>
              <Typography
                variant={isMobile ? "h5" : "h4"}
                sx={{
                  fontWeight: 700,
                  mb: 1,
                  maxWidth: { xs: "100%", md: 600 },
                }}
              >
                {project.case_title}
              </Typography>
              {project.description && (
                <Typography
                  variant="body1"
                  sx={{
                    opacity: 0.85,
                    maxWidth: { xs: "100%", md: 600 },
                    mb: 2,
                    fontSize: { xs: "0.9rem", sm: "1rem" },
                  }}
                >
                  {project.description}
                </Typography>
              )}
            </Box>
          </Box>

          {/* Meta Info Cards */}
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr 1fr",
                sm: "repeat(auto-fit, minmax(150px, 1fr))",
              },
              gap: { xs: 2, sm: 3, md: 4 },
              mt: 3,
            }}
          >
            {project.location && (
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: { xs: 1, sm: 1.5 },
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: "rgba(255,255,255,0.1)",
                    width: { xs: 32, sm: 36 },
                    height: { xs: 32, sm: 36 },
                  }}
                >
                  <LocationOn sx={{ fontSize: { xs: 16, sm: 18 } }} />
                </Avatar>
                <Box sx={{ minWidth: 0 }}>
                  <Typography
                    variant="caption"
                    sx={{
                      opacity: 0.7,
                      display: "block",
                      fontSize: { xs: "0.65rem", sm: "0.75rem" },
                    }}
                  >
                    Location
                  </Typography>
                  <Typography
                    variant="body2"
                    fontWeight={500}
                    sx={{
                      fontSize: { xs: "0.8rem", sm: "0.875rem" },
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {project.location}
                  </Typography>
                </Box>
              </Box>
            )}
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: { xs: 1, sm: 1.5 },
              }}
            >
              <Avatar
                sx={{
                  bgcolor: "rgba(255,255,255,0.1)",
                  width: { xs: 32, sm: 36 },
                  height: { xs: 32, sm: 36 },
                }}
              >
                <Person sx={{ fontSize: { xs: 16, sm: 18 } }} />
              </Avatar>
              <Box sx={{ minWidth: 0 }}>
                <Typography
                  variant="caption"
                  sx={{
                    opacity: 0.7,
                    display: "block",
                    fontSize: { xs: "0.65rem", sm: "0.75rem" },
                  }}
                >
                  Examiner
                </Typography>
                <Typography
                  variant="body2"
                  fontWeight={500}
                  sx={{
                    fontSize: { xs: "0.8rem", sm: "0.875rem" },
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {project.examiner_name}
                </Typography>
              </Box>
            </Box>
            {project.laboratory && (
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: { xs: 1, sm: 1.5 },
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: "rgba(255,255,255,0.1)",
                    width: { xs: 32, sm: 36 },
                    height: { xs: 32, sm: 36 },
                  }}
                >
                  <Science sx={{ fontSize: { xs: 16, sm: 18 } }} />
                </Avatar>
                <Box sx={{ minWidth: 0 }}>
                  <Typography
                    variant="caption"
                    sx={{
                      opacity: 0.7,
                      display: "block",
                      fontSize: { xs: "0.65rem", sm: "0.75rem" },
                    }}
                  >
                    Laboratory
                  </Typography>
                  <Typography
                    variant="body2"
                    fontWeight={500}
                    sx={{
                      fontSize: { xs: "0.8rem", sm: "0.875rem" },
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {project.laboratory}
                  </Typography>
                </Box>
              </Box>
            )}
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: { xs: 1, sm: 1.5 },
              }}
            >
              <Avatar
                sx={{
                  bgcolor: "rgba(255,255,255,0.1)",
                  width: { xs: 32, sm: 36 },
                  height: { xs: 32, sm: 36 },
                }}
              >
                <CalendarMonth sx={{ fontSize: { xs: 16, sm: 18 } }} />
              </Avatar>
              <Box sx={{ minWidth: 0 }}>
                <Typography
                  variant="caption"
                  sx={{
                    opacity: 0.7,
                    display: "block",
                    fontSize: { xs: "0.65rem", sm: "0.75rem" },
                  }}
                >
                  Created
                </Typography>
                <Typography
                  variant="body2"
                  fontWeight={500}
                  sx={{ fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
                >
                  {new Date(project.created_at).toLocaleDateString("en-IN", {
                    day: "2-digit",
                    month: "short",
                    year: "numeric",
                  })}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ mt: -2, pb: 4, px: { xs: 2, sm: 3 } }}>
        {/* Tabs */}
        <Paper
          elevation={0}
          sx={{
            mb: { xs: 2, sm: 3 },
            borderRadius: 2,
            border: "1px solid",
            borderColor: "divider",
            overflow: "hidden",
          }}
        >
          <Tabs
            value={currentTab}
            onChange={(_, newValue) => setCurrentTab(newValue)}
            variant={isMobile ? "scrollable" : "standard"}
            scrollButtons={isMobile ? "auto" : false}
            allowScrollButtonsMobile
            sx={{
              bgcolor: "white",
              "& .MuiTab-root": {
                py: { xs: 1.5, sm: 2 },
                px: { xs: 1.5, sm: 3 },
                minHeight: { xs: 56, sm: 64 },
                minWidth: { xs: "auto", sm: 120 },
                fontSize: { xs: "0.75rem", sm: "0.875rem" },
                "&.Mui-selected": { bgcolor: "rgba(26, 54, 93, 0.04)" },
              },
              "& .MuiTabs-indicator": {
                height: 3,
                borderRadius: "3px 3px 0 0",
              },
              "& .MuiTabs-scrollButtons": {
                color: "primary.main",
              },
            }}
          >
            <Tab
              icon={<CloudUpload sx={{ fontSize: { xs: 18, sm: 24 } }} />}
              label={isMobile ? "Images" : "Evidence Images"}
              iconPosition="start"
              sx={{ gap: { xs: 0.5, sm: 1 } }}
            />
            <Tab
              icon={<ViewInAr sx={{ fontSize: { xs: 18, sm: 24 } }} />}
              label={isMobile ? "3D" : "3D Reconstruction"}
              iconPosition="start"
              sx={{ gap: { xs: 0.5, sm: 1 } }}
            />
            <Tab
              icon={<Map sx={{ fontSize: { xs: 18, sm: 24 } }} />}
              label={isMobile ? "GPS" : "GPS Mapping"}
              iconPosition="start"
              sx={{ gap: { xs: 0.5, sm: 1 } }}
            />
            <Tab
              icon={<Straighten sx={{ fontSize: { xs: 18, sm: 24 } }} />}
              label={isMobile ? "Measure" : "Measurements"}
              iconPosition="start"
              sx={{ gap: { xs: 0.5, sm: 1 } }}
            />
            <Tab
              icon={<Description sx={{ fontSize: { xs: 18, sm: 24 } }} />}
              label={isMobile ? "Report" : "Generate Report"}
              iconPosition="start"
              sx={{ gap: { xs: 0.5, sm: 1 } }}
            />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <TabPanel value={currentTab} index={0}>
          <ImageUploadPanel
            projectId={parseInt(projectId!)}
            demoMode={demoMode}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <ModelViewer projectId={parseInt(projectId!)} demoMode={demoMode} />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <MapView projectId={parseInt(projectId!)} />
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <MeasurementsPanel
            projectId={parseInt(projectId!)}
            onTabChange={setCurrentTab}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={4}>
          <ReportPanel
            projectId={parseInt(projectId!)}
            project={project}
            onTabChange={setCurrentTab}
          />
        </TabPanel>
      </Container>
    </Box>
  );
}

export default ProjectDetailPage;
