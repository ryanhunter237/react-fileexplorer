from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from PIL import Image
from stl.mesh import Mesh

from fileexplorer.proc import ProcessorTemplate

STL_EXTENSIONS = ('.stl',)

class StlProcessor(ProcessorTemplate):
    extensions = STL_EXTENSIONS

    def make_thumbnail(
        self,
        file_path: Path,
        thumbnails_dir: Path,
        thumbnail_size: tuple[int, int]
    ) -> str | None:
        try:
            image = get_stl_image(file_path)
        except Exception:
            return None
        thumbnail_filename = self.write_thumbnail(
            image=image,
            thumbnails_dir=thumbnails_dir,
            thumbnail_size=thumbnail_size
        )
        return thumbnail_filename

    def make_data_file(self, file_path: Path, data_files_dir: Path) -> str:
        return self.make_symlink_data_file(
            file_path=file_path,
            data_files_dir=data_files_dir
        )
    
def get_stl_image(stl_path: str|Path) -> Image.Image:
    stl_path = Path(stl_path)
    mesh = Mesh.from_file(str(stl_path))

    figure = plt.figure()
    axes = figure.add_subplot(111, projection='3d')

    axes.add_collection3d(Poly3DCollection(mesh.vectors))

    xmin, ymin, zmin = np.min(mesh.points.reshape(-1,3), axis=0)
    xmax, ymax, zmax = np.max(mesh.points.reshape(-1,3), axis=0)
    axes.set_xlim([xmin, xmax])
    axes.set_ylim([ymin, ymax])
    axes.set_zlim([zmin, zmax])
    axes.set_box_aspect((xmax-xmin, ymax-ymin, zmax-zmin))
    plt.axis('off')

    img = figure_to_PIL(figure)
    return crop_where_transparent(img)

def figure_to_PIL(figure: plt.Figure) -> Image.Image:
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(figure)  # Close the figure to free memory
    buf.seek(0) # Rewind the buffer's file pointer
    return Image.open(buf)

def crop_where_transparent(img: Image.Image) -> Image.Image:
    data = np.asarray(img)
    not_transparent = data[:,:,-1] > 0
    not_transparent_cols = np.where(np.sum(not_transparent, axis=0) > 0)[0]
    left = not_transparent_cols[0]
    right = not_transparent_cols[-1] + 1
    not_transparent_rows = np.where(np.sum(not_transparent, axis=1) > 0)[0]
    upper = not_transparent_rows[0]
    lower = not_transparent_rows[-1] + 1
    return img.crop((left, upper, right, lower))