import { useState, useEffect } from "react";
import {
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  PictureAsPdf,
  History,
  Verified,
  Download,
  Gavel,
  Security,
  CheckCircle,
} from "@mui/icons-material";
import { Project, reportsAPI, API_BASE_URL } from "../api/client";

interface Props {
  projectId: number;
  project: Project;
  onTabChange?: (index: number) => void;
  demoMode?: boolean;
}

function ReportPanel({ projectId, project, demoMode = false }: Props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAuditLogs();
  }, [projectId]);

  const fetchAuditLogs = async () => {
    try {
      const response = await reportsAPI.getAuditLog(projectId);
      setAuditLogs(response.data);
    } catch (err) {
      console.error("Failed to load audit logs", err);
    }
  };

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await reportsAPI.generate(projectId, {});
      setReport(response.data);
      await fetchAuditLogs();
    } catch (err: any) {
      if (demoMode) {
        // In demo mode, simulate successful report generation
        setReport({
          message: "Demo Report generated successfully",
          report_path: null,
          report_hash: "demo-" + Date.now().toString(16),
          isDemo: true,
        });
      } else {
        const errorMessage = err.response?.data?.detail || "Failed to generate forensic report";
        setError(errorMessage);
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: { xs: 2, sm: 3 },
        border: "1px solid",
        borderColor: "divider",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #1a365d 0%, #2c5282 100%)",
          p: { xs: 2.5, sm: 4 },
          color: "white",
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: { xs: 1.5, sm: 2 },
            mb: 2,
          }}
        >
          <Box
            sx={{
              width: { xs: 40, sm: 48 },
              height: { xs: 40, sm: 48 },
              borderRadius: "50%",
              bgcolor: "rgba(198, 151, 73, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <Gavel sx={{ color: "#c69749", fontSize: { xs: 20, sm: 24 } }} />
          </Box>
          <Box>
            <Typography variant={isMobile ? "h6" : "h5"} fontWeight={700}>
              Forensic Report Generation
            </Typography>
            <Typography
              variant="body2"
              sx={{ opacity: 0.85, fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
            >
              Court-admissible documentation with chain of custody
            </Typography>
          </Box>
        </Box>
        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <Chip
            icon={
              <Security
                sx={{
                  color: "#86efac !important",
                  fontSize: { xs: 14, sm: 16 },
                }}
              />
            }
            label="BSA Sec 63"
            size="small"
            sx={{
              bgcolor: "rgba(45, 106, 79, 0.2)",
              color: "#86efac",
              border: "1px solid rgba(134, 239, 172, 0.3)",
              fontWeight: 600,
              fontSize: { xs: "0.65rem", sm: "0.75rem" },
            }}
          />
          <Chip
            icon={
              <CheckCircle
                sx={{
                  color: "#93c5fd !important",
                  fontSize: { xs: 14, sm: 16 },
                }}
              />
            }
            label="SHA-256"
            size="small"
            sx={{
              bgcolor: "rgba(147, 197, 253, 0.15)",
              color: "#93c5fd",
              border: "1px solid rgba(147, 197, 253, 0.3)",
              fontWeight: 600,
              fontSize: { xs: "0.65rem", sm: "0.75rem" },
            }}
          />
        </Box>
      </Box>

      <Box sx={{ p: { xs: 2.5, sm: 4 } }}>
        <Box
          sx={{
            display: "flex",
            gap: { xs: 2, sm: 4 },
            flexDirection: { xs: "column", md: "row" },
          }}
        >
          {/* Left Column - Report Generation */}
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="h6"
              gutterBottom
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                fontWeight: 600,
              }}
            >
              <Verified color="success" /> Report Certification
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Every report generated includes an automated{" "}
              <b>Chain of Custody</b> log, cryptographic file hashes (SHA-256),
              and GPS/time-stamp metadata to ensure evidentiary integrity in
              court proceedings.
            </Typography>

            {/* Compliance Info Box */}
            <Box
              sx={{
                bgcolor: "rgba(26, 54, 93, 0.04)",
                borderRadius: 2,
                p: 2.5,
                mb: 3,
                border: "1px solid",
                borderColor: "divider",
              }}
            >
              <Typography
                variant="subtitle2"
                fontWeight={600}
                color="primary.main"
                gutterBottom
              >
                Bharatiya Sakshya Adhiniyam Compliance
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                component="div"
              >
                • Section 63 - Electronic Evidence Certificate
                <br />
                • Digital Forensics Standards (RFC 3227)
                <br />
                • Chain of Custody Documentation
                <br />• Cryptographic Hash Verification
              </Typography>
            </Box>

            {report ? (
              <Alert
                severity="success"
                sx={{
                  mb: 3,
                  "& .MuiAlert-icon": { alignItems: "center" },
                }}
                icon={<CheckCircle />}
              >
                <Typography variant="subtitle2" fontWeight={600}>
                  {report.isDemo ? "Demo Report Preview Generated!" : "Report generated successfully!"}
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  display="block"
                  sx={{ mb: 1.5 }}
                >
                  Hash: {report.report_hash?.substring(0, 32)}...
                </Typography>
                {report.report_path ? (
                  <Button
                    startIcon={<Download />}
                    href={`${API_BASE_URL.replace("/api", "")}/${report.report_path}`}
                    target="_blank"
                    variant="contained"
                    size="small"
                    sx={{
                      bgcolor: "#2d6a4f",
                      "&:hover": { bgcolor: "#1b4332" },
                    }}
                  >
                    Download PDF Report
                  </Button>
                ) : (
                  <Typography variant="caption" color="text.secondary">
                    (Demo mode - PDF download unavailable)
                  </Typography>
                )}
              </Alert>
            ) : (
              <Button
                variant="contained"
                startIcon={
                  loading ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    <PictureAsPdf />
                  )
                }
                onClick={generateReport}
                disabled={loading}
                fullWidth
                size="large"
                sx={{
                  py: 1.5,
                  bgcolor: "#c69749",
                  color: "#0d1b2a",
                  fontWeight: 700,
                  "&:hover": { bgcolor: "#d4a85a" },
                }}
              >
                {loading
                  ? "Generating Forensic Report..."
                  : "Generate BSA Section 63 Report"}
              </Button>
            )}

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>

          <Divider
            orientation="vertical"
            flexItem
            sx={{ display: { xs: "none", md: "block" } }}
          />

          {/* Right Column - Audit Trail */}
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="h6"
              gutterBottom
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                fontWeight: 600,
              }}
            >
              <History color="primary" /> Forensic Audit Trail
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Live stream of system events for Case <b>{project.case_number}</b>
            </Typography>

            <Box
              sx={{
                bgcolor: "rgba(0,0,0,0.02)",
                borderRadius: 2,
                border: "1px solid",
                borderColor: "divider",
                maxHeight: 350,
                overflow: "auto",
              }}
            >
              <List dense>
                {auditLogs.length > 0 ? (
                  auditLogs.map((log, idx) => (
                    <ListItem
                      key={idx}
                      sx={{
                        borderBottom:
                          idx < auditLogs.length - 1 ? "1px solid" : "none",
                        borderColor: "divider",
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <Verified fontSize="small" color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography
                            variant="subtitle2"
                            fontWeight={600}
                            sx={{
                              textTransform: "uppercase",
                              fontSize: "0.75rem",
                            }}
                          >
                            {log.event_type.replace("_", " ")}
                          </Typography>
                        }
                        secondary={
                          <Typography variant="caption" color="text.secondary">
                            {log.event_description}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem>
                    <ListItemText
                      secondary={
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ textAlign: "center", py: 2 }}
                        >
                          No audit events recorded yet
                        </Typography>
                      }
                    />
                  </ListItem>
                )}
              </List>
            </Box>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
}

export default ReportPanel;
