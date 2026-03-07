import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
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
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState(0);

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
          pt: 2,
          pb: 4,
        }}
      >
        <Container maxWidth="xl">
          {/* Breadcrumbs */}
          <Breadcrumbs
            sx={{
              mb: 3,
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
                "&:hover": { color: "#c69749" },
              }}
              onClick={() => navigate("/projects")}
            >
              <Home sx={{ mr: 0.5, fontSize: 18 }} />
              Cases
            </Link>
            <Typography sx={{ color: "#c69749", fontWeight: 600 }}>
              {project.case_number}
            </Typography>
          </Breadcrumbs>

          {/* Project Header */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "start",
            }}
          >
            <Box>
              <Box
                sx={{ display: "flex", gap: 1.5, mb: 2, alignItems: "center" }}
              >
                <Chip
                  label={project.case_number}
                  sx={{
                    bgcolor: "rgba(198, 151, 73, 0.2)",
                    color: "#c69749",
                    fontWeight: 700,
                    border: "1px solid rgba(198, 151, 73, 0.4)",
                    fontSize: "0.85rem",
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
                  }}
                />
              </Box>
              <Typography
                variant="h4"
                sx={{ fontWeight: 700, mb: 1, maxWidth: 600 }}
              >
                {project.case_title}
              </Typography>
              {project.description && (
                <Typography
                  variant="body1"
                  sx={{ opacity: 0.85, maxWidth: 600, mb: 2 }}
                >
                  {project.description}
                </Typography>
              )}
            </Box>
          </Box>

          {/* Meta Info Cards */}
          <Box sx={{ display: "flex", gap: 4, mt: 3, flexWrap: "wrap" }}>
            {project.location && (
              <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                <Avatar
                  sx={{
                    bgcolor: "rgba(255,255,255,0.1)",
                    width: 36,
                    height: 36,
                  }}
                >
                  <LocationOn sx={{ fontSize: 18 }} />
                </Avatar>
                <Box>
                  <Typography
                    variant="caption"
                    sx={{ opacity: 0.7, display: "block" }}
                  >
                    Location
                  </Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {project.location}
                  </Typography>
                </Box>
              </Box>
            )}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              <Avatar
                sx={{ bgcolor: "rgba(255,255,255,0.1)", width: 36, height: 36 }}
              >
                <Person sx={{ fontSize: 18 }} />
              </Avatar>
              <Box>
                <Typography
                  variant="caption"
                  sx={{ opacity: 0.7, display: "block" }}
                >
                  Examiner
                </Typography>
                <Typography variant="body2" fontWeight={500}>
                  {project.examiner_name}
                </Typography>
              </Box>
            </Box>
            {project.laboratory && (
              <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                <Avatar
                  sx={{
                    bgcolor: "rgba(255,255,255,0.1)",
                    width: 36,
                    height: 36,
                  }}
                >
                  <Science sx={{ fontSize: 18 }} />
                </Avatar>
                <Box>
                  <Typography
                    variant="caption"
                    sx={{ opacity: 0.7, display: "block" }}
                  >
                    Laboratory
                  </Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {project.laboratory}
                  </Typography>
                </Box>
              </Box>
            )}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
              <Avatar
                sx={{ bgcolor: "rgba(255,255,255,0.1)", width: 36, height: 36 }}
              >
                <CalendarMonth sx={{ fontSize: 18 }} />
              </Avatar>
              <Box>
                <Typography
                  variant="caption"
                  sx={{ opacity: 0.7, display: "block" }}
                >
                  Created
                </Typography>
                <Typography variant="body2" fontWeight={500}>
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

      <Container maxWidth="xl" sx={{ mt: -2, pb: 4 }}>
        {/* Tabs */}
        <Paper
          elevation={0}
          sx={{
            mb: 3,
            borderRadius: 2,
            border: "1px solid",
            borderColor: "divider",
            overflow: "hidden",
          }}
        >
          <Tabs
            value={currentTab}
            onChange={(_, newValue) => setCurrentTab(newValue)}
            sx={{
              bgcolor: "white",
              "& .MuiTab-root": {
                py: 2,
                px: 3,
                minHeight: 64,
                "&.Mui-selected": { bgcolor: "rgba(26, 54, 93, 0.04)" },
              },
              "& .MuiTabs-indicator": {
                height: 3,
                borderRadius: "3px 3px 0 0",
              },
            }}
          >
            <Tab
              icon={<CloudUpload />}
              label="Evidence Images"
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab
              icon={<ViewInAr />}
              label="3D Reconstruction"
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab
              icon={<Map />}
              label="GPS Mapping"
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab
              icon={<Straighten />}
              label="Measurements"
              iconPosition="start"
              sx={{ gap: 1 }}
            />
            <Tab
              icon={<Description />}
              label="Generate Report"
              iconPosition="start"
              sx={{ gap: 1 }}
            />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <TabPanel value={currentTab} index={0}>
          <ImageUploadPanel projectId={parseInt(projectId!)} />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <ModelViewer projectId={parseInt(projectId!)} />
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
