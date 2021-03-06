import numpy as np
import pyopencl as cl
import syris
import syris.config as cfg
from syris.gpu import util as gpu_util
from syris.tests import SyrisTest, opencl


@opencl
class TestPrecision(SyrisTest):

    def setUp(self):
        syris.init(device_index=0)
        self.n = 2
        self.kernel_fn = "vfloat_test.cl"

    def _create_mem_objs(self, n):
        mem = cl.Buffer(cfg.OPENCL.ctx, cl.mem_flags.READ_WRITE, size=n * cfg.PRECISION.cl_float)
        ar = np.empty(n, dtype=cfg.PRECISION.np_float)

        return mem, ar

    def _execute_and_check(self):
        prg = cl.Program(cfg.OPENCL.ctx, gpu_util.get_source([self.kernel_fn])).build()
        mem, ar = self._create_mem_objs(self.n)
        prg.float_test(cfg.OPENCL.queue,
                       (self.n,),
                       None,
                       mem)
        cl.enqueue_copy(cfg.OPENCL.queue, ar, mem)
        res = ar == np.array([0, 1], dtype=cfg.PRECISION.np_float)
        self.assertTrue(res.all())

    def test_float(self):
        self._execute_and_check()

    def test_double(self):
        cfg.PRECISION.set_precision(True)
        self._execute_and_check()
