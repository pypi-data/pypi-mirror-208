project('wdmtoolbox', 'c',
  version : run_command('python', '-c', 'print(open("VERSION", encoding="ascii").readline())').stdout().strip(),
  default_options : ['warning_level=2'])

add_languages('fortran')

py_mod = import('python')
py3 = py_mod.find_installation('python3')
py3_dep = py3.dependency()
message(py3.path())
message(py3.get_install_dir())

incdir_numpy = run_command(py3,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

incdir_f2py = run_command(py3,
    ['-c', 'import os; os.chdir(".."); import numpy.f2py; print(numpy.f2py.get_include())'],
    check : true
).stdout().strip()

srcs = [
        'wdm_support/DTTM90.f',
        'wdm_support/TSBUFR.f',
        'wdm_support/UTCHAR.f',
        'wdm_support/UTCP90.f',
        'wdm_support/UTDATE.f',
        'wdm_support/UTNUMB.f',
        'wdm_support/UTWDMD.f',
        'wdm_support/UTWDMF.f',
        'wdm_support/UTWDT1.f',
        'wdm_support/WDATM1.f',
        'wdm_support/WDATM2.f',
        'wdm_support/WDATRB.f',
        'wdm_support/WDBTCH.f',
        'wdm_support/WDMESS.f',
        'wdm_support/WDMID.f',
        'wdm_support/WDOP.f',
        'wdm_support/WDTMS1.f',
        'wdm_support/WDTMS2.f',
        ]

_wdm_lib_source = custom_target('_wdm_libmodule.c',
                            input : srcs,
                            output : ['_wdm_libmodule.c', '_wdm_lib-f2pywrappers.f'],
                            command : [ py3, '-m', 'numpy.f2py', '@INPUT@',
                            '-m', '_wdm_lib', '--lower'])

inc_np = include_directories(incdir_numpy, incdir_f2py, 'wdm_support')

py3.extension_module('_wdm_lib',
           srcs,
           _wdm_lib_source,
           incdir_f2py+'/fortranobject.c',
           include_directories: inc_np,
           dependencies : py3_dep,
           install : true)
