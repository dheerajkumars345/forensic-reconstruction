import { useState, useEffect } from "react";
import {
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  FormControlLabel,
  Switch,
  Chip,
  SxProps,
  Theme,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  Polyline,
} from "react-leaflet";
import {
  Bloodtype,
  Satellite,
  LocationOn,
  GpsFixed,
} from "@mui/icons-material";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { imagesAPI, STATIC_BASE_URL } from "../api/client";

// Fix for default marker icons in Leaflet + Vite
const DefaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

interface Props {
  projectId: number;
}

// Component to recenter map when markers change
function MapRecenter({ coords }: { coords: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (coords.length > 0) {
      const bounds = L.latLngBounds(coords);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [coords, map]);
  return null;
}

function MapView({ projectId }: Props) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [images, setImages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchImages();
  }, [projectId]);

  const fetchImages = async () => {
    try {
      const response = await imagesAPI.list(projectId);
      setImages(response.data);
    } catch (err: any) {
      setError("Failed to load map data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const [showMacro, setShowMacro] = useState(false);

  const markers = images
    .filter((img) => img.gps_latitude && img.gps_longitude)
    .map((img) => ({
      position: [img.gps_latitude, img.gps_longitude] as [number, number],
      title: img.filename,
      id: img.id,
      thumbnail: img.filepath,
    }));

  // Simulate macro-reconstruction path (blood spatter distribution)
  const macroPath =
    markers.length > 1
      ? [markers[0].position, markers[markers.length - 1].position]
      : [];

  const headerStyle: SxProps<Theme> = {
    background: "linear-gradient(135deg, #1a365d 0%, #2c5282 100%)",
    p: { xs: 2, sm: 3 },
    color: "white",
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
      {/* eslint-disable-next-line @typescript-eslint/ban-ts-comment */}
      {/* @ts-ignore - MUI sx prop type complexity */}
      <Box sx={headerStyle}>
        <Box
          display="flex"
          flexDirection={{ xs: "column", sm: "row" }}
          justifyContent="space-between"
          alignItems={{ xs: "flex-start", sm: "center" }}
          gap={{ xs: 2, sm: 0 }}
        >
          <Box display="flex" alignItems="center" gap={{ xs: 1.5, sm: 2 }}>
            <Box
              sx={{
                width: { xs: 40, sm: 48 },
                height: { xs: 40, sm: 48 },
                borderRadius: "50%",
                bgcolor: "rgba(198, 151, 73, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Satellite
                sx={{ color: "#c69749", fontSize: { xs: 20, sm: 24 } }}
              />
            </Box>
            <Box>
              <Typography variant={isMobile ? "h6" : "h5"} fontWeight={700}>
                {isMobile ? "GPS View" : "Satellite & GPS View"}
              </Typography>
              <Typography
                variant="body2"
                sx={{ opacity: 0.85, display: { xs: "none", sm: "block" } }}
              >
                Geospatial visualization of evidence locations
              </Typography>
            </Box>
          </Box>
          <Box
            display="flex"
            alignItems="center"
            gap={{ xs: 1, sm: 2 }}
            flexWrap="wrap"
          >
            <Chip
              icon={<GpsFixed sx={{ fontSize: { xs: 14, sm: 16 } }} />}
              label={isMobile ? markers.length : `${markers.length} GPS Points`}
              size="small"
              color="success"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={showMacro}
                  onChange={(e) => setShowMacro(e.target.checked)}
                  color="error"
                  size={isMobile ? "small" : "medium"}
                />
              }
              label={
                <Box display="flex" alignItems="center" gap={0.5}>
                  <Bloodtype
                    sx={{ color: "#fca5a5", fontSize: { xs: 16, sm: 18 } }}
                  />
                  <Typography
                    variant="caption"
                    color="error"
                    sx={{ display: { xs: "none", sm: "block" } }}
                  >
                    Blood Spatter Analysis
                  </Typography>
                </Box>
              }
            />
          </Box>
        </Box>
      </Box>

      <Box p={{ xs: 2, sm: 3 }}>
        {loading ? (
          <Box
            sx={{
              height: { xs: 300, sm: 400, md: 500 },
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              bgcolor: "rgba(0,0,0,0.02)",
              borderRadius: 2,
            }}
          >
            <CircularProgress color="primary" />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : markers.length === 0 ? (
          <Box
            sx={{
              height: { xs: 300, sm: 400, md: 500 },
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              bgcolor: "rgba(0,0,0,0.02)",
              borderRadius: 2,
              border: "2px dashed",
              borderColor: "divider",
              flexDirection: "column",
              gap: 2,
              p: 2,
            }}
          >
            <Box
              sx={{
                width: { xs: 60, sm: 80 },
                height: { xs: 60, sm: 80 },
                borderRadius: "50%",
                bgcolor: "rgba(26, 54, 93, 0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <LocationOn
                sx={{ fontSize: { xs: 30, sm: 40 }, color: "#94a3b8" }}
              />
            </Box>
            <Typography
              variant={isMobile ? "body1" : "h6"}
              fontWeight={600}
              color="text.secondary"
              textAlign="center"
            >
              No GPS Metadata Found
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ maxWidth: 400, textAlign: "center" }}
            >
              {isMobile
                ? "Upload images with GPS tags or set manual location."
                : "Ensure uploaded images contain EXIF GPS tags or set a manual project location."}
            </Typography>
          </Box>
        ) : (
          <Box
            sx={{
              height: { xs: 300, sm: 400, md: 500 },
              borderRadius: 2,
              overflow: "hidden",
              border: "1px solid",
              borderColor: "divider",
            }}
          >
            <MapContainer
              center={markers[0].position}
              zoom={15}
              style={{ height: "100%", width: "100%" }}
              scrollWheelZoom={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {markers.map((marker) => (
                <Marker key={marker.id} position={marker.position}>
                  <Popup>
                    <Box sx={{ textAlign: "center" }}>
                      <Typography variant="subtitle2">
                        {marker.title}
                      </Typography>
                      <Box
                        component="img"
                        src={`${STATIC_BASE_URL}/${marker.thumbnail}`}
                        sx={{
                          width: 100,
                          height: "auto",
                          mt: 1,
                          borderRadius: 1,
                        }}
                      />
                      <Typography
                        variant="caption"
                        display="block"
                        sx={{ mt: 1 }}
                      >
                        {marker.position[0].toFixed(6)},{" "}
                        {marker.position[1].toFixed(6)}
                      </Typography>
                    </Box>
                  </Popup>
                </Marker>
              ))}
              {showMacro && macroPath.length > 0 && (
                <Polyline
                  positions={macroPath}
                  color="red"
                  weight={4}
                  opacity={0.7}
                  dashArray="10, 10"
                />
              )}
              <MapRecenter coords={markers.map((m) => m.position)} />
            </MapContainer>
          </Box>
        )}
      </Box>
    </Paper>
  );
}

export default MapView;
