// @ts-nocheck - Disable type checking due to MUI Box sx prop union type complexity
import { useState, useCallback, useEffect } from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CircularProgress,
  Chip,
  Paper,
  LinearProgress,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { CloudUpload, PhotoLibrary, Verified } from "@mui/icons-material";
import { useDropzone } from "react-dropzone";
import { imagesAPI, STATIC_BASE_URL } from "../api/client";

interface Props {
  projectId: number;
}

function ImageUploadPanel({ projectId }: Props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [uploading, setUploading] = useState(false);
  const [images, setImages] = useState<any[]>([]);

  useEffect(() => {
    fetchImages();
  }, [projectId]);

  const fetchImages = async () => {
    try {
      const response = await imagesAPI.list(projectId);
      setImages(response.data);
    } catch (error) {
      console.error("Error fetching images:", error);
    }
  };

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setUploading(true);
      try {
        const formData = new FormData();
        acceptedFiles.forEach((file) => {
          formData.append("files", file);
        });

        await imagesAPI.upload(projectId, formData);
        await fetchImages();
        alert(`Successfully uploaded ${acceptedFiles.length} images`);
      } catch (error) {
        console.error("Upload error:", error);
        alert("Failed to upload images");
      } finally {
        setUploading(false);
      }
    },
    [projectId],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".tif", ".tiff"] },
  });

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 2, sm: 4 },
        borderRadius: { xs: 2, sm: 3 },
        border: "1px solid",
        borderColor: "divider",
      }}
    >
      {/* Header */}
      <Box sx={{ mb: { xs: 2.5, sm: 4 } }}>
        <Typography
          variant={isMobile ? "h6" : "h5"}
          fontWeight={600}
          color="primary.main"
          gutterBottom
        >
          Evidence Image Upload
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
        >
          Upload crime scene photographs for photogrammetric analysis and 3D
          reconstruction
        </Typography>
      </Box>

      {/* Upload Zone */}
      <Box
        {...getRootProps()}
        sx={{
          border: "2px dashed",
          borderColor: isDragActive ? "primary.main" : "divider",
          borderRadius: { xs: 2, sm: 3 },
          p: { xs: 3, sm: 6 },
          textAlign: "center",
          bgcolor: isDragActive ? "rgba(26, 54, 93, 0.04)" : "rgba(0,0,0,0.01)",
          cursor: "pointer",
          mb: { xs: 3, sm: 4 },
          transition: "all 0.2s ease",
          "&:hover": {
            borderColor: "primary.light",
            bgcolor: "rgba(26, 54, 93, 0.02)",
          },
        }}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <Box>
            <CircularProgress size={isMobile ? 36 : 48} sx={{ mb: 2 }} />
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ fontSize: { xs: "0.875rem", sm: "1rem" } }}
            >
              Processing evidence images...
            </Typography>
            <LinearProgress sx={{ mt: 2, maxWidth: 300, mx: "auto" }} />
          </Box>
        ) : (
          <>
            <Box
              sx={{
                width: { xs: 60, sm: 80 },
                height: { xs: 60, sm: 80 },
                borderRadius: "50%",
                bgcolor: "primary.main",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                mx: "auto",
                mb: { xs: 2, sm: 3 },
              }}
            >
              <CloudUpload
                sx={{ fontSize: { xs: 28, sm: 40 }, color: "white" }}
              />
            </Box>
            <Typography
              variant={isMobile ? "body1" : "h6"}
              gutterBottom
              fontWeight={600}
            >
              {isDragActive
                ? "Drop images here"
                : isMobile
                  ? "Tap to upload images"
                  : "Drag & drop evidence images"}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 2, fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
            >
              {isMobile ? "or browse files" : "or click to browse files"}
            </Typography>
            <Box
              sx={{
                display: "flex",
                gap: 1,
                justifyContent: "center",
                flexWrap: "wrap",
              }}
            >
              <Chip label="JPG" size="small" variant="outlined" />
              <Chip label="PNG" size="small" variant="outlined" />
              <Chip label="TIFF" size="small" variant="outlined" />
            </Box>
          </>
        )}
      </Box>

      {/* Image Gallery */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          mb: { xs: 2, sm: 3 },
          pb: 2,
          borderBottom: "1px solid",
          borderColor: "divider",
          flexWrap: "wrap",
          gap: 1,
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <PhotoLibrary color="primary" sx={{ fontSize: { xs: 20, sm: 24 } }} />
          <Typography variant={isMobile ? "body1" : "h6"} fontWeight={600}>
            Evidence Gallery
          </Typography>
          <Chip
            label={`${images.length} images`}
            size="small"
            sx={{
              bgcolor: "primary.main",
              color: "white",
              fontWeight: 600,
              fontSize: { xs: "0.7rem", sm: "0.75rem" },
            }}
          />
        </Box>
      </Box>

      <Grid container spacing={{ xs: 1.5, sm: 2.5 }}>
        {images.map((image) => (
          <Grid item xs={6} sm={4} md={3} lg={2} key={image.id}>
            <Card
              elevation={0}
              sx={{
                border: "1px solid",
                borderColor: "divider",
                borderRadius: 2,
                overflow: "hidden",
                transition: "all 0.2s ease",
                "&:hover": {
                  transform: "translateY(-2px)",
                  boxShadow: "0 8px 16px rgba(26, 54, 93, 0.1)",
                  borderColor: "primary.light",
                },
              }}
            >
              <Box sx={{ position: "relative" }}>
                <CardMedia
                  component="img"
                  height="120"
                  image={`${STATIC_BASE_URL}/${image.filepath}`}
                  alt={image.filename}
                  sx={{ objectFit: "cover" }}
                />
                {image.file_hash && (
                  <Box
                    sx={{
                      position: "absolute",
                      top: 8,
                      right: 8,
                      bgcolor: "rgba(45, 106, 79, 0.9)",
                      borderRadius: "50%",
                      width: 24,
                      height: 24,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <Verified sx={{ fontSize: 14, color: "white" }} />
                  </Box>
                )}
              </Box>
              <CardContent sx={{ p: 1.5 }}>
                <Typography
                  variant="caption"
                  sx={{ fontWeight: 600, display: "block", mb: 0.5 }}
                  noWrap
                >
                  {image.filename}
                </Typography>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                  {image.width && image.height && (
                    <Chip
                      label={`${image.width}×${image.height}`}
                      size="small"
                      sx={{
                        fontSize: "9px",
                        height: 18,
                        bgcolor: "rgba(26, 54, 93, 0.08)",
                      }}
                    />
                  )}
                  {image.gps_latitude && (
                    <Chip
                      label="GPS"
                      size="small"
                      sx={{
                        fontSize: "9px",
                        height: 18,
                        bgcolor: "success.main",
                        color: "white",
                      }}
                    />
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {images.length === 0 && (
        <Box
          sx={{
            textAlign: "center",
            py: 8,
            bgcolor: "rgba(0,0,0,0.02)",
            borderRadius: 2,
          }}
        >
          <PhotoLibrary sx={{ fontSize: 64, color: "grey.300", mb: 2 }} />
          <Typography variant="body1" color="text.secondary">
            No evidence images uploaded yet
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Upload images to begin forensic analysis
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

export default ImageUploadPanel;
