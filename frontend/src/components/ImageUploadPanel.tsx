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
} from "@mui/material";
import { CloudUpload, PhotoLibrary, Verified } from "@mui/icons-material";
import { useDropzone } from "react-dropzone";
import { imagesAPI, STATIC_BASE_URL } from "../api/client";

interface Props {
  projectId: number;
}

function ImageUploadPanel({ projectId }: Props) {
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
        p: 4,
        borderRadius: 3,
        border: "1px solid",
        borderColor: "divider",
      }}
    >
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h5"
          fontWeight={600}
          color="primary.main"
          gutterBottom
        >
          Evidence Image Upload
        </Typography>
        <Typography variant="body2" color="text.secondary">
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
          borderRadius: 3,
          p: 6,
          textAlign: "center",
          bgcolor: isDragActive ? "rgba(26, 54, 93, 0.04)" : "rgba(0,0,0,0.01)",
          cursor: "pointer",
          mb: 4,
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
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Processing evidence images...
            </Typography>
            <LinearProgress sx={{ mt: 2, maxWidth: 300, mx: "auto" }} />
          </Box>
        ) : (
          <>
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                bgcolor: "primary.main",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                mx: "auto",
                mb: 3,
              }}
            >
              <CloudUpload sx={{ fontSize: 40, color: "white" }} />
            </Box>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              {isDragActive
                ? "Drop images here"
                : "Drag & drop evidence images"}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              or click to browse files
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
          mb: 3,
          pb: 2,
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          <PhotoLibrary color="primary" />
          <Typography variant="h6" fontWeight={600}>
            Evidence Gallery
          </Typography>
          <Chip
            label={`${images.length} images`}
            size="small"
            sx={{
              bgcolor: "primary.main",
              color: "white",
              fontWeight: 600,
            }}
          />
        </Box>
      </Box>

      <Grid container spacing={2.5}>
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
