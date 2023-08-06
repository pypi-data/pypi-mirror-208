# from future.utils import iteritems
import os
from os.path import join as pjoin
from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy


def find_in_path(name, path):
    """Find a file in a search path"""

    # Adapted fom http://code.activestate.com/recipes/52224
    for dir in path.split(os.pathsep):
        binpath = pjoin(dir, name)
        if os.path.exists(binpath):
            return os.path.abspath(binpath)
    return None


def locate_cuda():
    """Locate the CUDA environment on the system
    Returns a dict with keys 'home', 'nvcc', 'include', and 'lib64'
    and values giving the absolute path to each directory.
    Starts by looking for the CUDAHOME env variable. If not found,
    everything is based on finding 'nvcc' in the PATH.
    """

    # First check if the CUDAHOME env variable is in use
    if 'CUDAHOME' in os.environ:
        home = os.environ['CUDAHOME']
        nvcc = pjoin(home, 'bin', 'nvcc')
    else:
        # Otherwise, search the PATH for NVCC
        nvcc = find_in_path('nvcc', os.environ['PATH'])
        if nvcc is None:
            raise EnvironmentError('The nvcc binary could not be '
                'located in your $PATH. Either add it to your path, '
                'or set $CUDAHOME')
        home = os.path.dirname(os.path.dirname(nvcc))

    cudaconfig = {'home': home, 'nvcc': nvcc,
                  'include': pjoin(home, 'include'),
                  'lib64': pjoin(home, 'lib64')}
    for k, v in iter(cudaconfig.items()):
        if not os.path.exists(v):
            raise EnvironmentError('The CUDA %s path could not be '
                                   'located in %s' % (k, v))

    return cudaconfig


def customize_compiler_for_nvcc(self):
    """Inject deep into distutils to customize how the dispatch
    to gcc/nvcc works.
    If you subclass UnixCCompiler, it's not trivial to get your subclass
    injected in, and still have the right customizations (i.e.
    distutils.sysconfig.customize_compiler) run on it. So instead of going
    the OO route, I have this. Note, it's kindof like a wierd functional
    subclassing going on.
    """

    # Tell the compiler it can processes .cu
    self.src_extensions.append('.cu')

    # Save references to the default compiler_so and _comple methods
    default_compiler_so = self.compiler_so
    super = self._compile

    # Now redefine the _compile method. This gets executed for each
    # object but distutils doesn't have the ability to change compilers
    # based on source extension: we add it.
    def _compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
        if os.path.splitext(src)[1] == '.cu':
            # use the cuda for .cu files
            self.set_executable('compiler_so', CUDA['nvcc'])
            # use only a subset of the extra_postargs, which are 1-1
            # translated from the extra_compile_args in the Extension class
            postargs = extra_postargs['nvcc']
        else:
            postargs = extra_postargs['gcc']

        super(obj, src, ext, cc_args, postargs, pp_opts)
        # Reset the default compiler_so, which we might have changed for cuda
        self.compiler_so = default_compiler_so

    # Inject our redefined _compile method into the class
    self._compile = _compile



# Run the customize_compiler
class custom_build_ext(build_ext):
    def build_extensions(self):
        customize_compiler_for_nvcc(self.compiler)
        build_ext.build_extensions(self)



CUDA = locate_cuda()

# Obtain the numpy include directory. This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()


ext = Extension('test_add_python',
        sources = ['src/test_add.cu', 'test_add_wrapper.pyx', 'src/test_add_cpu.cpp'],
        library_dirs = [CUDA['lib64']],
        libraries = ['cudart'],
        language = 'c++',
        runtime_library_dirs = [CUDA['lib64']],
        # This syntax is specific to this build system
        # we're only going to use certain compiler args with nvcc
        # and not with gcc the implementation of this trick is in
        # customize_compiler()
        extra_compile_args= {
            'gcc': ['-fopenmp'],
            'nvcc': ['--ptxas-options=-v', '-c',
                '--compiler-options', "'-fPIC'"
                ]
            },
        extra_link_args= ['-fopenmp'],
            include_dirs = [numpy_include, CUDA['include'], 'src']
        )


long_description = """
# RocAuc Pairwise Loss
This is gpu implementation of rocauc pairwise loss.
Package could be used to solve classification problems with relative small numbers of objects, where you need to improve rocauc score. \
Also there is cpu multithread implementation of this losses.
## Losses that are realized in this package
1. **Sigmoid pairwise loss.** (GPU or CPU implementations)
$$ L = \sum_{i, j}\hat{P}_{ij}\log{P_{ij}} + (1 - \hat{P}_{ij})\log{(1 - P_{ij})}$$
2. **RocAuc Pairwise Loss** with approximate auc computation. (GPU or CPU implementations)
3. **RocAuc Pairwise Loss Exact** (GPU or CPU implementations) with exact auc computation. This could be more compute intensive, but this loss might be helpfull for first boosting rounds (if you are using gradient boosting)
4. **RocAuc Pairwise Loss Exact Smoothened** (GPU or CPU implementations). This loss allows you to incorporate information about equal instances. Because $\Delta_{AUC_{ij}} = 0$ if $y_i = y_j$. So we just add small $\epsilon > 0$ in equation.

### For more information 
- You can see example notebook on [GitHub](https://github.com/DmitryAsdre/rocauc_pairwise/blob/main/deltaauc_package_examples.ipynb)
- Or you can use example notebook on [Google Colab]((https://colab.research.google.com/drive/1w7BN0XGjB5vgFp2pbiCaejabc91xWmI0?usp=sharing))
- Or you can use example notebook on [Kaggle](https://www.kaggle.com/code/michailindmitry/gradient-boosting-roc-auc-pairwise-example-ipynb)

## References
[1] Sean J. Welleck, Efficient AUC Optimization for Information Ranking Applications, IBM USA (2016) \
[2] Burges, C.J.: From ranknet to lambdarank to lambdamart: An overview. Learning (2010) \
[3] Calders, T., Jaroszewicz, S.: Efficient auc optimization for classification. Knowledge
Discovery in Databases. (2007)
"""

setup(name = 'test_add_python',
      # Random metadata. there's more you can supply
      author = 'Dmitry Michaylin',
      version = '0.5',
      
      long_description=long_description,
      long_description_content_type='text/markdown',
      
      ext_modules = [ext],

      # Inject our custom trigger
      cmdclass = {'build_ext': custom_build_ext},

      # Since the package has c code, the egg cannot be zipped
      zip_safe = False)
