import numpy as np
import pyopencl as cl
import pyopencl.array as cl_array
import quantities as q
import syris
from syris.gpu import util as gpu_util
from syris import config as cfg
from syris import imageprocessing as ip
from syris.util import get_magnitude, make_tuple
import itertools
from syris.tests import SyrisTest, slow


def bin_cpu(image, shape):
    factor = (image.shape[0] / shape[0], image.shape[1] / shape[1])
    im = np.copy(image)
    for k in range(1, factor[0]):
        im[::factor[0], :] += im[k::factor[0], :]
    for k in range(1, factor[1]):
        im[:, ::factor[1]] += im[:, k::factor[1]]
    return im[::factor[0], ::factor[1]]


def get_gauss_2d(shape, sigma, pixel_size=None, fourier=False):
    shape = make_tuple(shape)
    sigma = get_magnitude(make_tuple(sigma))
    if pixel_size is None:
        pixel_size = (1, 1)
    else:
        pixel_size = get_magnitude(make_tuple(pixel_size))

    if fourier:
        i = np.fft.fftfreq(shape[1]) / pixel_size[1]
        j = np.fft.fftfreq(shape[0]) / pixel_size[0]
        i, j = np.meshgrid(i, j)

        return np.exp(-2 * np.pi ** 2 * ((i * sigma[1]) ** 2 + (j * sigma[0]) ** 2))
    else:
        x = (np.arange(shape[1]) - shape[1] / 2) * pixel_size[1]
        y = (np.arange(shape[0]) - shape[0] / 2) * pixel_size[0]
        x, y = np.meshgrid(x, y)
        gauss = np.exp(- x ** 2 / (2. * sigma[1] ** 2) - y ** 2 / (2. * sigma[0] ** 2))

        return np.fft.ifftshift(gauss)


@slow
class TestGPUImageProcessing(SyrisTest):

    def setUp(self):
        syris.init()
        src = gpu_util.get_source(["vcomplex.cl",
                                   "imageprocessing.cl"])
        self.prg = cl.Program(cfg.OPENCL.ctx, src).build()
        self.size = 256
        self.mem = cl.Buffer(cfg.OPENCL.ctx, cl.mem_flags.READ_WRITE,
                             size=self.size ** 2 * cfg.PRECISION.cl_float)
        self.res = np.empty((self.size, self.size), dtype=cfg.PRECISION.np_float)
        self.distance = 1 * q.m
        self.lam = 4.9594e-11 * q.m
        self.pixel_size = 1 * q.um

    def _test_gauss(self, shape, fourier):
        """Test if the gauss in Fourier space calculated on a GPU is
        the same as Fourier transform of a gauss in real space.
        """
        sigma = (shape[0] * self.pixel_size.magnitude,
                 shape[1] / 2 * self.pixel_size.magnitude) * self.pixel_size.units
        if fourier:
            # Make the profile broad
            sigma = (1. / sigma[0].magnitude, 1. / sigma[1].magnitude) * sigma.units
        gauss = ip.get_gauss_2d(shape, sigma, self.pixel_size, fourier=fourier).get()
        gt = get_gauss_2d(shape, sigma, self.pixel_size, fourier=fourier)
        np.testing.assert_almost_equal(gauss, gt)

    def test_gauss(self):
        n = (64, 128, 129)
        for shape in itertools.product(n, n):
            self._test_gauss(shape, False)
            self._test_gauss(shape, True)

    def test_sum(self):
        n = 16
        image = np.arange(n * n).reshape(n, n).astype(cfg.PRECISION.np_float)
        cl_im = cl_array.to_device(cfg.OPENCL.queue, image)
        sizes = (1, 2, 4)
        for shape in itertools.product(sizes, sizes):
            gt = bin_cpu(image, shape)
            res = ip.bin_image(cl_im, shape)
            np.testing.assert_equal(gt, res)
