"""
Tests for the inverse-problem approach based ADI post-processing algorithms, 
using the functional API.

"""

import copy
from multiprocessing import cpu_count
import vip_hci as vip
from .helpers import np, parametrize, fixture


@fixture(scope="module")
def injected_cube_position(example_dataset_adi):
    """
    Inject a fake companion into an example cube.

    Parameters
    ----------
    example_dataset_adi : fixture
        Taken automatically from ``conftest.py``.

    Returns
    -------
    dsi : VIP Dataset
    injected_position_yx : tuple(y, x)

    """
    print("injecting fake planet...")
    dsi = copy.copy(example_dataset_adi)
    # we chose a shallow copy, as we will not use any in-place operations
    # (like +=). Using `deepcopy` would be safer, but consume more memory.

    dsi.inject_companions(300, rad_dists=30)

    return dsi, dsi.injections_yx[0]


# ====== algos
def algo_fast_paco(ds):
    fp = vip.invprob.paco.FastPACO(cube = ds.cube, angles = ds.angles,
                                   psf = ds.psf, pixscale = ds.px_scale,
                                   fwhm = ds.fwhm*ds.px_scale, verbose=True)
    snr, flux = fp.run(cpu=cpu_count()//2)
    return snr

def algo_fast_paco_parallel(ds):
    fp = vip.invprob.paco.FastPACO(cube = ds.cube, angles = ds.angles,
                                   psf = ds.psf, pixscale = ds.px_scale,
                                   fwhm = ds.fwhm*ds.px_scale, verbose=True)
    snr, flux = fp.run(cpu=cpu_count()//2)
    return snr

def algo_full_paco(ds):
    fp = vip.invprob.paco.FullPACO(cube = ds.cube, angles = ds.angles,
                                   psf = ds.psf, pixscale = ds.px_scale,
                                   fwhm = ds.fwhm*ds.px_scale, verbose=True)
    snr, flux = fp.run(cpu=cpu_count()//2)
    return snr


# ====== SNR map
def snrmap_fast(frame, ds):
    return vip.metrics.snrmap(frame, fwhm=ds.fwhm, approximated=True)


def snrmap(frame, ds):
    return vip.metrics.snrmap(frame, fwhm=ds.fwhm)


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
                                  debug=True, full_output=True, verbose=True)
    msg = "Injected companion not recovered"
    assert verify_expcoord(table.y, table.x, yx_exp), msg


@parametrize("algo, make_detmap",
             [
                 (algo_fast_paco, None),
                 (algo_fast_paco_parallel, None),
                 (algo_full_paco, None)
                 ],
             ids=lambda x: (x.__name__.replace("algo_", "") if callable(x) else x))
def test_algos(injected_cube_position, algo, make_detmap):
    ds, position = injected_cube_position
    frame = algo(ds)

    if make_detmap is not None:
        detmap = make_detmap(frame, ds)
    else:
        detmap = frame

    check_detection(detmap, position, ds.fwhm, snr_thresh=2)
