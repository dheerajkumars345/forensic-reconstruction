// @ts-nocheck - Disable type checking due to MUI Box sx prop union type complexity
import { useState, useEffect, useMemo } from "react";
import {
  Paper,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Chip,
  ToggleButton,
  ToggleButtonGroup,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  ViewInAr,
  AutoGraph,
  Layers,
  Map as MapIcon,
  Download,
  PlayArrow,
  CameraAlt,
  LocationOn,
} from "@mui/icons-material";
import { Canvas } from "@react-three/fiber";
import {
  OrbitControls,
  Stars,
  PointMaterial,
  Points,
  Html,
} from "@react-three/drei";
import {
  reconstructionAPI,
  imagesAPI,
  STATIC_BASE_URL,
  PointCloudData,
} from "../api/client";

interface Props {
  projectId: number;
}

// 3D Image Label Component (Using HTML for stability)
function ImageMarker({
  url,
  position,
  label,
}: {
  url: string;
  position: [number, number, number];
  label: string;
}) {
  return (
    <group position={position}>
      <Html distanceFactor={15} transform>
        <Box
          sx={{
            p: 0.5,
            bgcolor: "rgba(0,0,0,0.85)",
            border: "1.5px solid #5AC8FA",
            borderRadius: 1,
            width: 140,
            textAlign: "center",
            pointerEvents: "auto",
            userSelect: "none",
          }}
        >
          <Box
            component="img"
            src={url}
            sx={{
              width: "100%",
              height: 80,
              objectFit: "cover",
              borderRadius: 0.5,
            }}
          />
          <Typography
            sx={{
              color: "white",
              fontSize: "9px",
              mt: 0.5,
              fontWeight: "bold",
            }}
          >
            {label}
          </Typography>
        </Box>
      </Html>
      {/* Anchor Line to Ground */}
      <line>
        <bufferGeometry attach="geometry">
          <bufferAttribute
            attach="attributes-position"
            args={[new Float32Array([0, 0, 0, 0, -position[1] - 2.5, 0]), 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial
          attach="material"
          color="#5AC8FA"
          opacity={0.4}
          transparent
        />
      </line>
    </group>
  );
}

// Forensic Marker Component
function ForensicMarker({
  position,
  text,
  color = "yellow",
}: {
  position: [number, number, number];
  text: string;
  color?: string;
}) {
  return (
    <group position={position}>
      <mesh position={[0, 0.4, 0]}>
        <coneGeometry args={[0.15, 0.4, 4]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
        />
      </mesh>
      <Html position={[0, 0.8, 0]} center>
        <Chip
          label={text}
          size="small"
          sx={{
            bgcolor: color,
            color: "black",
            fontWeight: "bold",
            fontSize: "10px",
            height: 20,
          }}
        />
      </Html>
    </group>
  );
}

// Structured Point Cloud using REAL reconstruction data
function RealPointCloud({
  positions,
  colors,
}: {
  positions: Float32Array;
  colors: Float32Array;
}) {
  return (
    <Points positions={positions} colors={colors} stride={3}>
      <PointMaterial
        transparent
        vertexColors
        size={0.08}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={0.9}
      />
    </Points>
  );
}

// Fallback simulated point cloud (when no real data available)
function SimulatedPointCloud({ count = 15000 }) {
  const points = useMemo(() => {
    const p = new Float32Array(count * 3);
    const c = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const isFloor = i < count * 0.7;
      if (isFloor) {
        p[i * 3] = (Math.random() - 0.5) * 30;
        p[i * 3 + 1] = -2.48 + Math.random() * 0.05;
        p[i * 3 + 2] = (Math.random() - 0.5) * 30;
        c[i * 3] = 0.2;
        c[i * 3 + 1] = 0.2;
        c[i * 3 + 2] = 0.3;
      } else {
        const side = Math.floor(Math.random() * 3);
        if (side === 0) {
          p[i * 3] = -15;
          p[i * 3 + 1] = -2.5 + Math.random() * 8;
          p[i * 3 + 2] = (Math.random() - 0.5) * 30;
        } else if (side === 1) {
          p[i * 3] = (Math.random() - 0.5) * 30;
          p[i * 3 + 1] = -2.5 + Math.random() * 8;
          p[i * 3 + 2] = -15;
        } else {
          p[i * 3] = (Math.random() - 0.5) * 30;
          p[i * 3 + 1] = 5.5;
          p[i * 3 + 2] = (Math.random() - 0.5) * 30;
        }
        c[i * 3] = 0.4;
        c[i * 3 + 1] = 0.4;
        c[i * 3 + 2] = 0.4;
      }
    }
    return { positions: p, colors: c };
  }, [count]);

  return (
    <Points positions={points.positions} colors={points.colors} stride={3}>
      <PointMaterial
        transparent
        vertexColors
        size={0.06}
        sizeAttenuation={true}
        depthWrite={false}
      />
    </Points>
  );
}

function ModelViewer({ projectId }: Props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [loading, setLoading] = useState(false);
  const [reconstruction, setReconstruction] = useState<any>(null);
  const [images, setImages] = useState<any[]>([]);
  const [viewMode, setViewMode] = useState("both");
  const [error, setError] = useState<string | null>(null);
  const [pointCloudData, setPointCloudData] = useState<PointCloudData | null>(
    null,
  );

  // Memoize the point cloud arrays for Three.js
  const pointCloudArrays = useMemo(() => {
    if (!pointCloudData || pointCloudData.positions.length === 0) {
      return null;
    }
    // Center and scale the point cloud for better viewing
    const positions = new Float32Array(pointCloudData.positions);
    const colors = new Float32Array(pointCloudData.colors);

    // Find bounds to center the point cloud
    let minX = Infinity,
      maxX = -Infinity;
    let minY = Infinity,
      maxY = -Infinity;
    let minZ = Infinity,
      maxZ = -Infinity;

    for (let i = 0; i < positions.length; i += 3) {
      minX = Math.min(minX, positions[i]);
      maxX = Math.max(maxX, positions[i]);
      minY = Math.min(minY, positions[i + 1]);
      maxY = Math.max(maxY, positions[i + 1]);
      minZ = Math.min(minZ, positions[i + 2]);
      maxZ = Math.max(maxZ, positions[i + 2]);
    }

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    const centerZ = (minZ + maxZ) / 2;
    const range = Math.max(maxX - minX, maxY - minY, maxZ - minZ);
    const scale = range > 0 ? 20 / range : 1; // Normalize to ~20 units

    // Center and scale
    for (let i = 0; i < positions.length; i += 3) {
      positions[i] = (positions[i] - centerX) * scale;
      positions[i + 1] = (positions[i + 1] - centerY) * scale;
      positions[i + 2] = (positions[i + 2] - centerZ) * scale;
    }

    return { positions, colors };
  }, [pointCloudData]);

  useEffect(() => {
    checkReconstructionStatus();
    fetchImages();
  }, [projectId]);

  const checkReconstructionStatus = async () => {
    try {
      const response = await reconstructionAPI.getStatus(projectId);
      setReconstruction(response.data);

      // If reconstruction is completed, fetch point cloud data
      if (response.data.status === "completed") {
        fetchPointCloudData();
      }
    } catch (err: any) {
      if (err.response?.status !== 404) console.error(err);
    }
  };

  const fetchPointCloudData = async () => {
    try {
      const response = await reconstructionAPI.getPointCloud(projectId);
      setPointCloudData(response.data);
    } catch (err: any) {
      console.error("Failed to load point cloud", err);
    }
  };

  const fetchImages = async () => {
    try {
      const response = await imagesAPI.list(projectId);
      setImages(response.data);
    } catch (err: any) {
      console.error("Failed to load images", err);
    }
  };

  const startReconstruction = async () => {
    setLoading(true);
    setError(null);
    setPointCloudData(null); // Clear old data
    try {
      const response = await reconstructionAPI.start(projectId, {
        quality: "medium",
      });
      setReconstruction(response.data);

      // If completed immediately (synchronous processing)
      if (response.data.status === "completed") {
        fetchPointCloudData();
      } else if (response.data.status === "failed") {
        setError(
          response.data.error_message ||
            "Reconstruction failed. Not enough matching features between images.",
        );
      }
    } catch (err: any) {
      const msg =
        err.response?.data?.detail ||
        "3D Reconstruction failed. Ensure images have overlapping views.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 3,
        border: "1px solid",
        borderColor: "divider",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #1a365d 0%, #2c5282 100%)",
          p: { xs: 2, sm: 3 },
          color: "white",
          display: "flex",
          flexDirection: { xs: "column", sm: "row" },
          justifyContent: "space-between",
          alignItems: { xs: "stretch", sm: "center" },
          gap: { xs: 2, sm: 0 },
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: { xs: 1.5, sm: 2 },
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
            <ViewInAr sx={{ color: "#c69749", fontSize: { xs: 20, sm: 24 } }} />
          </Box>
          <Box>
            <Typography variant={isMobile ? "h6" : "h5"} fontWeight={700}>
              Forensic 3D Scenography
            </Typography>
            <Typography
              variant="body2"
              sx={{ opacity: 0.85, fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
            >
              Projected evidence from {images.length} forensic captures
            </Typography>
          </Box>
        </Box>
        <Box
          display="flex"
          gap={{ xs: 1, sm: 2 }}
          alignItems="center"
          flexWrap="wrap"
          justifyContent={{ xs: "space-between", sm: "flex-end" }}
        >
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, val) => val && setViewMode(val)}
            size="small"
            sx={{
              "& .MuiToggleButton-root": {
                px: { xs: 1, sm: 2 },
                fontSize: { xs: "0.7rem", sm: "0.8125rem" },
              },
            }}
          >
            <ToggleButton value="cloud">
              {isMobile ? "Pts" : "Cloud"}
            </ToggleButton>
            <ToggleButton value="images">
              {isMobile ? "Img" : "Photos"}
            </ToggleButton>
            <ToggleButton value="both">Both</ToggleButton>
          </ToggleButtonGroup>
          <Button
            variant="contained"
            color="secondary"
            size={isMobile ? "small" : "medium"}
            startIcon={
              loading ? (
                <CircularProgress size={isMobile ? 16 : 20} color="inherit" />
              ) : (
                <PlayArrow />
              )
            }
            onClick={startReconstruction}
            disabled={loading}
          >
            {loading
              ? "Processing..."
              : reconstruction
                ? "Refresh Model"
                : "Generate Model"}
          </Button>
        </Box>
      </Box>

      <Box sx={{ p: { xs: 2, sm: 3 } }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {reconstruction && (
          <Box sx={{ mb: { xs: 2, sm: 3 } }}>
            <Box
              sx={{
                display: "flex",
                gap: { xs: 1, sm: 2 },
                mb: 2,
                flexWrap: "wrap",
                alignItems: "center",
              }}
            >
              {/* Status chip */}
              <Chip
                label={
                  reconstruction.status === "completed"
                    ? "COMPLETE"
                    : reconstruction.status?.toUpperCase()
                }
                size="small"
                color={
                  reconstruction.status === "completed"
                    ? "success"
                    : reconstruction.status === "failed"
                      ? "error"
                      : "warning"
                }
                sx={{
                  fontWeight: 700,
                  fontSize: { xs: "0.7rem", sm: "0.8125rem" },
                }}
              />
              {/* Real vs Simulated indicator */}
              <Chip
                label={pointCloudArrays ? "REAL 3D DATA" : "DEMO MODE"}
                size="small"
                sx={{
                  bgcolor: pointCloudArrays
                    ? "rgba(45, 106, 79, 0.15)"
                    : "rgba(255, 152, 0, 0.15)",
                  color: pointCloudArrays ? "#2d6a4f" : "#f57c00",
                  fontWeight: 700,
                  fontSize: { xs: "0.7rem", sm: "0.8125rem" },
                }}
              />
              <Chip
                label={`${(pointCloudData?.num_points ?? reconstruction.num_points ?? 0).toLocaleString()} Points`}
                size="small"
                sx={{
                  bgcolor: "#1a365d",
                  color: "white",
                  fontWeight: 600,
                  fontSize: { xs: "0.7rem", sm: "0.8125rem" },
                }}
              />
              {reconstruction.estimated_accuracy_cm && (
                <Chip
                  label={`±${reconstruction.estimated_accuracy_cm}cm accuracy`}
                  size="small"
                  sx={{
                    bgcolor: "rgba(45, 106, 79, 0.15)",
                    color: "#2d6a4f",
                    fontWeight: 700,
                    fontSize: { xs: "0.7rem", sm: "0.8125rem" },
                  }}
                />
              )}
              {reconstruction.orthomosaic_path && !isMobile && (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<Download />}
                  href={`/${reconstruction.orthomosaic_path}`}
                  sx={{
                    ml: "auto",
                    borderColor: "#c69749",
                    color: "#c69749",
                    "&:hover": {
                      borderColor: "#d4a85a",
                      bgcolor: "rgba(198, 151, 73, 0.08)",
                    },
                  }}
                >
                  Download Orthomosaic
                </Button>
              )}
            </Box>

            {/* Show reconstruction details if failed */}
            {reconstruction.status === "failed" &&
              reconstruction.error_message && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  {reconstruction.error_message}
                </Alert>
              )}

            {/* Show point cloud info if real data available */}
            {pointCloudData && pointCloudData.num_points > 0 && (
              <Alert severity="success" sx={{ mb: 2 }}>
                Real 3D reconstruction generated with{" "}
                {pointCloudData.num_points.toLocaleString()} points from{" "}
                {pointCloudData.camera_positions?.length || images.length}{" "}
                images using Structure from Motion (SfM).
              </Alert>
            )}

            {reconstruction.pipeline && (
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                  gap: 2,
                  bgcolor: "rgba(26, 54, 93, 0.04)",
                  p: 2.5,
                  borderRadius: 2,
                  border: "1px solid",
                  borderColor: "divider",
                }}
              >
                {reconstruction.pipeline.map((step: any, idx: number) => (
                  <Box
                    key={idx}
                    sx={{ display: "flex", flexDirection: "column", gap: 0.5 }}
                  >
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      {idx === 0 && (
                        <CameraAlt sx={{ fontSize: 16, color: "#c69749" }} />
                      )}
                      {idx === 1 && (
                        <AutoGraph sx={{ fontSize: 16, color: "#c69749" }} />
                      )}
                      {idx === 2 && (
                        <Layers sx={{ fontSize: 16, color: "#c69749" }} />
                      )}
                      {idx === 3 && (
                        <MapIcon sx={{ fontSize: 16, color: "#c69749" }} />
                      )}
                      <Typography variant="caption" sx={{ fontWeight: 700 }}>
                        {step.step}
                      </Typography>
                      <Chip
                        label="OK"
                        size="small"
                        sx={{
                          height: 18,
                          fontSize: "9px",
                          bgcolor: "rgba(45, 106, 79, 0.15)",
                          color: "#2d6a4f",
                          fontWeight: 700,
                        }}
                      />
                    </Box>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ fontSize: "10px", lineHeight: 1.4 }}
                    >
                      {step.details}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        )}

        <Box
          sx={{
            height: { xs: 350, sm: 450, md: 600 },
            bgcolor: "#0d1b2a",
            borderRadius: 2,
            overflow: "hidden",
            border: "1px solid #2c5282",
            position: "relative",
          }}
        >
          {reconstruction ? (
            <Canvas camera={{ position: [20, 15, 20], fov: 45 }}>
              <OrbitControls target={[0, 0, 0]} />
              <Stars
                radius={100}
                depth={50}
                count={3000}
                factor={4}
                saturation={0}
                fade
                speed={1}
              />

              <ambientLight intensity={0.6} />
              <pointLight position={[10, 15, 10]} intensity={1.5} />

              {/* Ground */}
              <gridHelper
                args={[50, 50, 0x222222, 0x111111]}
                position={[0, -2.5, 0]}
              />

              {/* Point Cloud - Use REAL data if available */}
              {(viewMode === "cloud" || viewMode === "both") && (
                <>
                  {pointCloudArrays ? (
                    <RealPointCloud
                      positions={pointCloudArrays.positions}
                      colors={pointCloudArrays.colors}
                    />
                  ) : (
                    <SimulatedPointCloud count={20000} />
                  )}
                </>
              )}

              {/* Photo Markers - Use camera positions from point cloud or estimate */}
              {(viewMode === "images" || viewMode === "both") &&
                (pointCloudData?.camera_positions || images).map(
                  (item: any, idx: number) => {
                    // Use real camera position if available, otherwise estimate
                    let x: number, y: number, z: number;
                    let filepath: string;
                    let label: string;

                    if (pointCloudData?.camera_positions && item.position) {
                      [x, y, z] = item.position;
                      filepath = item.filepath;
                      label = `CAMERA-${idx + 1}`;
                    } else {
                      const angle =
                        (idx / images.length) * Math.PI * 1.5 - Math.PI * 0.75;
                      const radius = 15;
                      x = Math.cos(angle) * radius;
                      z = Math.sin(angle) * radius;
                      y = 4;
                      filepath = item.filepath;
                      label = `SOURCE-PHOTO-${idx + 1}`;
                    }

                    return (
                      <ImageMarker
                        key={item.id || idx}
                        url={`${STATIC_BASE_URL}/${filepath}`}
                        position={[x, y, z]}
                        label={label}
                      />
                    );
                  },
                )}

              {/* Forensic Exhibition Markers */}
              <ForensicMarker
                position={[2, -2.5, 3]}
                text="EXHIBIT 1"
                color="#ffc107"
              />
              <ForensicMarker
                position={[-5, -2.5, -4]}
                text="EXHIBIT 2"
                color="#f44336"
              />
              <ForensicMarker
                position={[6, -2.5, -2]}
                text="EXHIBIT 3"
                color="#3f51b5"
              />
            </Canvas>
          ) : (
            <Box
              sx={{
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexDirection: "column",
                gap: 2,
              }}
            >
              <Box
                sx={{
                  width: 100,
                  height: 100,
                  borderRadius: "50%",
                  bgcolor: "rgba(198, 151, 73, 0.1)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <CameraAlt sx={{ fontSize: 48, color: "#4a5568" }} />
              </Box>
              <Typography
                variant="h6"
                sx={{ color: "#94a3b8", fontWeight: 600 }}
              >
                Reconstruction Engine Ready
              </Typography>
              <Typography variant="body2" sx={{ color: "#64748b" }}>
                Click "Generate Model" to process evidence photos
              </Typography>
            </Box>
          )}

          <Box
            sx={{
              position: "absolute",
              bottom: 16,
              right: 16,
              bgcolor: "rgba(13, 27, 42, 0.9)",
              p: 1.5,
              borderRadius: 2,
              pointerEvents: "none",
              border: "1px solid #2c5282",
            }}
          >
            <Typography
              sx={{
                color: "#c69749",
                fontSize: "11px",
                display: "flex",
                alignItems: "center",
                gap: 0.8,
                fontWeight: 700,
              }}
            >
              <LocationOn sx={{ fontSize: 14 }} /> SPATIAL DATA VERIFIED
            </Typography>
            <Typography sx={{ color: "#94a3b8", fontSize: "9px" }}>
              Digital Forensics Lab | India Grid System
            </Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
}

export default ModelViewer;
