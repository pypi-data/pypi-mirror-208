"""
Tests for the post-processing pipeline, using the functional API.

"""

import copy
import vip_hci as vip
from .helpers import np, parametrize, fixture


def print_debug(s, *args, **kwargs):
    print(("\033[34m" + s + "\033[0m").format(*args, **kwargs))


@fixture(scope="module")
def injected_cube_position(example_dataset_rdi):
    """
    Inject a fake companion into an example cube.

    Parameters
    ----------
    example_dataset_rdi : fixture
        Taken automatically from ``conftest.py``.

    Returns
    -------
    dsi : VIP Dataset
    injected_position_yx : tuple(y, x)

    """
    print_debug("injecting fake planet...")
    dsi = copy.copy(example_dataset_rdi)
    # we chose a shallow copy, as we will not use any in-place operations
    # (like +=). Using `deepcopy` would be safer, but consume more memory.

    dsi.inject_companions(300, rad_dists=30)

    return dsi, dsi.injections_yx[0]


# ====== algos
def algo_pca(ds):
    return vip.psfsub.pca(ds.cube, ds.angles, cube_ref=ds.cuberef, ncomp=30,
                          mask_center_px=15)

def algo_pca_mask(ds):
    mask_rdi = np.ones([ds.cube.shape[-2], ds.cube.shape[-1]])
    mask_rdi = vip.var.get_annulus_segments(mask_rdi, 15, 30, mode="mask")[0]
    return vip.psfsub.pca(ds.cube, ds.angles, cube_ref=ds.cuberef, ncomp=30,
                          mask_center_px=15, mask_rdi=mask_rdi)

def algo_nmf(ds):
    return vip.psfsub.nmf(ds.cube, ds.angles, cube_ref=ds.cuberef, ncomp=30,
                          mask_center_px=15)


def algo_pca_annular_ardi(ds):
    return vip.psfsub.pca_annular(ds.cube, ds.angles, cube_ref=ds.cuberef,
                                  ncomp=10)


def algo_pca_annular_rdi(ds):
    return vip.psfsub.pca_annular(ds.cube, ds.angles, cube_ref=ds.cuberef,
                                  ncomp=30, delta_rot=100)


def algo_nmf_annular_ardi(ds):
    return vip.psfsub.nmf_annular(ds.cube, ds.angles, cube_ref=ds.cuberef,
                                  ncomp=10)


def algo_nmf_annular_rdi(ds):
    return vip.psfsub.nmf_annular(ds.cube, ds.angles, cube_ref=ds.cuberef,
                                  ncomp=30, delta_rot=100)

# ====== SNR map


def snrmap_fast(frame, ds):
    return vip.metrics.snrmap(frame, fwhm=ds.fwhm, approximated=True)


def snrmap(frame, ds):
    return vip.metrics.snrmap(frame, fwhm=np.mean(ds.fwhm))


# ====== Detection with ``vip_hci.metrics.detection``, by default with a
# location error or 3px
def check_detection(frame, yx_exp, fwhm, snr_thresh, deltapix=3):
    """
    Verify if injected companion is recovered.

    Parameters
    ----------
    frame : 2d ndarray
    yx_exp : tuple(y, x)
        Expected position of the fake companion (= injected position).
    fwhm : int or float
        FWHM.
    snr_thresh : int or float, optional
        S/N threshold.
    deltapix : int or float, optional
        Error margin in pixels, between the expected position and the recovered.

    """
    def verify_expcoord(vectory, vectorx, exp_yx):
        for coor in zip(vectory, vectorx):
            print(coor, exp_yx)
            if np.allclose(coor[0], exp_yx[0], atol=deltapix) and \
                    np.allclose(coor[1], exp_yx[1], atol=deltapix):
                return True
        return False

    table = vip.metrics.detection(frame, fwhm=fwhm, mode='lpeaks', bkg_sigma=5,
                                  matched_filter=False, mask=True,
                                  snr_thresh=snr_thresh, plot=False,
                                  debug=False, full_output=True, verbose=True)
    msg = "Injected companion not recovered"
    assert verify_expcoord(table.y, table.x, yx_exp), msg


@parametrize("algo, make_detmap", [
    (algo_pca, snrmap_fast),
    (algo_pca_mask, snrmap_fast),
    (algo_pca_annular_ardi, snrmap_fast),
    (algo_pca_annular_rdi, snrmap_fast),
    (algo_nmf, snrmap_fast),
    (algo_nmf_annular_ardi, snrmap_fast),
    (algo_nmf_annular_rdi, snrmap_fast)],
             ids=lambda x: (x.__name__.replace("algo_", "") if
                            callable(x) else x))
def test_algos(injected_cube_position, algo, make_detmap):
    ds, position = injected_cube_position
    frame = algo(ds)

    if make_detmap is not None:
        detmap = make_detmap(frame, ds)
    else:
        detmap = frame

    # since some are run with mask of zeros, detmap may have non-finite values
    detmap[np.where(np.isinf(detmap))] = 0

    check_detection(detmap, position, np.mean(ds.fwhm), snr_thresh=2)
