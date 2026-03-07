// @ts-nocheck - Disable type checking due to MUI Box sx prop union type complexity
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { Add, Folder, Image as ImageIcon, Delete } from "@mui/icons-material";
import { projectsAPI, Project } from "../api/client";

function ProjectsPage() {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.down("md"));
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);
  const [newProject, setNewProject] = useState({
    case_number: "",
    case_title: "",
    description: "",
    location: "",
    examiner_name: "",
    examiner_id: "",
    laboratory: "",
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.list();
      setProjects(response.data);
    } catch (error) {
      console.error("Error loading projects:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    try {
      const response = await projectsAPI.create(newProject);
      setProjects([response.data, ...projects]);
      setCreateDialogOpen(false);
      setNewProject({
        case_number: "",
        case_title: "",
        description: "",
        location: "",
        examiner_name: "",
        examiner_id: "",
        laboratory: "",
      });
    } catch (error) {
      console.error("Error creating project:", error);
      alert("Failed to create project");
    }
  };

  const handleDeleteProject = async () => {
    if (!projectToDelete) return;
    try {
      await projectsAPI.delete(projectToDelete.id);
      setProjects(projects.filter((p) => p.id !== projectToDelete.id));
      setDeleteDialogOpen(false);
      setProjectToDelete(null);
    } catch (error) {
      console.error("Error deleting project:", error);
      alert("Failed to delete project");
    }
  };

  const openDeleteDialog = (project: Project, e: React.MouseEvent) => {
    e.stopPropagation();
    setProjectToDelete(project);
    setDeleteDialogOpen(true);
  };

  if (loading) {
    return (
      <Container sx={{ py: 4 }}>
        <Typography>Loading projects...</Typography>
      </Container>
    );
  }

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          backgroundColor: "#1a365d",
          color: "white",
          pt: { xs: 3, sm: 5 },
          pb: { xs: 3, sm: 5 },
          mb: { xs: 2, sm: 4 },
        }}
      >
        <Container maxWidth="xl">
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", sm: "row" },
              justifyContent: "space-between",
              alignItems: { xs: "stretch", sm: "center" },
              gap: { xs: 2, sm: 0 },
            }}
          >
            <Box sx={{ textAlign: { xs: "center", sm: "left" } }}>
              <Typography
                variant={isMobile ? "h4" : "h3"}
                sx={{
                  fontWeight: 700,
                  mb: 1,
                  color: "#c69749",
                }}
              >
                Case Management
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  opacity: 0.85,
                  maxWidth: 500,
                  mx: { xs: "auto", sm: 0 },
                  fontSize: { xs: "0.9rem", sm: "1rem" },
                }}
              >
                Manage forensic crime scene reconstruction projects with full
                chain of custody tracking
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
              size={isMobile ? "medium" : "large"}
              fullWidth={isMobile}
              sx={{
                bgcolor: "#c69749",
                color: "#0d1b2a",
                px: { xs: 3, sm: 4 },
                py: { xs: 1.25, sm: 1.5 },
                fontWeight: 700,
                "&:hover": {
                  bgcolor: "#d4a85a",
                },
              }}
            >
              New Case
            </Button>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ pb: { xs: 3, sm: 6 } }}>
        {/* Stats Bar */}
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            gap: { xs: 2, sm: 3 },
            mb: { xs: 3, sm: 4 },
            p: { xs: 2, sm: 2.5 },
            bgcolor: "white",
            borderRadius: 2,
            border: "1px solid",
            borderColor: "divider",
          }}
        >
          <Box
            sx={{ display: "flex", alignItems: "center", gap: 1.5, flex: 1 }}
          >
            <Box
              sx={{
                width: { xs: 36, sm: 40 },
                height: { xs: 36, sm: 40 },
                borderRadius: 1,
                bgcolor: "primary.main",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <Folder sx={{ fontSize: { xs: 20, sm: 24 } }} />
            </Box>
            <Box>
              <Typography
                variant="h5"
                fontWeight={700}
                color="primary.main"
                sx={{ fontSize: { xs: "1.25rem", sm: "1.5rem" } }}
              >
                {projects.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Cases
              </Typography>
            </Box>
          </Box>
          <Box
            sx={{
              borderLeft: { xs: "none", sm: "1px solid" },
              borderTop: { xs: "1px solid", sm: "none" },
              borderColor: "divider",
              pl: { xs: 0, sm: 3 },
              pt: { xs: 2, sm: 0 },
              display: "flex",
              alignItems: "center",
              gap: 1.5,
              flex: 1,
            }}
          >
            <Box
              sx={{
                width: { xs: 36, sm: 40 },
                height: { xs: 36, sm: 40 },
                borderRadius: 1,
                bgcolor: "success.main",
                color: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <ImageIcon sx={{ fontSize: { xs: 20, sm: 24 } }} />
            </Box>
            <Box>
              <Typography
                variant="h5"
                fontWeight={700}
                color="success.main"
                sx={{ fontSize: { xs: "1.25rem", sm: "1.5rem" } }}
              >
                {projects.reduce((acc, p) => acc + (p.image_count || 0), 0)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Evidence Images
              </Typography>
            </Box>
          </Box>
        </Box>

        <Grid container spacing={3}>
          {projects.map((project) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={project.id}>
              <Card
                elevation={0}
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  transition: "all 0.3s ease",
                  border: "1px solid",
                  borderColor: "divider",
                  "&:hover": {
                    transform: "translateY(-4px)",
                    boxShadow: "0 12px 24px rgba(26, 54, 93, 0.12)",
                    borderColor: "primary.light",
                  },
                }}
              >
                {/* Card Header with gradient */}
                <Box
                  sx={{
                    background:
                      "linear-gradient(135deg, #1a365d 0%, #2c5282 100%)",
                    p: 2,
                    color: "white",
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "start",
                    }}
                  >
                    <Chip
                      label={project.case_number}
                      size="small"
                      sx={{
                        bgcolor: "rgba(198, 151, 73, 0.2)",
                        color: "#c69749",
                        fontWeight: 700,
                        border: "1px solid rgba(198, 151, 73, 0.4)",
                      }}
                    />
                    <Chip
                      label={project.status}
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
                        fontWeight: 500,
                        fontSize: "0.7rem",
                      }}
                    />
                  </Box>
                </Box>

                <CardContent sx={{ flexGrow: 1, pt: 2.5 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontWeight: 600, lineHeight: 1.3 }}
                  >
                    {project.case_title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      mb: 2.5,
                      minHeight: 40,
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                      overflow: "hidden",
                    }}
                  >
                    {project.description || "No description provided"}
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 0.5,
                        px: 1.5,
                        py: 0.5,
                        bgcolor: "rgba(26, 54, 93, 0.06)",
                        borderRadius: 1,
                      }}
                    >
                      <ImageIcon
                        fontSize="small"
                        sx={{ color: "primary.main" }}
                      />
                      <Typography variant="caption" fontWeight={600}>
                        {project.image_count || 0}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(project.created_at).toLocaleDateString(
                        "en-IN",
                        {
                          day: "2-digit",
                          month: "short",
                          year: "numeric",
                        },
                      )}
                    </Typography>
                  </Box>
                </CardContent>
                <CardActions sx={{ p: 2, pt: 0, gap: 1 }}>
                  <Button
                    size="medium"
                    onClick={() => navigate(`/projects/${project.id}`)}
                    variant="contained"
                    sx={{
                      bgcolor: "primary.main",
                      "&:hover": { bgcolor: "primary.dark" },
                      flex: 1,
                    }}
                  >
                    Open Case
                  </Button>
                  <Button
                    size="medium"
                    onClick={(e) => openDeleteDialog(project, e)}
                    variant="outlined"
                    color="error"
                    sx={{
                      minWidth: { xs: 40, sm: "auto" },
                      px: { xs: 1, sm: 2 },
                    }}
                  >
                    {isMobile ? (
                      <Delete fontSize="small" />
                    ) : (
                      <>
                        <Delete fontSize="small" sx={{ mr: 0.5 }} /> Delete
                      </>
                    )}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        {projects.length === 0 && (
          <Box
            sx={{
              textAlign: "center",
              py: 10,
              bgcolor: "white",
              borderRadius: 3,
              border: "2px dashed",
              borderColor: "divider",
            }}
          >
            <Folder sx={{ fontSize: 80, color: "grey.300", mb: 2 }} />
            <Typography variant="h5" color="text.secondary" gutterBottom>
              No Cases Found
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Create your first forensic case to begin analysis
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
              sx={{ bgcolor: "#c69749", "&:hover": { bgcolor: "#d4a85a" } }}
            >
              Create First Case
            </Button>
          </Box>
        )}
      </Container>

      {/* Create Project Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        fullScreen={isMobile}
        PaperProps={{
          sx: { borderRadius: isMobile ? 0 : 3 },
        }}
      >
        <DialogTitle
          sx={{
            bgcolor: "primary.main",
            color: "white",
            pb: 2,
          }}
        >
          <Typography variant="h6" fontWeight={600}>
            Create New Forensic Case
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            Enter case details for chain of custody tracking
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              gap: { xs: 2, sm: 2.5 },
              mt: 1,
            }}
          >
            <TextField
              label="Case Number"
              value={newProject.case_number}
              onChange={(e) =>
                setNewProject({ ...newProject, case_number: e.target.value })
              }
              fullWidth
              required
              placeholder="e.g., FIR-2026-001"
              helperText="Unique identifier for legal reference"
            />
            <TextField
              label="Case Title"
              value={newProject.case_title}
              onChange={(e) =>
                setNewProject({ ...newProject, case_title: e.target.value })
              }
              fullWidth
              required
              placeholder="Brief description of the case"
            />
            <TextField
              label="Description"
              value={newProject.description}
              onChange={(e) =>
                setNewProject({ ...newProject, description: e.target.value })
              }
              fullWidth
              multiline
              rows={3}
              placeholder="Detailed case notes..."
            />
            <TextField
              label="Location"
              value={newProject.location}
              onChange={(e) =>
                setNewProject({ ...newProject, location: e.target.value })
              }
              fullWidth
              placeholder="Crime scene address"
            />
            <TextField
              label="Examiner Name"
              value={newProject.examiner_name}
              onChange={(e) =>
                setNewProject({ ...newProject, examiner_name: e.target.value })
              }
              fullWidth
              required
              placeholder="Lead forensic examiner"
            />
            <TextField
              label="Examiner ID"
              value={newProject.examiner_id}
              onChange={(e) =>
                setNewProject({ ...newProject, examiner_id: e.target.value })
              }
              fullWidth
              placeholder="Badge/ID number"
            />
            <TextField
              label="Laboratory"
              value={newProject.laboratory}
              onChange={(e) =>
                setNewProject({ ...newProject, laboratory: e.target.value })
              }
              fullWidth
              placeholder="Forensic Science Laboratory name"
            />
          </Box>
        </DialogContent>
        <DialogActions
          sx={{
            p: { xs: 2, sm: 2.5 },
            gap: 1,
            flexDirection: { xs: "column-reverse", sm: "row" },
          }}
        >
          <Button
            onClick={() => setCreateDialogOpen(false)}
            fullWidth={isMobile}
            sx={{ color: "text.secondary" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreateProject}
            variant="contained"
            fullWidth={isMobile}
            disabled={
              !newProject.case_number ||
              !newProject.case_title ||
              !newProject.examiner_name
            }
            sx={{
              bgcolor: "#c69749",
              color: "#0d1b2a",
              px: 4,
              "&:hover": { bgcolor: "#d4a85a" },
            }}
          >
            Create Case
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box display="flex" alignItems="center" gap={1}>
            <Delete color="error" />
            <Typography variant="h6" fontWeight={600}>
              Delete Case
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" color="text.secondary">
            Are you sure you want to delete case{" "}
            <strong>{projectToDelete?.case_number}</strong>?
          </Typography>
          <Typography variant="body2" color="error" sx={{ mt: 1 }}>
            This action cannot be undone. All evidence, measurements, and
            reports will be permanently deleted.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button
            onClick={() => setDeleteDialogOpen(false)}
            sx={{ color: "text.secondary" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeleteProject}
            variant="contained"
            color="error"
          >
            Delete Case
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ProjectsPage;
