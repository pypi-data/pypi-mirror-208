from upyog.ml.imports import *
from upyog.image import fig_to_pil


__all__ = ["visualise_conf_matrix"]


def visualise_conf_matrix(
    conf_matrix: np.ndarray,
    labels: List[str],
    title: Optional[str] = None,
    normalize: bool = True,
    cmap: Union[None, str, mpl.colors.Colormap] = None,
    width: int = 6,
    dpi: int = 200,
    return_pil: bool = True,
):
    # Convert to DataFrame
    cm = conf_matrix
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm = pd.DataFrame(cm * 100)
    else:
        cm = pd.DataFrame(cm)
    cm.index = labels
    cm.columns = labels

    # Setup plot canvas
    fig, ax = plt.subplots(figsize=(width, width), dpi=dpi)

    # Colormap
    if not cmap:
        cmap = 'Blues'
        # cmap = sns.cubehelix_palette(as_cmap=True)

    # Draw heatmap, axes and title
    sns.heatmap(cm, annot=True, fmt=".1f", cbar=False, ax=ax, cmap=cmap)
    _= ax.set_yticklabels(labels, rotation=0)
    _= ax.set_xticklabels(labels, rotation=90)

    if title:
        ax.set_title(title)

    if return_pil: return fig_to_pil(fig)
    else:          return fig
