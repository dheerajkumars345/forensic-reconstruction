"""
3D Reconstruction Service
Processes point clouds and generates 3D meshes
"""
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging

from config import settings

logger = logging.getLogger(__name__)

# Lazy import of open3d — optional heavy dependency
try:
    import open3d as o3d
    HAS_OPEN3D = True
except ImportError:
    o3d = None  # type: ignore
    HAS_OPEN3D = False
    logger.warning(
        "open3d is not installed. 3D reconstruction features will use fallback implementations. "
        "Install open3d for full functionality: pip install open3d"
    )


def _require_open3d():
    """Raise a clear error when open3d is needed but missing."""
    if not HAS_OPEN3D:
        raise RuntimeError(
            "open3d is required for this operation but is not installed. "
            "Install it with: pip install open3d"
        )


class Reconstruction3DService:
    """3D reconstruction and mesh processing"""

    @staticmethod
    def is_available() -> bool:
        """Check whether the open3d backend is available."""
        return HAS_OPEN3D
    
    @staticmethod
    def load_point_cloud(file_path: Path) -> Any:
        """
        Load point cloud from file
        
        Args:
            file_path: Path to point cloud file (.ply, .pcd, .xyz)
            
        Returns:
            Open3D point cloud object
        """
        _require_open3d()
        try:
            pcd = o3d.io.read_point_cloud(str(file_path))
            logger.info(f"Loaded point cloud with {len(pcd.points)} points")
            return pcd
        except Exception as e:
            logger.error(f"Error loading point cloud: {e}")
            raise
    
    @staticmethod
    def filter_point_cloud(
        pcd: Any,
        voxel_size: float = 0.01,
        remove_outliers: bool = True
    ) -> Any:
        """
        Filter and clean point cloud
        
        Args:
            pcd: Input point cloud
            voxel_size: Voxel size for downsampling
            remove_outliers: Whether to remove statistical outliers
            
        Returns:
            Filtered point cloud
        """
        _require_open3d()
        try:
            logger.info("Filtering point cloud...")
            original_count = len(pcd.points)
            
            # Downsample
            pcd_down = pcd.voxel_down_sample(voxel_size)
            logger.info(f"Downsampled from {original_count} to {len(pcd_down.points)} points")
            
            # Remove outliers
            if remove_outliers:
                pcd_filtered, ind = pcd_down.remove_statistical_outlier(
                    nb_neighbors=20,
                    std_ratio=2.0
                )
                logger.info(f"Removed {len(pcd_down.points) - len(pcd_filtered.points)} outliers")
                return pcd_filtered
            
            return pcd_down
            
        except Exception as e:
            logger.error(f"Error filtering point cloud: {e}")
            return pcd
    
    @staticmethod
    def estimate_normals(pcd: Any) -> Any:
        """
        Estimate normals for point cloud
        
        Args:
            pcd: Input point cloud
            
        Returns:
            Point cloud with normals
        """
        _require_open3d()
        try:
            pcd.estimate_normals(
                search_param=o3d.geometry.KDTreeSearchParamHybrid(
                    radius=0.1, max_nn=30
                )
            )
            pcd.orient_normals_consistent_tangent_plane(k=15)
            logger.info("Normals estimated and oriented")
            return pcd
        except Exception as e:
            logger.error(f"Error estimating normals: {e}")
            return pcd
    
    @staticmethod
    def create_mesh_poisson(
        pcd: Any,
        depth: int = 9
    ) -> Tuple[Any, np.ndarray]:
        """
        Create mesh using Poisson surface reconstruction
        
        Args:
            pcd: Input point cloud with normals
            depth: Octree depth (higher = more detail, 8-10 recommended)
            
        Returns:
            Tuple of (mesh, densities)
        """
        _require_open3d()
        try:
            logger.info(f"Creating mesh with Poisson reconstruction (depth={depth})...")
            mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                pcd, depth=depth
            )
            logger.info(f"Created mesh with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
            return mesh, densities
        except Exception as e:
            logger.error(f"Error creating Poisson mesh: {e}")
            raise
    
    @staticmethod
    def create_mesh_ball_pivoting(
        pcd: Any,
        radii: list = None
    ) -> Any:
        """
        Create mesh using Ball Pivoting Algorithm
        
        Args:
            pcd: Input point cloud with normals
            radii: List of radii for ball pivoting
            
        Returns:
            Triangle mesh
        """
        _require_open3d()
        try:
            if radii is None:
                # Estimate appropriate radii based on point cloud
                distances = pcd.compute_nearest_neighbor_distance()
                avg_dist = np.mean(distances)
                radii = [avg_dist, avg_dist * 2, avg_dist * 4]
            
            logger.info(f"Creating mesh with Ball Pivoting (radii={radii})...")
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                pcd,
                o3d.utility.DoubleVector(radii)
            )
            logger.info(f"Created mesh with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
            return mesh
        except Exception as e:
            logger.error(f"Error creating Ball Pivoting mesh: {e}")
            raise
    
    @staticmethod
    def filter_mesh_by_density(
        mesh: Any,
        densities: np.ndarray,
        quantile: float = 0.01
    ) -> Any:
        """
        Remove low-density vertices from mesh
        
        Args:
            mesh: Input mesh
            densities: Density values for each vertex
            quantile: Quantile threshold for filtering
            
        Returns:
            Filtered mesh
        """
        _require_open3d()
        try:
            vertices_to_remove = densities < np.quantile(densities, quantile)
            mesh.remove_vertices_by_mask(vertices_to_remove)
            logger.info(f"Filtered mesh to {len(mesh.vertices)} vertices")
            return mesh
        except Exception as e:
            logger.error(f"Error filtering mesh: {e}")
            return mesh
    
    @staticmethod
    def simplify_mesh(
        mesh: Any,
        target_reduction: float = 0.8
    ) -> Any:
        """
        Simplify mesh by reducing triangle count
        
        Args:
            mesh: Input mesh
            target_reduction: Target reduction ratio (0-1)
            
        Returns:
            Simplified mesh
        """
        _require_open3d()
        try:
            original_triangles = len(mesh.triangles)
            target_triangles = int(original_triangles * (1 - target_reduction))
            
            logger.info(f"Simplifying mesh from {original_triangles} to {target_triangles} triangles...")
            mesh_simplified = mesh.simplify_quadric_decimation(target_triangles)
            
            logger.info(f"Simplified to {len(mesh_simplified.triangles)} triangles")
            return mesh_simplified
        except Exception as e:
            logger.error(f"Error simplifying mesh: {e}")
            return mesh
    
    @staticmethod
    def smooth_mesh(
        mesh: Any,
        iterations: int = 5
    ) -> Any:
        """
        Smooth mesh surface
        
        Args:
            mesh: Input mesh
            iterations: Number of smoothing iterations
            
        Returns:
            Smoothed mesh
        """
        _require_open3d()
        try:
            mesh_smooth = mesh.filter_smooth_simple(number_of_iterations=iterations)
            logger.info(f"Mesh smoothed with {iterations} iterations")
            return mesh_smooth
        except Exception as e:
            logger.error(f"Error smoothing mesh: {e}")
            return mesh
    
    @staticmethod
    def save_mesh(
        mesh: Any,
        output_path: Path,
        format: str = None
    ) -> bool:
        """
        Save mesh to file
        
        Args:
            mesh: Mesh to save
            output_path: Output file path
            format: File format (ply, obj, gltf, stl)
            
        Returns:
            True if successful
        """
        _require_open3d()
        try:
            # Ensure mesh has vertex normals
            if not mesh.has_vertex_normals():
                mesh.compute_vertex_normals()
            
            success = o3d.io.write_triangle_mesh(str(output_path), mesh)
            
            if success:
                logger.info(f"Mesh saved to {output_path}")
            else:
                logger.error(f"Failed to save mesh to {output_path}")
            
            return success
        except Exception as e:
            logger.error(f"Error saving mesh: {e}")
            return False
    
    @staticmethod
    def save_point_cloud(
        pcd: Any,
        output_path: Path
    ) -> bool:
        """
        Save point cloud to file
        
        Args:
            pcd: Point cloud to save
            output_path: Output file path
            
        Returns:
            True if successful
        """
        _require_open3d()
        try:
            success = o3d.io.write_point_cloud(str(output_path), pcd)
            if success:
                logger.info(f"Point cloud saved to {output_path}")
            return success
        except Exception as e:
            logger.error(f"Error saving point cloud: {e}")
            return False
    
    @staticmethod
    def get_mesh_info(mesh: Any) -> Dict[str, Any]:
        """
        Get information about mesh
        
        Args:
            mesh: Input mesh
            
        Returns:
            Dictionary with mesh information
        """
        _require_open3d()
        return {
            "num_vertices": len(mesh.vertices),
            "num_triangles": len(mesh.triangles),
            "has_vertex_normals": mesh.has_vertex_normals(),
            "has_vertex_colors": mesh.has_vertex_colors(),
            "has_triangle_normals": mesh.has_triangle_normals(),
            "is_watertight": mesh.is_watertight(),
            "is_orientable": mesh.is_orientable(),
            "bounds": {
                "min": np.asarray(mesh.get_min_bound()).tolist(),
                "max": np.asarray(mesh.get_max_bound()).tolist()
            },
            "center": np.asarray(mesh.get_center()).tolist()
        }
