from __future__ import print_function, absolute_import, division
import _supy_driver
import f90wrap.runtime
import logging
import numpy

class Suews_Driver(f90wrap.runtime.FortranModule):
    """
    Module suews_driver
    
    
    Defined at suews_ctrl_driver.fpp lines 10-4601
    
    """
    @f90wrap.runtime.register_class("supy_driver.config")
    class config(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=config)
        
        
        Defined at suews_ctrl_driver.fpp lines 50-54
        
        """
        def __init__(self, handle=None):
            """
            self = Config()
            
            
            Defined at suews_ctrl_driver.fpp lines 50-54
            
            
            Returns
            -------
            this : Config
            	Object to be constructed
            
            
            Automatically generated constructor for config
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            result = _supy_driver.f90wrap_config_initialise()
            self._handle = result[0] if isinstance(result, tuple) else result
        
        def __del__(self):
            """
            Destructor for class Config
            
            
            Defined at suews_ctrl_driver.fpp lines 50-54
            
            Parameters
            ----------
            this : Config
            	Object to be destructed
            
            
            Automatically generated destructor for config
            """
            if self._alloc:
                _supy_driver.f90wrap_config_finalise(this=self._handle)
        
        @property
        def var1(self):
            """
            Element var1 ftype=integer  pytype=int
            
            
            Defined at suews_ctrl_driver.fpp line 51
            
            """
            return _supy_driver.f90wrap_config__get__var1(self._handle)
        
        @var1.setter
        def var1(self, var1):
            _supy_driver.f90wrap_config__set__var1(self._handle, var1)
        
        @property
        def var2(self):
            """
            Element var2 ftype=integer  pytype=int
            
            
            Defined at suews_ctrl_driver.fpp line 52
            
            """
            return _supy_driver.f90wrap_config__get__var2(self._handle)
        
        @var2.setter
        def var2(self, var2):
            _supy_driver.f90wrap_config__set__var2(self._handle, var2)
        
        def __str__(self):
            ret = ['<config>{\n']
            ret.append('    var1 : ')
            ret.append(repr(self.var1))
            ret.append(',\n    var2 : ')
            ret.append(repr(self.var2))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    
    @f90wrap.runtime.register_class("supy_driver.array_m")
    class array_m(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=array_m)
        
        
        Defined at suews_ctrl_driver.fpp lines 56-60
        
        """
        def __init__(self, handle=None):
            """
            self = Array_M()
            
            
            Defined at suews_ctrl_driver.fpp lines 56-60
            
            
            Returns
            -------
            this : Array_M
            	Object to be constructed
            
            
            Automatically generated constructor for array_m
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            result = _supy_driver.f90wrap_array_m_initialise()
            self._handle = result[0] if isinstance(result, tuple) else result
        
        def __del__(self):
            """
            Destructor for class Array_M
            
            
            Defined at suews_ctrl_driver.fpp lines 56-60
            
            Parameters
            ----------
            this : Array_M
            	Object to be destructed
            
            
            Automatically generated destructor for array_m
            """
            if self._alloc:
                _supy_driver.f90wrap_array_m_finalise(this=self._handle)
        
        @property
        def var1(self):
            """
            Element var1 ftype=integer pytype=int
            
            
            Defined at suews_ctrl_driver.fpp line 57
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_array_m__array__var1(self._handle)
            if array_handle in self._arrays:
                var1 = self._arrays[array_handle]
            else:
                var1 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_array_m__array__var1)
                self._arrays[array_handle] = var1
            return var1
        
        @var1.setter
        def var1(self, var1):
            self.var1[...] = var1
        
        @property
        def var2(self):
            """
            Element var2 ftype=integer pytype=int
            
            
            Defined at suews_ctrl_driver.fpp line 58
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_array_m__array__var2(self._handle)
            if array_handle in self._arrays:
                var2 = self._arrays[array_handle]
            else:
                var2 = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_array_m__array__var2)
                self._arrays[array_handle] = var2
            return var2
        
        @var2.setter
        def var2(self, var2):
            self.var2[...] = var2
        
        def __str__(self):
            ret = ['<array_m>{\n']
            ret.append('    var1 : ')
            ret.append(repr(self.var1))
            ret.append(',\n    var2 : ')
            ret.append(repr(self.var2))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    
    @f90wrap.runtime.register_class("supy_driver.output_block")
    class output_block(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=output_block)
        
        
        Defined at suews_ctrl_driver.fpp lines 62-75
        
        """
        def __init__(self, handle=None):
            """
            self = Output_Block()
            
            
            Defined at suews_ctrl_driver.fpp lines 62-75
            
            
            Returns
            -------
            this : Output_Block
            	Object to be constructed
            
            
            Automatically generated constructor for output_block
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            result = _supy_driver.f90wrap_output_block_initialise()
            self._handle = result[0] if isinstance(result, tuple) else result
        
        def __del__(self):
            """
            Destructor for class Output_Block
            
            
            Defined at suews_ctrl_driver.fpp lines 62-75
            
            Parameters
            ----------
            this : Output_Block
            	Object to be destructed
            
            
            Automatically generated destructor for output_block
            """
            if self._alloc:
                _supy_driver.f90wrap_output_block_finalise(this=self._handle)
        
        @property
        def dataoutblocksuews(self):
            """
            Element dataoutblocksuews ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 63
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblocksuews(self._handle)
            if array_handle in self._arrays:
                dataoutblocksuews = self._arrays[array_handle]
            else:
                dataoutblocksuews = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblocksuews)
                self._arrays[array_handle] = dataoutblocksuews
            return dataoutblocksuews
        
        @dataoutblocksuews.setter
        def dataoutblocksuews(self, dataoutblocksuews):
            self.dataoutblocksuews[...] = dataoutblocksuews
        
        @property
        def dataoutblocksnow(self):
            """
            Element dataoutblocksnow ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 64
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblocksnow(self._handle)
            if array_handle in self._arrays:
                dataoutblocksnow = self._arrays[array_handle]
            else:
                dataoutblocksnow = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblocksnow)
                self._arrays[array_handle] = dataoutblocksnow
            return dataoutblocksnow
        
        @dataoutblocksnow.setter
        def dataoutblocksnow(self, dataoutblocksnow):
            self.dataoutblocksnow[...] = dataoutblocksnow
        
        @property
        def dataoutblockestm(self):
            """
            Element dataoutblockestm ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 65
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblockestm(self._handle)
            if array_handle in self._arrays:
                dataoutblockestm = self._arrays[array_handle]
            else:
                dataoutblockestm = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblockestm)
                self._arrays[array_handle] = dataoutblockestm
            return dataoutblockestm
        
        @dataoutblockestm.setter
        def dataoutblockestm(self, dataoutblockestm):
            self.dataoutblockestm[...] = dataoutblockestm
        
        @property
        def dataoutblockestmext(self):
            """
            Element dataoutblockestmext ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 66
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblockestmext(self._handle)
            if array_handle in self._arrays:
                dataoutblockestmext = self._arrays[array_handle]
            else:
                dataoutblockestmext = \
                    f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblockestmext)
                self._arrays[array_handle] = dataoutblockestmext
            return dataoutblockestmext
        
        @dataoutblockestmext.setter
        def dataoutblockestmext(self, dataoutblockestmext):
            self.dataoutblockestmext[...] = dataoutblockestmext
        
        @property
        def dataoutblockrsl(self):
            """
            Element dataoutblockrsl ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 67
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblockrsl(self._handle)
            if array_handle in self._arrays:
                dataoutblockrsl = self._arrays[array_handle]
            else:
                dataoutblockrsl = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblockrsl)
                self._arrays[array_handle] = dataoutblockrsl
            return dataoutblockrsl
        
        @dataoutblockrsl.setter
        def dataoutblockrsl(self, dataoutblockrsl):
            self.dataoutblockrsl[...] = dataoutblockrsl
        
        @property
        def dataoutblockbeers(self):
            """
            Element dataoutblockbeers ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 68
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblockbeers(self._handle)
            if array_handle in self._arrays:
                dataoutblockbeers = self._arrays[array_handle]
            else:
                dataoutblockbeers = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblockbeers)
                self._arrays[array_handle] = dataoutblockbeers
            return dataoutblockbeers
        
        @dataoutblockbeers.setter
        def dataoutblockbeers(self, dataoutblockbeers):
            self.dataoutblockbeers[...] = dataoutblockbeers
        
        @property
        def dataoutblockdebug(self):
            """
            Element dataoutblockdebug ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 69
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblockdebug(self._handle)
            if array_handle in self._arrays:
                dataoutblockdebug = self._arrays[array_handle]
            else:
                dataoutblockdebug = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblockdebug)
                self._arrays[array_handle] = dataoutblockdebug
            return dataoutblockdebug
        
        @dataoutblockdebug.setter
        def dataoutblockdebug(self, dataoutblockdebug):
            self.dataoutblockdebug[...] = dataoutblockdebug
        
        @property
        def dataoutblockspartacus(self):
            """
            Element dataoutblockspartacus ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 70
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblockspartacus(self._handle)
            if array_handle in self._arrays:
                dataoutblockspartacus = self._arrays[array_handle]
            else:
                dataoutblockspartacus = \
                    f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblockspartacus)
                self._arrays[array_handle] = dataoutblockspartacus
            return dataoutblockspartacus
        
        @dataoutblockspartacus.setter
        def dataoutblockspartacus(self, dataoutblockspartacus):
            self.dataoutblockspartacus[...] = dataoutblockspartacus
        
        @property
        def dataoutblockdailystate(self):
            """
            Element dataoutblockdailystate ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 71
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_block__array__dataoutblockdailystate(self._handle)
            if array_handle in self._arrays:
                dataoutblockdailystate = self._arrays[array_handle]
            else:
                dataoutblockdailystate = \
                    f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_block__array__dataoutblockdailystate)
                self._arrays[array_handle] = dataoutblockdailystate
            return dataoutblockdailystate
        
        @dataoutblockdailystate.setter
        def dataoutblockdailystate(self, dataoutblockdailystate):
            self.dataoutblockdailystate[...] = dataoutblockdailystate
        
        def __str__(self):
            ret = ['<output_block>{\n']
            ret.append('    dataoutblocksuews : ')
            ret.append(repr(self.dataoutblocksuews))
            ret.append(',\n    dataoutblocksnow : ')
            ret.append(repr(self.dataoutblocksnow))
            ret.append(',\n    dataoutblockestm : ')
            ret.append(repr(self.dataoutblockestm))
            ret.append(',\n    dataoutblockestmext : ')
            ret.append(repr(self.dataoutblockestmext))
            ret.append(',\n    dataoutblockrsl : ')
            ret.append(repr(self.dataoutblockrsl))
            ret.append(',\n    dataoutblockbeers : ')
            ret.append(repr(self.dataoutblockbeers))
            ret.append(',\n    dataoutblockdebug : ')
            ret.append(repr(self.dataoutblockdebug))
            ret.append(',\n    dataoutblockspartacus : ')
            ret.append(repr(self.dataoutblockspartacus))
            ret.append(',\n    dataoutblockdailystate : ')
            ret.append(repr(self.dataoutblockdailystate))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    
    @f90wrap.runtime.register_class("supy_driver.output_line")
    class output_line(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=output_line)
        
        
        Defined at suews_ctrl_driver.fpp lines 77-87
        
        """
        def __init__(self, handle=None):
            """
            self = Output_Line()
            
            
            Defined at suews_ctrl_driver.fpp lines 77-87
            
            
            Returns
            -------
            this : Output_Line
            	Object to be constructed
            
            
            Automatically generated constructor for output_line
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            result = _supy_driver.f90wrap_output_line_initialise()
            self._handle = result[0] if isinstance(result, tuple) else result
        
        def __del__(self):
            """
            Destructor for class Output_Line
            
            
            Defined at suews_ctrl_driver.fpp lines 77-87
            
            Parameters
            ----------
            this : Output_Line
            	Object to be destructed
            
            
            Automatically generated destructor for output_line
            """
            if self._alloc:
                _supy_driver.f90wrap_output_line_finalise(this=self._handle)
        
        @property
        def datetimeline(self):
            """
            Element datetimeline ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 78
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__datetimeline(self._handle)
            if array_handle in self._arrays:
                datetimeline = self._arrays[array_handle]
            else:
                datetimeline = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__datetimeline)
                self._arrays[array_handle] = datetimeline
            return datetimeline
        
        @datetimeline.setter
        def datetimeline(self, datetimeline):
            self.datetimeline[...] = datetimeline
        
        @property
        def dataoutlinesuews(self):
            """
            Element dataoutlinesuews ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 79
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlinesuews(self._handle)
            if array_handle in self._arrays:
                dataoutlinesuews = self._arrays[array_handle]
            else:
                dataoutlinesuews = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlinesuews)
                self._arrays[array_handle] = dataoutlinesuews
            return dataoutlinesuews
        
        @dataoutlinesuews.setter
        def dataoutlinesuews(self, dataoutlinesuews):
            self.dataoutlinesuews[...] = dataoutlinesuews
        
        @property
        def dataoutlinesnow(self):
            """
            Element dataoutlinesnow ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 80
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlinesnow(self._handle)
            if array_handle in self._arrays:
                dataoutlinesnow = self._arrays[array_handle]
            else:
                dataoutlinesnow = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlinesnow)
                self._arrays[array_handle] = dataoutlinesnow
            return dataoutlinesnow
        
        @dataoutlinesnow.setter
        def dataoutlinesnow(self, dataoutlinesnow):
            self.dataoutlinesnow[...] = dataoutlinesnow
        
        @property
        def dataoutlineestm(self):
            """
            Element dataoutlineestm ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 81
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlineestm(self._handle)
            if array_handle in self._arrays:
                dataoutlineestm = self._arrays[array_handle]
            else:
                dataoutlineestm = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlineestm)
                self._arrays[array_handle] = dataoutlineestm
            return dataoutlineestm
        
        @dataoutlineestm.setter
        def dataoutlineestm(self, dataoutlineestm):
            self.dataoutlineestm[...] = dataoutlineestm
        
        @property
        def dataoutlineestmext(self):
            """
            Element dataoutlineestmext ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 82
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlineestmext(self._handle)
            if array_handle in self._arrays:
                dataoutlineestmext = self._arrays[array_handle]
            else:
                dataoutlineestmext = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlineestmext)
                self._arrays[array_handle] = dataoutlineestmext
            return dataoutlineestmext
        
        @dataoutlineestmext.setter
        def dataoutlineestmext(self, dataoutlineestmext):
            self.dataoutlineestmext[...] = dataoutlineestmext
        
        @property
        def dataoutlinersl(self):
            """
            Element dataoutlinersl ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 83
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlinersl(self._handle)
            if array_handle in self._arrays:
                dataoutlinersl = self._arrays[array_handle]
            else:
                dataoutlinersl = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlinersl)
                self._arrays[array_handle] = dataoutlinersl
            return dataoutlinersl
        
        @dataoutlinersl.setter
        def dataoutlinersl(self, dataoutlinersl):
            self.dataoutlinersl[...] = dataoutlinersl
        
        @property
        def dataoutlinebeers(self):
            """
            Element dataoutlinebeers ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 84
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlinebeers(self._handle)
            if array_handle in self._arrays:
                dataoutlinebeers = self._arrays[array_handle]
            else:
                dataoutlinebeers = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlinebeers)
                self._arrays[array_handle] = dataoutlinebeers
            return dataoutlinebeers
        
        @dataoutlinebeers.setter
        def dataoutlinebeers(self, dataoutlinebeers):
            self.dataoutlinebeers[...] = dataoutlinebeers
        
        @property
        def dataoutlinedebug(self):
            """
            Element dataoutlinedebug ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 85
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlinedebug(self._handle)
            if array_handle in self._arrays:
                dataoutlinedebug = self._arrays[array_handle]
            else:
                dataoutlinedebug = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlinedebug)
                self._arrays[array_handle] = dataoutlinedebug
            return dataoutlinedebug
        
        @dataoutlinedebug.setter
        def dataoutlinedebug(self, dataoutlinedebug):
            self.dataoutlinedebug[...] = dataoutlinedebug
        
        @property
        def dataoutlinespartacus(self):
            """
            Element dataoutlinespartacus ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 86
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlinespartacus(self._handle)
            if array_handle in self._arrays:
                dataoutlinespartacus = self._arrays[array_handle]
            else:
                dataoutlinespartacus = \
                    f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlinespartacus)
                self._arrays[array_handle] = dataoutlinespartacus
            return dataoutlinespartacus
        
        @dataoutlinespartacus.setter
        def dataoutlinespartacus(self, dataoutlinespartacus):
            self.dataoutlinespartacus[...] = dataoutlinespartacus
        
        @property
        def dataoutlinedailystate(self):
            """
            Element dataoutlinedailystate ftype=real(kind(1d0) pytype=float
            
            
            Defined at suews_ctrl_driver.fpp line 87
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _supy_driver.f90wrap_output_line__array__dataoutlinedailystate(self._handle)
            if array_handle in self._arrays:
                dataoutlinedailystate = self._arrays[array_handle]
            else:
                dataoutlinedailystate = \
                    f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _supy_driver.f90wrap_output_line__array__dataoutlinedailystate)
                self._arrays[array_handle] = dataoutlinedailystate
            return dataoutlinedailystate
        
        @dataoutlinedailystate.setter
        def dataoutlinedailystate(self, dataoutlinedailystate):
            self.dataoutlinedailystate[...] = dataoutlinedailystate
        
        def __str__(self):
            ret = ['<output_line>{\n']
            ret.append('    datetimeline : ')
            ret.append(repr(self.datetimeline))
            ret.append(',\n    dataoutlinesuews : ')
            ret.append(repr(self.dataoutlinesuews))
            ret.append(',\n    dataoutlinesnow : ')
            ret.append(repr(self.dataoutlinesnow))
            ret.append(',\n    dataoutlineestm : ')
            ret.append(repr(self.dataoutlineestm))
            ret.append(',\n    dataoutlineestmext : ')
            ret.append(repr(self.dataoutlineestmext))
            ret.append(',\n    dataoutlinersl : ')
            ret.append(repr(self.dataoutlinersl))
            ret.append(',\n    dataoutlinebeers : ')
            ret.append(repr(self.dataoutlinebeers))
            ret.append(',\n    dataoutlinedebug : ')
            ret.append(repr(self.dataoutlinedebug))
            ret.append(',\n    dataoutlinespartacus : ')
            ret.append(repr(self.dataoutlinespartacus))
            ret.append(',\n    dataoutlinedailystate : ')
            ret.append(repr(self.dataoutlinedailystate))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    
    @staticmethod
    def output_line_init(self):
        """
        output_line_init(self)
        
        
        Defined at suews_ctrl_driver.fpp lines 90-102
        
        Parameters
        ----------
        this_line : Output_Line
        
        """
        _supy_driver.f90wrap_output_line_init(this_line=self._handle)
    
    @staticmethod
    def output_block_init(self, len_bn):
        """
        output_block_init(self, len_bn)
        
        
        Defined at suews_ctrl_driver.fpp lines 104-126
        
        Parameters
        ----------
        this_block : Output_Block
        len_bn : int
        
        """
        _supy_driver.f90wrap_output_block_init(this_block=self._handle, len_bn=len_bn)
    
    @staticmethod
    def output_block_finalize(self):
        """
        output_block_finalize(self)
        
        
        Defined at suews_ctrl_driver.fpp lines 128-139
        
        Parameters
        ----------
        this_line : Output_Block
        
        """
        _supy_driver.f90wrap_output_block_finalize(this_line=self._handle)
    
    @staticmethod
    def var2add_two(self):
        """
        res_type = var2add_two(self)
        
        
        Defined at suews_ctrl_driver.fpp lines 141-145
        
        Parameters
        ----------
        arg_type : Config
        
        Returns
        -------
        res_type : Config
        
        """
        res_type = _supy_driver.f90wrap_var2add_two(arg_type=self._handle)
        res_type = \
            f90wrap.runtime.lookup_class("supy_driver.config").from_handle(res_type, \
            alloc=True)
        return res_type
    
    @staticmethod
    def arr2add_two(self):
        """
        res_type = arr2add_two(self)
        
        
        Defined at suews_ctrl_driver.fpp lines 147-151
        
        Parameters
        ----------
        arg_type : Array_M
        
        Returns
        -------
        res_type : Array_M
        
        """
        res_type = _supy_driver.f90wrap_arr2add_two(arg_type=self._handle)
        res_type = \
            f90wrap.runtime.lookup_class("supy_driver.array_m").from_handle(res_type, \
            alloc=True)
        return res_type
    
    @staticmethod
    def suews_cal_main(ah_min, ahprof_24hr, ah_slope_cooling, ah_slope_heating, alb, \
        albmax_dectr, albmax_evetr, albmax_grass, albmin_dectr, albmin_evetr, \
        albmin_grass, alpha_bioco2, alpha_enh_bioco2, alt, kdown, avrh, avu1, baset, \
        basete, beta_bioco2, beta_enh_bioco2, bldgh, capmax_dec, capmin_dec, \
        chanohm, co2pointsource, cpanohm, crwmax, crwmin, daywat, daywatper, \
        dectreeh, diagmethod, diagnose, drainrt, dt_since_start, dqndt, qn_av, \
        dqnsdt, qn_s_av, ef_umolco2perj, emis, emissionsmethod, enef_v_jkm, enddls, \
        evetreeh, faibldg, faidectree, faievetree, faut, fcef_v_kgkm, fcld_obs, \
        flowchange, frfossilfuel_heat, frfossilfuel_nonheat, g_max, g_k, g_q_base, \
        g_q_shape, g_t, g_sm, gdd_id, gddfull, gridiv, gsmodel, h_maintain, hdd_id, \
        humactivity_24hr, icefrac, id, ie_a, ie_end, ie_m, ie_start, imin, \
        internalwateruse_h, irrfracpaved, irrfracbldgs, irrfracevetr, irrfracdectr, \
        irrfracgrass, irrfracbsoil, irrfracwater, isec, it, iy, kkanohm, kmax, \
        lai_id, laimax, laimin, lai_obs, laipower, laitype, lat, lenday_id, \
        ldown_obs, lng, maxconductance, maxfcmetab, maxqfmetab, snowwater, \
        minfcmetab, minqfmetab, min_res_bioco2, narp_emis_snow, narp_trans_site, \
        netradiationmethod, nlayer, n_vegetation_region_urban, n_stream_sw_urban, \
        n_stream_lw_urban, sw_dn_direct_frac, air_ext_sw, air_ssa_sw, veg_ssa_sw, \
        air_ext_lw, air_ssa_lw, veg_ssa_lw, veg_fsd_const, \
        veg_contact_fraction_const, ground_albedo_dir_mult_fact, \
        use_sw_direct_albedo, height, building_frac, veg_frac, building_scale, \
        veg_scale, alb_roof, emis_roof, alb_wall, emis_wall, \
        roof_albedo_dir_mult_fact, wall_specular_frac, ohm_coef, ohmincqf, \
        ohm_threshsw, ohm_threshwd, pipecapacity, popdensdaytime, popdensnighttime, \
        popprof_24hr, pormax_dec, pormin_dec, precip, preciplimit, preciplimitalb, \
        press_hpa, qf0_beu, qf_a, qf_b, qf_c, qn1_obs, qs_obs, qf_obs, radmeltfact, \
        raincover, rainmaxres, resp_a, resp_b, roughlenheatmethod, \
        roughlenmommethod, runofftowater, s1, s2, sathydraulicconduct, sddfull, \
        sdd_id, smdmethod, snowalb, snowalbmax, snowalbmin, snowpacklimit, snowdens, \
        snowdensmax, snowdensmin, snowfallcum, snowfrac, snowlimbldg, snowlimpaved, \
        snowfrac_obs, snowpack, snowprof_24hr, snowuse, soildepth, stabilitymethod, \
        startdls, soilstore_surf, soilstorecap_surf, state_surf, statelimit_surf, \
        wetthresh_surf, soilstore_roof, soilstorecap_roof, state_roof, \
        statelimit_roof, wetthresh_roof, soilstore_wall, soilstorecap_wall, \
        state_wall, statelimit_wall, wetthresh_wall, storageheatmethod, \
        storedrainprm, surfacearea, tair_av, tau_a, tau_f, tau_r, tmax_id, tmin_id, \
        baset_cooling, baset_heating, temp_c, tempmeltfact, th, theta_bioco2, \
        timezone, tl, trafficrate, trafficunits, sfr_surf, tsfc_roof, tsfc_wall, \
        tsfc_surf, temp_roof, temp_wall, temp_surf, tin_roof, tin_wall, tin_surf, \
        k_roof, k_wall, k_surf, cp_roof, cp_wall, cp_surf, dz_roof, dz_wall, \
        dz_surf, traffprof_24hr, ts5mindata_ir, tstep, tstep_prev, veg_type, \
        waterdist, waterusemethod, wu_m3, wuday_id, decidcap_id, albdectr_id, \
        albevetr_id, albgrass_id, porosity_id, wuprofa_24hr, wuprofm_24hr, xsmd, z, \
        z0m_in, zdm_in):
        """
        output_line_suews = suews_cal_main(ah_min, ahprof_24hr, ah_slope_cooling, \
            ah_slope_heating, alb, albmax_dectr, albmax_evetr, albmax_grass, \
            albmin_dectr, albmin_evetr, albmin_grass, alpha_bioco2, alpha_enh_bioco2, \
            alt, kdown, avrh, avu1, baset, basete, beta_bioco2, beta_enh_bioco2, bldgh, \
            capmax_dec, capmin_dec, chanohm, co2pointsource, cpanohm, crwmax, crwmin, \
            daywat, daywatper, dectreeh, diagmethod, diagnose, drainrt, dt_since_start, \
            dqndt, qn_av, dqnsdt, qn_s_av, ef_umolco2perj, emis, emissionsmethod, \
            enef_v_jkm, enddls, evetreeh, faibldg, faidectree, faievetree, faut, \
            fcef_v_kgkm, fcld_obs, flowchange, frfossilfuel_heat, frfossilfuel_nonheat, \
            g_max, g_k, g_q_base, g_q_shape, g_t, g_sm, gdd_id, gddfull, gridiv, \
            gsmodel, h_maintain, hdd_id, humactivity_24hr, icefrac, id, ie_a, ie_end, \
            ie_m, ie_start, imin, internalwateruse_h, irrfracpaved, irrfracbldgs, \
            irrfracevetr, irrfracdectr, irrfracgrass, irrfracbsoil, irrfracwater, isec, \
            it, iy, kkanohm, kmax, lai_id, laimax, laimin, lai_obs, laipower, laitype, \
            lat, lenday_id, ldown_obs, lng, maxconductance, maxfcmetab, maxqfmetab, \
            snowwater, minfcmetab, minqfmetab, min_res_bioco2, narp_emis_snow, \
            narp_trans_site, netradiationmethod, nlayer, n_vegetation_region_urban, \
            n_stream_sw_urban, n_stream_lw_urban, sw_dn_direct_frac, air_ext_sw, \
            air_ssa_sw, veg_ssa_sw, air_ext_lw, air_ssa_lw, veg_ssa_lw, veg_fsd_const, \
            veg_contact_fraction_const, ground_albedo_dir_mult_fact, \
            use_sw_direct_albedo, height, building_frac, veg_frac, building_scale, \
            veg_scale, alb_roof, emis_roof, alb_wall, emis_wall, \
            roof_albedo_dir_mult_fact, wall_specular_frac, ohm_coef, ohmincqf, \
            ohm_threshsw, ohm_threshwd, pipecapacity, popdensdaytime, popdensnighttime, \
            popprof_24hr, pormax_dec, pormin_dec, precip, preciplimit, preciplimitalb, \
            press_hpa, qf0_beu, qf_a, qf_b, qf_c, qn1_obs, qs_obs, qf_obs, radmeltfact, \
            raincover, rainmaxres, resp_a, resp_b, roughlenheatmethod, \
            roughlenmommethod, runofftowater, s1, s2, sathydraulicconduct, sddfull, \
            sdd_id, smdmethod, snowalb, snowalbmax, snowalbmin, snowpacklimit, snowdens, \
            snowdensmax, snowdensmin, snowfallcum, snowfrac, snowlimbldg, snowlimpaved, \
            snowfrac_obs, snowpack, snowprof_24hr, snowuse, soildepth, stabilitymethod, \
            startdls, soilstore_surf, soilstorecap_surf, state_surf, statelimit_surf, \
            wetthresh_surf, soilstore_roof, soilstorecap_roof, state_roof, \
            statelimit_roof, wetthresh_roof, soilstore_wall, soilstorecap_wall, \
            state_wall, statelimit_wall, wetthresh_wall, storageheatmethod, \
            storedrainprm, surfacearea, tair_av, tau_a, tau_f, tau_r, tmax_id, tmin_id, \
            baset_cooling, baset_heating, temp_c, tempmeltfact, th, theta_bioco2, \
            timezone, tl, trafficrate, trafficunits, sfr_surf, tsfc_roof, tsfc_wall, \
            tsfc_surf, temp_roof, temp_wall, temp_surf, tin_roof, tin_wall, tin_surf, \
            k_roof, k_wall, k_surf, cp_roof, cp_wall, cp_surf, dz_roof, dz_wall, \
            dz_surf, traffprof_24hr, ts5mindata_ir, tstep, tstep_prev, veg_type, \
            waterdist, waterusemethod, wu_m3, wuday_id, decidcap_id, albdectr_id, \
            albevetr_id, albgrass_id, porosity_id, wuprofa_24hr, wuprofm_24hr, xsmd, z, \
            z0m_in, zdm_in)
        
        
        Defined at suews_ctrl_driver.fpp lines 218-1552
        
        Parameters
        ----------
        ah_min : float array
        ahprof_24hr : float array
        ah_slope_cooling : float array
        ah_slope_heating : float array
        alb : float array
        albmax_dectr : float
        albmax_evetr : float
        albmax_grass : float
        albmin_dectr : float
        albmin_evetr : float
        albmin_grass : float
        alpha_bioco2 : float array
        alpha_enh_bioco2 : float array
        alt : float
        kdown : float
        avrh : float
        avu1 : float
        baset : float array
        basete : float array
        beta_bioco2 : float array
        beta_enh_bioco2 : float array
        bldgh : float
        capmax_dec : float
        capmin_dec : float
        chanohm : float array
        co2pointsource : float
        cpanohm : float array
        crwmax : float
        crwmin : float
        daywat : float array
        daywatper : float array
        dectreeh : float
        diagmethod : int
        diagnose : int
        drainrt : float
        dt_since_start : int
        dqndt : float
        qn_av : float
        dqnsdt : float
        qn_s_av : float
        ef_umolco2perj : float
        emis : float array
        emissionsmethod : int
        enef_v_jkm : float
        enddls : int
        evetreeh : float
        faibldg : float
        faidectree : float
        faievetree : float
        faut : float
        fcef_v_kgkm : float array
        fcld_obs : float
        flowchange : float
        frfossilfuel_heat : float
        frfossilfuel_nonheat : float
        g_max : float
        g_k : float
        g_q_base : float
        g_q_shape : float
        g_t : float
        g_sm : float
        gdd_id : float array
        gddfull : float array
        gridiv : int
        gsmodel : int
        h_maintain : float
        hdd_id : float array
        humactivity_24hr : float array
        icefrac : float array
        id : int
        ie_a : float array
        ie_end : int
        ie_m : float array
        ie_start : int
        imin : int
        internalwateruse_h : float
        irrfracpaved : float
        irrfracbldgs : float
        irrfracevetr : float
        irrfracdectr : float
        irrfracgrass : float
        irrfracbsoil : float
        irrfracwater : float
        isec : int
        it : int
        iy : int
        kkanohm : float array
        kmax : float
        lai_id : float array
        laimax : float array
        laimin : float array
        lai_obs : float
        laipower : float array
        laitype : int array
        lat : float
        lenday_id : float
        ldown_obs : float
        lng : float
        maxconductance : float array
        maxfcmetab : float
        maxqfmetab : float
        snowwater : float array
        minfcmetab : float
        minqfmetab : float
        min_res_bioco2 : float array
        narp_emis_snow : float
        narp_trans_site : float
        netradiationmethod : int
        nlayer : int
        n_vegetation_region_urban : int
        n_stream_sw_urban : int
        n_stream_lw_urban : int
        sw_dn_direct_frac : float
        air_ext_sw : float
        air_ssa_sw : float
        veg_ssa_sw : float
        air_ext_lw : float
        air_ssa_lw : float
        veg_ssa_lw : float
        veg_fsd_const : float
        veg_contact_fraction_const : float
        ground_albedo_dir_mult_fact : float
        use_sw_direct_albedo : bool
        height : float array
        building_frac : float array
        veg_frac : float array
        building_scale : float array
        veg_scale : float array
        alb_roof : float array
        emis_roof : float array
        alb_wall : float array
        emis_wall : float array
        roof_albedo_dir_mult_fact : float array
        wall_specular_frac : float array
        ohm_coef : float array
        ohmincqf : int
        ohm_threshsw : float array
        ohm_threshwd : float array
        pipecapacity : float
        popdensdaytime : float array
        popdensnighttime : float
        popprof_24hr : float array
        pormax_dec : float
        pormin_dec : float
        precip : float
        preciplimit : float
        preciplimitalb : float
        press_hpa : float
        qf0_beu : float array
        qf_a : float array
        qf_b : float array
        qf_c : float array
        qn1_obs : float
        qs_obs : float
        qf_obs : float
        radmeltfact : float
        raincover : float
        rainmaxres : float
        resp_a : float array
        resp_b : float array
        roughlenheatmethod : int
        roughlenmommethod : int
        runofftowater : float
        s1 : float
        s2 : float
        sathydraulicconduct : float array
        sddfull : float array
        sdd_id : float array
        smdmethod : int
        snowalb : float
        snowalbmax : float
        snowalbmin : float
        snowpacklimit : float array
        snowdens : float array
        snowdensmax : float
        snowdensmin : float
        snowfallcum : float
        snowfrac : float array
        snowlimbldg : float
        snowlimpaved : float
        snowfrac_obs : float
        snowpack : float array
        snowprof_24hr : float array
        snowuse : int
        soildepth : float array
        stabilitymethod : int
        startdls : int
        soilstore_surf : float array
        soilstorecap_surf : float array
        state_surf : float array
        statelimit_surf : float array
        wetthresh_surf : float array
        soilstore_roof : float array
        soilstorecap_roof : float array
        state_roof : float array
        statelimit_roof : float array
        wetthresh_roof : float array
        soilstore_wall : float array
        soilstorecap_wall : float array
        state_wall : float array
        statelimit_wall : float array
        wetthresh_wall : float array
        storageheatmethod : int
        storedrainprm : float array
        surfacearea : float
        tair_av : float
        tau_a : float
        tau_f : float
        tau_r : float
        tmax_id : float
        tmin_id : float
        baset_cooling : float array
        baset_heating : float array
        temp_c : float
        tempmeltfact : float
        th : float
        theta_bioco2 : float array
        timezone : float
        tl : float
        trafficrate : float array
        trafficunits : float
        sfr_surf : float array
        tsfc_roof : float array
        tsfc_wall : float array
        tsfc_surf : float array
        temp_roof : float array
        temp_wall : float array
        temp_surf : float array
        tin_roof : float array
        tin_wall : float array
        tin_surf : float array
        k_roof : float array
        k_wall : float array
        k_surf : float array
        cp_roof : float array
        cp_wall : float array
        cp_surf : float array
        dz_roof : float array
        dz_wall : float array
        dz_surf : float array
        traffprof_24hr : float array
        ts5mindata_ir : float array
        tstep : int
        tstep_prev : int
        veg_type : int
        waterdist : float array
        waterusemethod : int
        wu_m3 : float
        wuday_id : float array
        decidcap_id : float
        albdectr_id : float
        albevetr_id : float
        albgrass_id : float
        porosity_id : float
        wuprofa_24hr : float array
        wuprofm_24hr : float array
        xsmd : float
        z : float
        z0m_in : float
        zdm_in : float
        
        Returns
        -------
        output_line_suews : Output_Line
        
        ==============main calculation start=======================
        ==============surface roughness calculation=======================
        """
        output_line_suews = _supy_driver.f90wrap_suews_cal_main(ah_min=ah_min, \
            ahprof_24hr=ahprof_24hr, ah_slope_cooling=ah_slope_cooling, \
            ah_slope_heating=ah_slope_heating, alb=alb, albmax_dectr=albmax_dectr, \
            albmax_evetr=albmax_evetr, albmax_grass=albmax_grass, \
            albmin_dectr=albmin_dectr, albmin_evetr=albmin_evetr, \
            albmin_grass=albmin_grass, alpha_bioco2=alpha_bioco2, \
            alpha_enh_bioco2=alpha_enh_bioco2, alt=alt, kdown=kdown, avrh=avrh, \
            avu1=avu1, baset=baset, basete=basete, beta_bioco2=beta_bioco2, \
            beta_enh_bioco2=beta_enh_bioco2, bldgh=bldgh, capmax_dec=capmax_dec, \
            capmin_dec=capmin_dec, chanohm=chanohm, co2pointsource=co2pointsource, \
            cpanohm=cpanohm, crwmax=crwmax, crwmin=crwmin, daywat=daywat, \
            daywatper=daywatper, dectreeh=dectreeh, diagmethod=diagmethod, \
            diagnose=diagnose, drainrt=drainrt, dt_since_start=dt_since_start, \
            dqndt=dqndt, qn_av=qn_av, dqnsdt=dqnsdt, qn_s_av=qn_s_av, \
            ef_umolco2perj=ef_umolco2perj, emis=emis, emissionsmethod=emissionsmethod, \
            enef_v_jkm=enef_v_jkm, enddls=enddls, evetreeh=evetreeh, faibldg=faibldg, \
            faidectree=faidectree, faievetree=faievetree, faut=faut, \
            fcef_v_kgkm=fcef_v_kgkm, fcld_obs=fcld_obs, flowchange=flowchange, \
            frfossilfuel_heat=frfossilfuel_heat, \
            frfossilfuel_nonheat=frfossilfuel_nonheat, g_max=g_max, g_k=g_k, \
            g_q_base=g_q_base, g_q_shape=g_q_shape, g_t=g_t, g_sm=g_sm, gdd_id=gdd_id, \
            gddfull=gddfull, gridiv=gridiv, gsmodel=gsmodel, h_maintain=h_maintain, \
            hdd_id=hdd_id, humactivity_24hr=humactivity_24hr, icefrac=icefrac, id=id, \
            ie_a=ie_a, ie_end=ie_end, ie_m=ie_m, ie_start=ie_start, imin=imin, \
            internalwateruse_h=internalwateruse_h, irrfracpaved=irrfracpaved, \
            irrfracbldgs=irrfracbldgs, irrfracevetr=irrfracevetr, \
            irrfracdectr=irrfracdectr, irrfracgrass=irrfracgrass, \
            irrfracbsoil=irrfracbsoil, irrfracwater=irrfracwater, isec=isec, it=it, \
            iy=iy, kkanohm=kkanohm, kmax=kmax, lai_id=lai_id, laimax=laimax, \
            laimin=laimin, lai_obs=lai_obs, laipower=laipower, laitype=laitype, lat=lat, \
            lenday_id=lenday_id, ldown_obs=ldown_obs, lng=lng, \
            maxconductance=maxconductance, maxfcmetab=maxfcmetab, maxqfmetab=maxqfmetab, \
            snowwater=snowwater, minfcmetab=minfcmetab, minqfmetab=minqfmetab, \
            min_res_bioco2=min_res_bioco2, narp_emis_snow=narp_emis_snow, \
            narp_trans_site=narp_trans_site, netradiationmethod=netradiationmethod, \
            nlayer=nlayer, n_vegetation_region_urban=n_vegetation_region_urban, \
            n_stream_sw_urban=n_stream_sw_urban, n_stream_lw_urban=n_stream_lw_urban, \
            sw_dn_direct_frac=sw_dn_direct_frac, air_ext_sw=air_ext_sw, \
            air_ssa_sw=air_ssa_sw, veg_ssa_sw=veg_ssa_sw, air_ext_lw=air_ext_lw, \
            air_ssa_lw=air_ssa_lw, veg_ssa_lw=veg_ssa_lw, veg_fsd_const=veg_fsd_const, \
            veg_contact_fraction_const=veg_contact_fraction_const, \
            ground_albedo_dir_mult_fact=ground_albedo_dir_mult_fact, \
            use_sw_direct_albedo=use_sw_direct_albedo, height=height, \
            building_frac=building_frac, veg_frac=veg_frac, \
            building_scale=building_scale, veg_scale=veg_scale, alb_roof=alb_roof, \
            emis_roof=emis_roof, alb_wall=alb_wall, emis_wall=emis_wall, \
            roof_albedo_dir_mult_fact=roof_albedo_dir_mult_fact, \
            wall_specular_frac=wall_specular_frac, ohm_coef=ohm_coef, ohmincqf=ohmincqf, \
            ohm_threshsw=ohm_threshsw, ohm_threshwd=ohm_threshwd, \
            pipecapacity=pipecapacity, popdensdaytime=popdensdaytime, \
            popdensnighttime=popdensnighttime, popprof_24hr=popprof_24hr, \
            pormax_dec=pormax_dec, pormin_dec=pormin_dec, precip=precip, \
            preciplimit=preciplimit, preciplimitalb=preciplimitalb, press_hpa=press_hpa, \
            qf0_beu=qf0_beu, qf_a=qf_a, qf_b=qf_b, qf_c=qf_c, qn1_obs=qn1_obs, \
            qs_obs=qs_obs, qf_obs=qf_obs, radmeltfact=radmeltfact, raincover=raincover, \
            rainmaxres=rainmaxres, resp_a=resp_a, resp_b=resp_b, \
            roughlenheatmethod=roughlenheatmethod, roughlenmommethod=roughlenmommethod, \
            runofftowater=runofftowater, s1=s1, s2=s2, \
            sathydraulicconduct=sathydraulicconduct, sddfull=sddfull, sdd_id=sdd_id, \
            smdmethod=smdmethod, snowalb=snowalb, snowalbmax=snowalbmax, \
            snowalbmin=snowalbmin, snowpacklimit=snowpacklimit, snowdens=snowdens, \
            snowdensmax=snowdensmax, snowdensmin=snowdensmin, snowfallcum=snowfallcum, \
            snowfrac=snowfrac, snowlimbldg=snowlimbldg, snowlimpaved=snowlimpaved, \
            snowfrac_obs=snowfrac_obs, snowpack=snowpack, snowprof_24hr=snowprof_24hr, \
            snowuse=snowuse, soildepth=soildepth, stabilitymethod=stabilitymethod, \
            startdls=startdls, soilstore_surf=soilstore_surf, \
            soilstorecap_surf=soilstorecap_surf, state_surf=state_surf, \
            statelimit_surf=statelimit_surf, wetthresh_surf=wetthresh_surf, \
            soilstore_roof=soilstore_roof, soilstorecap_roof=soilstorecap_roof, \
            state_roof=state_roof, statelimit_roof=statelimit_roof, \
            wetthresh_roof=wetthresh_roof, soilstore_wall=soilstore_wall, \
            soilstorecap_wall=soilstorecap_wall, state_wall=state_wall, \
            statelimit_wall=statelimit_wall, wetthresh_wall=wetthresh_wall, \
            storageheatmethod=storageheatmethod, storedrainprm=storedrainprm, \
            surfacearea=surfacearea, tair_av=tair_av, tau_a=tau_a, tau_f=tau_f, \
            tau_r=tau_r, tmax_id=tmax_id, tmin_id=tmin_id, baset_cooling=baset_cooling, \
            baset_heating=baset_heating, temp_c=temp_c, tempmeltfact=tempmeltfact, \
            th=th, theta_bioco2=theta_bioco2, timezone=timezone, tl=tl, \
            trafficrate=trafficrate, trafficunits=trafficunits, sfr_surf=sfr_surf, \
            tsfc_roof=tsfc_roof, tsfc_wall=tsfc_wall, tsfc_surf=tsfc_surf, \
            temp_roof=temp_roof, temp_wall=temp_wall, temp_surf=temp_surf, \
            tin_roof=tin_roof, tin_wall=tin_wall, tin_surf=tin_surf, k_roof=k_roof, \
            k_wall=k_wall, k_surf=k_surf, cp_roof=cp_roof, cp_wall=cp_wall, \
            cp_surf=cp_surf, dz_roof=dz_roof, dz_wall=dz_wall, dz_surf=dz_surf, \
            traffprof_24hr=traffprof_24hr, ts5mindata_ir=ts5mindata_ir, tstep=tstep, \
            tstep_prev=tstep_prev, veg_type=veg_type, waterdist=waterdist, \
            waterusemethod=waterusemethod, wu_m3=wu_m3, wuday_id=wuday_id, \
            decidcap_id=decidcap_id, albdectr_id=albdectr_id, albevetr_id=albevetr_id, \
            albgrass_id=albgrass_id, porosity_id=porosity_id, wuprofa_24hr=wuprofa_24hr, \
            wuprofm_24hr=wuprofm_24hr, xsmd=xsmd, z=z, z0m_in=z0m_in, zdm_in=zdm_in)
        output_line_suews = \
            f90wrap.runtime.lookup_class("supy_driver.output_line").from_handle(output_line_suews, \
            alloc=True)
        return output_line_suews
    
    @staticmethod
    def suews_cal_anthropogenicemission(ah_min, ahprof_24hr, ah_slope_cooling, \
        ah_slope_heating, co2pointsource, dayofweek_id, dls, ef_umolco2perj, \
        emissionsmethod, enef_v_jkm, fcef_v_kgkm, frfossilfuel_heat, \
        frfossilfuel_nonheat, hdd_id, humactivity_24hr, imin, it, maxfcmetab, \
        maxqfmetab, minfcmetab, minqfmetab, popdensdaytime, popdensnighttime, \
        popprof_24hr, qf0_beu, qf_a, qf_b, qf_c, qf_obs, surfacearea, baset_cooling, \
        baset_heating, temp_c, trafficrate, trafficunits, traffprof_24hr):
        """
        qf, qf_sahp, fc_anthro, fc_build, fc_metab, fc_point, fc_traff = \
            suews_cal_anthropogenicemission(ah_min, ahprof_24hr, ah_slope_cooling, \
            ah_slope_heating, co2pointsource, dayofweek_id, dls, ef_umolco2perj, \
            emissionsmethod, enef_v_jkm, fcef_v_kgkm, frfossilfuel_heat, \
            frfossilfuel_nonheat, hdd_id, humactivity_24hr, imin, it, maxfcmetab, \
            maxqfmetab, minfcmetab, minqfmetab, popdensdaytime, popdensnighttime, \
            popprof_24hr, qf0_beu, qf_a, qf_b, qf_c, qf_obs, surfacearea, baset_cooling, \
            baset_heating, temp_c, trafficrate, trafficunits, traffprof_24hr)
        
        
        Defined at suews_ctrl_driver.fpp lines 1564-1644
        
        Parameters
        ----------
        ah_min : float array
        ahprof_24hr : float array
        ah_slope_cooling : float array
        ah_slope_heating : float array
        co2pointsource : float
        dayofweek_id : int array
        dls : int
        ef_umolco2perj : float
        emissionsmethod : int
        enef_v_jkm : float
        fcef_v_kgkm : float array
        frfossilfuel_heat : float
        frfossilfuel_nonheat : float
        hdd_id : float array
        humactivity_24hr : float array
        imin : int
        it : int
        maxfcmetab : float
        maxqfmetab : float
        minfcmetab : float
        minqfmetab : float
        popdensdaytime : float array
        popdensnighttime : float
        popprof_24hr : float array
        qf0_beu : float array
        qf_a : float array
        qf_b : float array
        qf_c : float array
        qf_obs : float
        surfacearea : float
        baset_cooling : float array
        baset_heating : float array
        temp_c : float
        trafficrate : float array
        trafficunits : float
        traffprof_24hr : float array
        
        Returns
        -------
        qf : float
        qf_sahp : float
        fc_anthro : float
        fc_build : float
        fc_metab : float
        fc_point : float
        fc_traff : float
        
        """
        qf, qf_sahp, fc_anthro, fc_build, fc_metab, fc_point, fc_traff = \
            _supy_driver.f90wrap_suews_cal_anthropogenicemission(ah_min=ah_min, \
            ahprof_24hr=ahprof_24hr, ah_slope_cooling=ah_slope_cooling, \
            ah_slope_heating=ah_slope_heating, co2pointsource=co2pointsource, \
            dayofweek_id=dayofweek_id, dls=dls, ef_umolco2perj=ef_umolco2perj, \
            emissionsmethod=emissionsmethod, enef_v_jkm=enef_v_jkm, \
            fcef_v_kgkm=fcef_v_kgkm, frfossilfuel_heat=frfossilfuel_heat, \
            frfossilfuel_nonheat=frfossilfuel_nonheat, hdd_id=hdd_id, \
            humactivity_24hr=humactivity_24hr, imin=imin, it=it, maxfcmetab=maxfcmetab, \
            maxqfmetab=maxqfmetab, minfcmetab=minfcmetab, minqfmetab=minqfmetab, \
            popdensdaytime=popdensdaytime, popdensnighttime=popdensnighttime, \
            popprof_24hr=popprof_24hr, qf0_beu=qf0_beu, qf_a=qf_a, qf_b=qf_b, qf_c=qf_c, \
            qf_obs=qf_obs, surfacearea=surfacearea, baset_cooling=baset_cooling, \
            baset_heating=baset_heating, temp_c=temp_c, trafficrate=trafficrate, \
            trafficunits=trafficunits, traffprof_24hr=traffprof_24hr)
        return qf, qf_sahp, fc_anthro, fc_build, fc_metab, fc_point, fc_traff
    
    @staticmethod
    def suews_cal_biogenco2(alpha_bioco2, alpha_enh_bioco2, avkdn, avrh, \
        beta_bioco2, beta_enh_bioco2, dectime, diagnose, emissionsmethod, fc_anthro, \
        g_max, g_k, g_q_base, g_q_shape, g_t, g_sm, gfunc, gsmodel, id, it, kmax, \
        lai_id, laimin, laimax, maxconductance, min_res_bioco2, press_hpa, resp_a, \
        resp_b, s1, s2, sfr_surf, smdmethod, snowfrac, t2_c, temp_c, theta_bioco2, \
        th, tl, vsmd, xsmd):
        """
        fc, fc_biogen, fc_photo, fc_respi = suews_cal_biogenco2(alpha_bioco2, \
            alpha_enh_bioco2, avkdn, avrh, beta_bioco2, beta_enh_bioco2, dectime, \
            diagnose, emissionsmethod, fc_anthro, g_max, g_k, g_q_base, g_q_shape, g_t, \
            g_sm, gfunc, gsmodel, id, it, kmax, lai_id, laimin, laimax, maxconductance, \
            min_res_bioco2, press_hpa, resp_a, resp_b, s1, s2, sfr_surf, smdmethod, \
            snowfrac, t2_c, temp_c, theta_bioco2, th, tl, vsmd, xsmd)
        
        
        Defined at suews_ctrl_driver.fpp lines 1654-1760
        
        Parameters
        ----------
        alpha_bioco2 : float array
        alpha_enh_bioco2 : float array
        avkdn : float
        avrh : float
        beta_bioco2 : float array
        beta_enh_bioco2 : float array
        dectime : float
        diagnose : int
        emissionsmethod : int
        fc_anthro : float
        g_max : float
        g_k : float
        g_q_base : float
        g_q_shape : float
        g_t : float
        g_sm : float
        gfunc : float
        gsmodel : int
        id : int
        it : int
        kmax : float
        lai_id : float array
        laimin : float array
        laimax : float array
        maxconductance : float array
        min_res_bioco2 : float array
        press_hpa : float
        resp_a : float array
        resp_b : float array
        s1 : float
        s2 : float
        sfr_surf : float array
        smdmethod : int
        snowfrac : float array
        t2_c : float
        temp_c : float
        theta_bioco2 : float array
        th : float
        tl : float
        vsmd : float
        xsmd : float
        
        Returns
        -------
        fc : float
        fc_biogen : float
        fc_photo : float
        fc_respi : float
        
        """
        fc, fc_biogen, fc_photo, fc_respi = \
            _supy_driver.f90wrap_suews_cal_biogenco2(alpha_bioco2=alpha_bioco2, \
            alpha_enh_bioco2=alpha_enh_bioco2, avkdn=avkdn, avrh=avrh, \
            beta_bioco2=beta_bioco2, beta_enh_bioco2=beta_enh_bioco2, dectime=dectime, \
            diagnose=diagnose, emissionsmethod=emissionsmethod, fc_anthro=fc_anthro, \
            g_max=g_max, g_k=g_k, g_q_base=g_q_base, g_q_shape=g_q_shape, g_t=g_t, \
            g_sm=g_sm, gfunc=gfunc, gsmodel=gsmodel, id=id, it=it, kmax=kmax, \
            lai_id=lai_id, laimin=laimin, laimax=laimax, maxconductance=maxconductance, \
            min_res_bioco2=min_res_bioco2, press_hpa=press_hpa, resp_a=resp_a, \
            resp_b=resp_b, s1=s1, s2=s2, sfr_surf=sfr_surf, smdmethod=smdmethod, \
            snowfrac=snowfrac, t2_c=t2_c, temp_c=temp_c, theta_bioco2=theta_bioco2, \
            th=th, tl=tl, vsmd=vsmd, xsmd=xsmd)
        return fc, fc_biogen, fc_photo, fc_respi
    
    @staticmethod
    def suews_cal_qn(storageheatmethod, netradiationmethod, snowuse, tstep, nlayer, \
        snowpack_prev, tau_a, tau_f, snowalbmax, snowalbmin, diagnose, ldown_obs, \
        fcld_obs, dectime, zenith_deg, tsurf_0, kdown, tair_c, avrh, ea_hpa, \
        qn1_obs, snowalb_prev, snowfrac_prev, diagqn, narp_trans_site, \
        narp_emis_snow, icefrac, sfr_surf, sfr_roof, sfr_wall, tsfc_surf, tsfc_roof, \
        tsfc_wall, emis, alb_prev, albdectr_id, albevetr_id, albgrass_id, lai_id, \
        n_vegetation_region_urban, n_stream_sw_urban, n_stream_lw_urban, \
        sw_dn_direct_frac, air_ext_sw, air_ssa_sw, veg_ssa_sw, air_ext_lw, \
        air_ssa_lw, veg_ssa_lw, veg_fsd_const, veg_contact_fraction_const, \
        ground_albedo_dir_mult_fact, use_sw_direct_albedo, height, building_frac, \
        veg_frac, building_scale, veg_scale, alb_roof, emis_roof, alb_wall, \
        emis_wall, roof_albedo_dir_mult_fact, wall_specular_frac, alb_next, qn_surf, \
        qn_roof, qn_wall, qn_ind_snow, kup_ind_snow, tsurf_ind_snow, tsurf_ind, \
        dataoutlinespartacus):
        """
        ldown, fcld, qn, qn_snowfree, qn_snow, kclear, kup, lup, tsurf, albedo_snow, \
            snowalb_next = suews_cal_qn(storageheatmethod, netradiationmethod, snowuse, \
            tstep, nlayer, snowpack_prev, tau_a, tau_f, snowalbmax, snowalbmin, \
            diagnose, ldown_obs, fcld_obs, dectime, zenith_deg, tsurf_0, kdown, tair_c, \
            avrh, ea_hpa, qn1_obs, snowalb_prev, snowfrac_prev, diagqn, narp_trans_site, \
            narp_emis_snow, icefrac, sfr_surf, sfr_roof, sfr_wall, tsfc_surf, tsfc_roof, \
            tsfc_wall, emis, alb_prev, albdectr_id, albevetr_id, albgrass_id, lai_id, \
            n_vegetation_region_urban, n_stream_sw_urban, n_stream_lw_urban, \
            sw_dn_direct_frac, air_ext_sw, air_ssa_sw, veg_ssa_sw, air_ext_lw, \
            air_ssa_lw, veg_ssa_lw, veg_fsd_const, veg_contact_fraction_const, \
            ground_albedo_dir_mult_fact, use_sw_direct_albedo, height, building_frac, \
            veg_frac, building_scale, veg_scale, alb_roof, emis_roof, alb_wall, \
            emis_wall, roof_albedo_dir_mult_fact, wall_specular_frac, alb_next, qn_surf, \
            qn_roof, qn_wall, qn_ind_snow, kup_ind_snow, tsurf_ind_snow, tsurf_ind, \
            dataoutlinespartacus)
        
        
        Defined at suews_ctrl_driver.fpp lines 1789-1981
        
        Parameters
        ----------
        storageheatmethod : int
        netradiationmethod : int
        snowuse : int
        tstep : int
        nlayer : int
        snowpack_prev : float array
        tau_a : float
        tau_f : float
        snowalbmax : float
        snowalbmin : float
        diagnose : int
        ldown_obs : float
        fcld_obs : float
        dectime : float
        zenith_deg : float
        tsurf_0 : float
        kdown : float
        tair_c : float
        avrh : float
        ea_hpa : float
        qn1_obs : float
        snowalb_prev : float
        snowfrac_prev : float array
        diagqn : int
        narp_trans_site : float
        narp_emis_snow : float
        icefrac : float array
        sfr_surf : float array
        sfr_roof : float array
        sfr_wall : float array
        tsfc_surf : float array
        tsfc_roof : float array
        tsfc_wall : float array
        emis : float array
        alb_prev : float array
        albdectr_id : float
        albevetr_id : float
        albgrass_id : float
        lai_id : float array
        n_vegetation_region_urban : int
        n_stream_sw_urban : int
        n_stream_lw_urban : int
        sw_dn_direct_frac : float
        air_ext_sw : float
        air_ssa_sw : float
        veg_ssa_sw : float
        air_ext_lw : float
        air_ssa_lw : float
        veg_ssa_lw : float
        veg_fsd_const : float
        veg_contact_fraction_const : float
        ground_albedo_dir_mult_fact : float
        use_sw_direct_albedo : bool
        height : float array
        building_frac : float array
        veg_frac : float array
        building_scale : float array
        veg_scale : float array
        alb_roof : float array
        emis_roof : float array
        alb_wall : float array
        emis_wall : float array
        roof_albedo_dir_mult_fact : float array
        wall_specular_frac : float array
        alb_next : float array
        qn_surf : float array
        qn_roof : float array
        qn_wall : float array
        qn_ind_snow : float array
        kup_ind_snow : float array
        tsurf_ind_snow : float array
        tsurf_ind : float array
        dataoutlinespartacus : float array
        
        Returns
        -------
        ldown : float
        fcld : float
        qn : float
        qn_snowfree : float
        qn_snow : float
        kclear : float
        kup : float
        lup : float
        tsurf : float
        albedo_snow : float
        snowalb_next : float
        
        """
        ldown, fcld, qn, qn_snowfree, qn_snow, kclear, kup, lup, tsurf, albedo_snow, \
            snowalb_next = \
            _supy_driver.f90wrap_suews_cal_qn(storageheatmethod=storageheatmethod, \
            netradiationmethod=netradiationmethod, snowuse=snowuse, tstep=tstep, \
            nlayer=nlayer, snowpack_prev=snowpack_prev, tau_a=tau_a, tau_f=tau_f, \
            snowalbmax=snowalbmax, snowalbmin=snowalbmin, diagnose=diagnose, \
            ldown_obs=ldown_obs, fcld_obs=fcld_obs, dectime=dectime, \
            zenith_deg=zenith_deg, tsurf_0=tsurf_0, kdown=kdown, tair_c=tair_c, \
            avrh=avrh, ea_hpa=ea_hpa, qn1_obs=qn1_obs, snowalb_prev=snowalb_prev, \
            snowfrac_prev=snowfrac_prev, diagqn=diagqn, narp_trans_site=narp_trans_site, \
            narp_emis_snow=narp_emis_snow, icefrac=icefrac, sfr_surf=sfr_surf, \
            sfr_roof=sfr_roof, sfr_wall=sfr_wall, tsfc_surf=tsfc_surf, \
            tsfc_roof=tsfc_roof, tsfc_wall=tsfc_wall, emis=emis, alb_prev=alb_prev, \
            albdectr_id=albdectr_id, albevetr_id=albevetr_id, albgrass_id=albgrass_id, \
            lai_id=lai_id, n_vegetation_region_urban=n_vegetation_region_urban, \
            n_stream_sw_urban=n_stream_sw_urban, n_stream_lw_urban=n_stream_lw_urban, \
            sw_dn_direct_frac=sw_dn_direct_frac, air_ext_sw=air_ext_sw, \
            air_ssa_sw=air_ssa_sw, veg_ssa_sw=veg_ssa_sw, air_ext_lw=air_ext_lw, \
            air_ssa_lw=air_ssa_lw, veg_ssa_lw=veg_ssa_lw, veg_fsd_const=veg_fsd_const, \
            veg_contact_fraction_const=veg_contact_fraction_const, \
            ground_albedo_dir_mult_fact=ground_albedo_dir_mult_fact, \
            use_sw_direct_albedo=use_sw_direct_albedo, height=height, \
            building_frac=building_frac, veg_frac=veg_frac, \
            building_scale=building_scale, veg_scale=veg_scale, alb_roof=alb_roof, \
            emis_roof=emis_roof, alb_wall=alb_wall, emis_wall=emis_wall, \
            roof_albedo_dir_mult_fact=roof_albedo_dir_mult_fact, \
            wall_specular_frac=wall_specular_frac, alb_next=alb_next, qn_surf=qn_surf, \
            qn_roof=qn_roof, qn_wall=qn_wall, qn_ind_snow=qn_ind_snow, \
            kup_ind_snow=kup_ind_snow, tsurf_ind_snow=tsurf_ind_snow, \
            tsurf_ind=tsurf_ind, dataoutlinespartacus=dataoutlinespartacus)
        return ldown, fcld, qn, qn_snowfree, qn_snow, kclear, kup, lup, tsurf, \
            albedo_snow, snowalb_next
    
    @staticmethod
    def suews_cal_qs(storageheatmethod, qs_obs, ohmincqf, gridiv, id, tstep, \
        dt_since_start, diagnose, nlayer, qg_surf, qg_roof, qg_wall, tsfc_roof, \
        tin_roof, temp_in_roof, k_roof, cp_roof, dz_roof, sfr_roof, tsfc_wall, \
        tin_wall, temp_in_wall, k_wall, cp_wall, dz_wall, sfr_wall, tsfc_surf, \
        tin_surf, temp_in_surf, k_surf, cp_surf, dz_surf, sfr_surf, ohm_coef, \
        ohm_threshsw, ohm_threshwd, soilstore_id, soilstorecap, state_id, snowuse, \
        snowfrac, diagqs, hdd_id, metforcingdata_grid, ts5mindata_ir, qf, qn, avkdn, \
        avu1, temp_c, zenith_deg, avrh, press_hpa, ldown, bldgh, alb, emis, cpanohm, \
        kkanohm, chanohm, emissionsmethod, tair_av, qn_av_prev, dqndt_prev, \
        qn_s_av_prev, dqnsdt_prev, storedrainprm, dataoutlineestm, deltaqi, \
        temp_out_roof, qs_roof, temp_out_wall, qs_wall, temp_out_surf, qs_surf):
        """
        qn_s, qs, qn_av_next, dqndt_next, qn_s_av_next, dqnsdt_next, a1, a2, a3 = \
            suews_cal_qs(storageheatmethod, qs_obs, ohmincqf, gridiv, id, tstep, \
            dt_since_start, diagnose, nlayer, qg_surf, qg_roof, qg_wall, tsfc_roof, \
            tin_roof, temp_in_roof, k_roof, cp_roof, dz_roof, sfr_roof, tsfc_wall, \
            tin_wall, temp_in_wall, k_wall, cp_wall, dz_wall, sfr_wall, tsfc_surf, \
            tin_surf, temp_in_surf, k_surf, cp_surf, dz_surf, sfr_surf, ohm_coef, \
            ohm_threshsw, ohm_threshwd, soilstore_id, soilstorecap, state_id, snowuse, \
            snowfrac, diagqs, hdd_id, metforcingdata_grid, ts5mindata_ir, qf, qn, avkdn, \
            avu1, temp_c, zenith_deg, avrh, press_hpa, ldown, bldgh, alb, emis, cpanohm, \
            kkanohm, chanohm, emissionsmethod, tair_av, qn_av_prev, dqndt_prev, \
            qn_s_av_prev, dqnsdt_prev, storedrainprm, dataoutlineestm, deltaqi, \
            temp_out_roof, qs_roof, temp_out_wall, qs_wall, temp_out_surf, qs_surf)
        
        
        Defined at suews_ctrl_driver.fpp lines 2005-2199
        
        Parameters
        ----------
        storageheatmethod : int
        qs_obs : float
        ohmincqf : int
        gridiv : int
        id : int
        tstep : int
        dt_since_start : int
        diagnose : int
        nlayer : int
        qg_surf : float array
        qg_roof : float array
        qg_wall : float array
        tsfc_roof : float array
        tin_roof : float array
        temp_in_roof : float array
        k_roof : float array
        cp_roof : float array
        dz_roof : float array
        sfr_roof : float array
        tsfc_wall : float array
        tin_wall : float array
        temp_in_wall : float array
        k_wall : float array
        cp_wall : float array
        dz_wall : float array
        sfr_wall : float array
        tsfc_surf : float array
        tin_surf : float array
        temp_in_surf : float array
        k_surf : float array
        cp_surf : float array
        dz_surf : float array
        sfr_surf : float array
        ohm_coef : float array
        ohm_threshsw : float array
        ohm_threshwd : float array
        soilstore_id : float array
        soilstorecap : float array
        state_id : float array
        snowuse : int
        snowfrac : float array
        diagqs : int
        hdd_id : float array
        metforcingdata_grid : float array
        ts5mindata_ir : float array
        qf : float
        qn : float
        avkdn : float
        avu1 : float
        temp_c : float
        zenith_deg : float
        avrh : float
        press_hpa : float
        ldown : float
        bldgh : float
        alb : float array
        emis : float array
        cpanohm : float array
        kkanohm : float array
        chanohm : float array
        emissionsmethod : int
        tair_av : float
        qn_av_prev : float
        dqndt_prev : float
        qn_s_av_prev : float
        dqnsdt_prev : float
        storedrainprm : float array
        dataoutlineestm : float array
        deltaqi : float array
        temp_out_roof : float array
        qs_roof : float array
        temp_out_wall : float array
        qs_wall : float array
        temp_out_surf : float array
        qs_surf : float array
        
        Returns
        -------
        qn_s : float
        qs : float
        qn_av_next : float
        dqndt_next : float
        qn_s_av_next : float
        dqnsdt_next : float
        a1 : float
        a2 : float
        a3 : float
        
        """
        qn_s, qs, qn_av_next, dqndt_next, qn_s_av_next, dqnsdt_next, a1, a2, a3 = \
            _supy_driver.f90wrap_suews_cal_qs(storageheatmethod=storageheatmethod, \
            qs_obs=qs_obs, ohmincqf=ohmincqf, gridiv=gridiv, id=id, tstep=tstep, \
            dt_since_start=dt_since_start, diagnose=diagnose, nlayer=nlayer, \
            qg_surf=qg_surf, qg_roof=qg_roof, qg_wall=qg_wall, tsfc_roof=tsfc_roof, \
            tin_roof=tin_roof, temp_in_roof=temp_in_roof, k_roof=k_roof, \
            cp_roof=cp_roof, dz_roof=dz_roof, sfr_roof=sfr_roof, tsfc_wall=tsfc_wall, \
            tin_wall=tin_wall, temp_in_wall=temp_in_wall, k_wall=k_wall, \
            cp_wall=cp_wall, dz_wall=dz_wall, sfr_wall=sfr_wall, tsfc_surf=tsfc_surf, \
            tin_surf=tin_surf, temp_in_surf=temp_in_surf, k_surf=k_surf, \
            cp_surf=cp_surf, dz_surf=dz_surf, sfr_surf=sfr_surf, ohm_coef=ohm_coef, \
            ohm_threshsw=ohm_threshsw, ohm_threshwd=ohm_threshwd, \
            soilstore_id=soilstore_id, soilstorecap=soilstorecap, state_id=state_id, \
            snowuse=snowuse, snowfrac=snowfrac, diagqs=diagqs, hdd_id=hdd_id, \
            metforcingdata_grid=metforcingdata_grid, ts5mindata_ir=ts5mindata_ir, qf=qf, \
            qn=qn, avkdn=avkdn, avu1=avu1, temp_c=temp_c, zenith_deg=zenith_deg, \
            avrh=avrh, press_hpa=press_hpa, ldown=ldown, bldgh=bldgh, alb=alb, \
            emis=emis, cpanohm=cpanohm, kkanohm=kkanohm, chanohm=chanohm, \
            emissionsmethod=emissionsmethod, tair_av=tair_av, qn_av_prev=qn_av_prev, \
            dqndt_prev=dqndt_prev, qn_s_av_prev=qn_s_av_prev, dqnsdt_prev=dqnsdt_prev, \
            storedrainprm=storedrainprm, dataoutlineestm=dataoutlineestm, \
            deltaqi=deltaqi, temp_out_roof=temp_out_roof, qs_roof=qs_roof, \
            temp_out_wall=temp_out_wall, qs_wall=qs_wall, temp_out_surf=temp_out_surf, \
            qs_surf=qs_surf)
        return qn_s, qs, qn_av_next, dqndt_next, qn_s_av_next, dqnsdt_next, a1, a2, a3
    
    @staticmethod
    def suews_cal_water(diagnose, snowuse, nonwaterfraction, addpipes, \
        addimpervious, addveg, addwaterbody, state_id, sfr_surf, storedrainprm, \
        waterdist, nsh_real, drain, frac_water2runoff, addwater):
        """
        drain_per_tstep, additionalwater, runoffpipes, runoff_per_interval = \
            suews_cal_water(diagnose, snowuse, nonwaterfraction, addpipes, \
            addimpervious, addveg, addwaterbody, state_id, sfr_surf, storedrainprm, \
            waterdist, nsh_real, drain, frac_water2runoff, addwater)
        
        
        Defined at suews_ctrl_driver.fpp lines 2210-2279
        
        Parameters
        ----------
        diagnose : int
        snowuse : int
        nonwaterfraction : float
        addpipes : float
        addimpervious : float
        addveg : float
        addwaterbody : float
        state_id : float array
        sfr_surf : float array
        storedrainprm : float array
        waterdist : float array
        nsh_real : float
        drain : float array
        frac_water2runoff : float array
        addwater : float array
        
        Returns
        -------
        drain_per_tstep : float
        additionalwater : float
        runoffpipes : float
        runoff_per_interval : float
        
        ============= Grid-to-grid runoff =============
         Calculate additional water coming from other grids
         i.e. the variables addImpervious, addVeg, addWaterBody, addPipes
        call RunoffFromGrid(GridFromFrac)
        Need to code between-grid water transfer
         Sum water coming from other grids(these are expressed as depths over the whole \
             surface)
        """
        drain_per_tstep, additionalwater, runoffpipes, runoff_per_interval = \
            _supy_driver.f90wrap_suews_cal_water(diagnose=diagnose, snowuse=snowuse, \
            nonwaterfraction=nonwaterfraction, addpipes=addpipes, \
            addimpervious=addimpervious, addveg=addveg, addwaterbody=addwaterbody, \
            state_id=state_id, sfr_surf=sfr_surf, storedrainprm=storedrainprm, \
            waterdist=waterdist, nsh_real=nsh_real, drain=drain, \
            frac_water2runoff=frac_water2runoff, addwater=addwater)
        return drain_per_tstep, additionalwater, runoffpipes, runoff_per_interval
    
    @staticmethod
    def suews_init_qh(avdens, avcp, h_mod, qn1, dectime):
        """
        h_init = suews_init_qh(avdens, avcp, h_mod, qn1, dectime)
        
        
        Defined at suews_ctrl_driver.fpp lines 2285-2306
        
        Parameters
        ----------
        avdens : float
        avcp : float
        h_mod : float
        qn1 : float
        dectime : float
        
        Returns
        -------
        h_init : float
        
        """
        h_init = _supy_driver.f90wrap_suews_init_qh(avdens=avdens, avcp=avcp, \
            h_mod=h_mod, qn1=qn1, dectime=dectime)
        return h_init
    
    @staticmethod
    def suews_cal_snow(diagnose, nlayer, tstep, imin, it, evapmethod, dayofweek_id, \
        crwmin, crwmax, dectime, avdens, avcp, lv_j_kg, lvs_j_kg, avrh, press_hpa, \
        temp_c, rasnow, psyc_hpa, sice_hpa, tau_r, radmeltfact, tempmeltfact, \
        snowalbmax, preciplimit, preciplimitalb, qn_ind_snow, kup_ind_snow, deltaqi, \
        tsurf_ind_snow, snowalb_in, pervfraction, vegfraction, addimpervious, \
        qn_snowfree, qf, qs, vpd_hpa, s_hpa, rs, ra, rb, snowdensmax, snowdensmin, \
        precip, pipecapacity, runofftowater, addveg, snowlimpaved, snowlimbldg, \
        flowchange, drain, wetthresh_surf, soilstorecap, tsurf_ind, sfr_surf, \
        addwater, addwaterrunoff, storedrainprm, snowpacklimit, snowprof_24hr, \
        snowpack_in, snowfrac_in, snowwater_in, icefrac_in, snowdens_in, \
        snowfallcum_in, state_id_in, soilstore_id_in, qn_surf, qs_surf, snowremoval, \
        snowpack_out, snowfrac_out, snowwater_out, icefrac_out, snowdens_out, \
        state_id_out, soilstore_id_out, qe_surf, qe_roof, qe_wall, rss_surf, \
        dataoutlinesnow):
        """
        snowfallcum_out, state_per_tstep, nwstate_per_tstep, qe, snowalb_out, swe, \
            chsnow_per_tstep, ev_per_tstep, runoff_per_tstep, surf_chang_per_tstep, \
            runoffpipes, mwstore, runoffwaterbody, runoffagveg, runoffagimpervious = \
            suews_cal_snow(diagnose, nlayer, tstep, imin, it, evapmethod, dayofweek_id, \
            crwmin, crwmax, dectime, avdens, avcp, lv_j_kg, lvs_j_kg, avrh, press_hpa, \
            temp_c, rasnow, psyc_hpa, sice_hpa, tau_r, radmeltfact, tempmeltfact, \
            snowalbmax, preciplimit, preciplimitalb, qn_ind_snow, kup_ind_snow, deltaqi, \
            tsurf_ind_snow, snowalb_in, pervfraction, vegfraction, addimpervious, \
            qn_snowfree, qf, qs, vpd_hpa, s_hpa, rs, ra, rb, snowdensmax, snowdensmin, \
            precip, pipecapacity, runofftowater, addveg, snowlimpaved, snowlimbldg, \
            flowchange, drain, wetthresh_surf, soilstorecap, tsurf_ind, sfr_surf, \
            addwater, addwaterrunoff, storedrainprm, snowpacklimit, snowprof_24hr, \
            snowpack_in, snowfrac_in, snowwater_in, icefrac_in, snowdens_in, \
            snowfallcum_in, state_id_in, soilstore_id_in, qn_surf, qs_surf, snowremoval, \
            snowpack_out, snowfrac_out, snowwater_out, icefrac_out, snowdens_out, \
            state_id_out, soilstore_id_out, qe_surf, qe_roof, qe_wall, rss_surf, \
            dataoutlinesnow)
        
        
        Defined at suews_ctrl_driver.fpp lines 2335-2636
        
        Parameters
        ----------
        diagnose : int
        nlayer : int
        tstep : int
        imin : int
        it : int
        evapmethod : int
        dayofweek_id : int array
        crwmin : float
        crwmax : float
        dectime : float
        avdens : float
        avcp : float
        lv_j_kg : float
        lvs_j_kg : float
        avrh : float
        press_hpa : float
        temp_c : float
        rasnow : float
        psyc_hpa : float
        sice_hpa : float
        tau_r : float
        radmeltfact : float
        tempmeltfact : float
        snowalbmax : float
        preciplimit : float
        preciplimitalb : float
        qn_ind_snow : float array
        kup_ind_snow : float array
        deltaqi : float array
        tsurf_ind_snow : float array
        snowalb_in : float
        pervfraction : float
        vegfraction : float
        addimpervious : float
        qn_snowfree : float
        qf : float
        qs : float
        vpd_hpa : float
        s_hpa : float
        rs : float
        ra : float
        rb : float
        snowdensmax : float
        snowdensmin : float
        precip : float
        pipecapacity : float
        runofftowater : float
        addveg : float
        snowlimpaved : float
        snowlimbldg : float
        flowchange : float
        drain : float array
        wetthresh_surf : float array
        soilstorecap : float array
        tsurf_ind : float array
        sfr_surf : float array
        addwater : float array
        addwaterrunoff : float array
        storedrainprm : float array
        snowpacklimit : float array
        snowprof_24hr : float array
        snowpack_in : float array
        snowfrac_in : float array
        snowwater_in : float array
        icefrac_in : float array
        snowdens_in : float array
        snowfallcum_in : float
        state_id_in : float array
        soilstore_id_in : float array
        qn_surf : float array
        qs_surf : float array
        snowremoval : float array
        snowpack_out : float array
        snowfrac_out : float array
        snowwater_out : float array
        icefrac_out : float array
        snowdens_out : float array
        state_id_out : float array
        soilstore_id_out : float array
        qe_surf : float array
        qe_roof : float array
        qe_wall : float array
        rss_surf : float array
        dataoutlinesnow : float array
        
        Returns
        -------
        snowfallcum_out : float
        state_per_tstep : float
        nwstate_per_tstep : float
        qe : float
        snowalb_out : float
        swe : float
        chsnow_per_tstep : float
        ev_per_tstep : float
        runoff_per_tstep : float
        surf_chang_per_tstep : float
        runoffpipes : float
        mwstore : float
        runoffwaterbody : float
        runoffagveg : float
        runoffagimpervious : float
        
        """
        snowfallcum_out, state_per_tstep, nwstate_per_tstep, qe, snowalb_out, swe, \
            chsnow_per_tstep, ev_per_tstep, runoff_per_tstep, surf_chang_per_tstep, \
            runoffpipes, mwstore, runoffwaterbody, runoffagveg, runoffagimpervious = \
            _supy_driver.f90wrap_suews_cal_snow(diagnose=diagnose, nlayer=nlayer, \
            tstep=tstep, imin=imin, it=it, evapmethod=evapmethod, \
            dayofweek_id=dayofweek_id, crwmin=crwmin, crwmax=crwmax, dectime=dectime, \
            avdens=avdens, avcp=avcp, lv_j_kg=lv_j_kg, lvs_j_kg=lvs_j_kg, avrh=avrh, \
            press_hpa=press_hpa, temp_c=temp_c, rasnow=rasnow, psyc_hpa=psyc_hpa, \
            sice_hpa=sice_hpa, tau_r=tau_r, radmeltfact=radmeltfact, \
            tempmeltfact=tempmeltfact, snowalbmax=snowalbmax, preciplimit=preciplimit, \
            preciplimitalb=preciplimitalb, qn_ind_snow=qn_ind_snow, \
            kup_ind_snow=kup_ind_snow, deltaqi=deltaqi, tsurf_ind_snow=tsurf_ind_snow, \
            snowalb_in=snowalb_in, pervfraction=pervfraction, vegfraction=vegfraction, \
            addimpervious=addimpervious, qn_snowfree=qn_snowfree, qf=qf, qs=qs, \
            vpd_hpa=vpd_hpa, s_hpa=s_hpa, rs=rs, ra=ra, rb=rb, snowdensmax=snowdensmax, \
            snowdensmin=snowdensmin, precip=precip, pipecapacity=pipecapacity, \
            runofftowater=runofftowater, addveg=addveg, snowlimpaved=snowlimpaved, \
            snowlimbldg=snowlimbldg, flowchange=flowchange, drain=drain, \
            wetthresh_surf=wetthresh_surf, soilstorecap=soilstorecap, \
            tsurf_ind=tsurf_ind, sfr_surf=sfr_surf, addwater=addwater, \
            addwaterrunoff=addwaterrunoff, storedrainprm=storedrainprm, \
            snowpacklimit=snowpacklimit, snowprof_24hr=snowprof_24hr, \
            snowpack_in=snowpack_in, snowfrac_in=snowfrac_in, snowwater_in=snowwater_in, \
            icefrac_in=icefrac_in, snowdens_in=snowdens_in, \
            snowfallcum_in=snowfallcum_in, state_id_in=state_id_in, \
            soilstore_id_in=soilstore_id_in, qn_surf=qn_surf, qs_surf=qs_surf, \
            snowremoval=snowremoval, snowpack_out=snowpack_out, \
            snowfrac_out=snowfrac_out, snowwater_out=snowwater_out, \
            icefrac_out=icefrac_out, snowdens_out=snowdens_out, \
            state_id_out=state_id_out, soilstore_id_out=soilstore_id_out, \
            qe_surf=qe_surf, qe_roof=qe_roof, qe_wall=qe_wall, rss_surf=rss_surf, \
            dataoutlinesnow=dataoutlinesnow)
        return snowfallcum_out, state_per_tstep, nwstate_per_tstep, qe, snowalb_out, \
            swe, chsnow_per_tstep, ev_per_tstep, runoff_per_tstep, surf_chang_per_tstep, \
            runoffpipes, mwstore, runoffwaterbody, runoffagveg, runoffagimpervious
    
    @staticmethod
    def suews_cal_qe(diagnose, storageheatmethod, nlayer, tstep, evapmethod, avdens, \
        avcp, lv_j_kg, psyc_hpa, pervfraction, addimpervious, qf, vpd_hpa, s_hpa, \
        rs, ra_h, rb, precip, pipecapacity, runofftowater, nonwaterfraction, \
        wu_surf, addveg, addwaterbody, addwater_surf, flowchange, drain_surf, \
        frac_water2runoff_surf, storedrainprm, sfr_surf, statelimit_surf, \
        soilstorecap_surf, wetthresh_surf, state_surf_in, soilstore_surf_in, \
        qn_surf, qs_surf, sfr_roof, statelimit_roof, soilstorecap_roof, \
        wetthresh_roof, state_roof_in, soilstore_roof_in, qn_roof, qs_roof, \
        sfr_wall, statelimit_wall, soilstorecap_wall, wetthresh_wall, state_wall_in, \
        soilstore_wall_in, qn_wall, qs_wall, state_surf_out, soilstore_surf_out, \
        ev_surf, state_roof_out, soilstore_roof_out, ev_roof, state_wall_out, \
        soilstore_wall_out, ev_wall, ev0_surf, qe0_surf, qe_surf, qe_roof, qe_wall, \
        rss_surf):
        """
        state_grid, nwstate_grid, qe, ev_grid, runoff_grid, surf_chang_grid, \
            runoffpipes_grid, runoffwaterbody_grid, runoffagveg_grid, \
            runoffagimpervious_grid = suews_cal_qe(diagnose, storageheatmethod, nlayer, \
            tstep, evapmethod, avdens, avcp, lv_j_kg, psyc_hpa, pervfraction, \
            addimpervious, qf, vpd_hpa, s_hpa, rs, ra_h, rb, precip, pipecapacity, \
            runofftowater, nonwaterfraction, wu_surf, addveg, addwaterbody, \
            addwater_surf, flowchange, drain_surf, frac_water2runoff_surf, \
            storedrainprm, sfr_surf, statelimit_surf, soilstorecap_surf, wetthresh_surf, \
            state_surf_in, soilstore_surf_in, qn_surf, qs_surf, sfr_roof, \
            statelimit_roof, soilstorecap_roof, wetthresh_roof, state_roof_in, \
            soilstore_roof_in, qn_roof, qs_roof, sfr_wall, statelimit_wall, \
            soilstorecap_wall, wetthresh_wall, state_wall_in, soilstore_wall_in, \
            qn_wall, qs_wall, state_surf_out, soilstore_surf_out, ev_surf, \
            state_roof_out, soilstore_roof_out, ev_roof, state_wall_out, \
            soilstore_wall_out, ev_wall, ev0_surf, qe0_surf, qe_surf, qe_roof, qe_wall, \
            rss_surf)
        
        
        Defined at suews_ctrl_driver.fpp lines 2668-2927
        
        Parameters
        ----------
        diagnose : int
        storageheatmethod : int
        nlayer : int
        tstep : int
        evapmethod : int
        avdens : float
        avcp : float
        lv_j_kg : float
        psyc_hpa : float
        pervfraction : float
        addimpervious : float
        qf : float
        vpd_hpa : float
        s_hpa : float
        rs : float
        ra_h : float
        rb : float
        precip : float
        pipecapacity : float
        runofftowater : float
        nonwaterfraction : float
        wu_surf : float array
        addveg : float
        addwaterbody : float
        addwater_surf : float array
        flowchange : float
        drain_surf : float array
        frac_water2runoff_surf : float array
        storedrainprm : float array
        sfr_surf : float array
        statelimit_surf : float array
        soilstorecap_surf : float array
        wetthresh_surf : float array
        state_surf_in : float array
        soilstore_surf_in : float array
        qn_surf : float array
        qs_surf : float array
        sfr_roof : float array
        statelimit_roof : float array
        soilstorecap_roof : float array
        wetthresh_roof : float array
        state_roof_in : float array
        soilstore_roof_in : float array
        qn_roof : float array
        qs_roof : float array
        sfr_wall : float array
        statelimit_wall : float array
        soilstorecap_wall : float array
        wetthresh_wall : float array
        state_wall_in : float array
        soilstore_wall_in : float array
        qn_wall : float array
        qs_wall : float array
        state_surf_out : float array
        soilstore_surf_out : float array
        ev_surf : float array
        state_roof_out : float array
        soilstore_roof_out : float array
        ev_roof : float array
        state_wall_out : float array
        soilstore_wall_out : float array
        ev_wall : float array
        ev0_surf : float array
        qe0_surf : float array
        qe_surf : float array
        qe_roof : float array
        qe_wall : float array
        rss_surf : float array
        
        Returns
        -------
        state_grid : float
        nwstate_grid : float
        qe : float
        ev_grid : float
        runoff_grid : float
        surf_chang_grid : float
        runoffpipes_grid : float
        runoffwaterbody_grid : float
        runoffagveg_grid : float
        runoffagimpervious_grid : float
        
        """
        state_grid, nwstate_grid, qe, ev_grid, runoff_grid, surf_chang_grid, \
            runoffpipes_grid, runoffwaterbody_grid, runoffagveg_grid, \
            runoffagimpervious_grid = \
            _supy_driver.f90wrap_suews_cal_qe(diagnose=diagnose, \
            storageheatmethod=storageheatmethod, nlayer=nlayer, tstep=tstep, \
            evapmethod=evapmethod, avdens=avdens, avcp=avcp, lv_j_kg=lv_j_kg, \
            psyc_hpa=psyc_hpa, pervfraction=pervfraction, addimpervious=addimpervious, \
            qf=qf, vpd_hpa=vpd_hpa, s_hpa=s_hpa, rs=rs, ra_h=ra_h, rb=rb, precip=precip, \
            pipecapacity=pipecapacity, runofftowater=runofftowater, \
            nonwaterfraction=nonwaterfraction, wu_surf=wu_surf, addveg=addveg, \
            addwaterbody=addwaterbody, addwater_surf=addwater_surf, \
            flowchange=flowchange, drain_surf=drain_surf, \
            frac_water2runoff_surf=frac_water2runoff_surf, storedrainprm=storedrainprm, \
            sfr_surf=sfr_surf, statelimit_surf=statelimit_surf, \
            soilstorecap_surf=soilstorecap_surf, wetthresh_surf=wetthresh_surf, \
            state_surf_in=state_surf_in, soilstore_surf_in=soilstore_surf_in, \
            qn_surf=qn_surf, qs_surf=qs_surf, sfr_roof=sfr_roof, \
            statelimit_roof=statelimit_roof, soilstorecap_roof=soilstorecap_roof, \
            wetthresh_roof=wetthresh_roof, state_roof_in=state_roof_in, \
            soilstore_roof_in=soilstore_roof_in, qn_roof=qn_roof, qs_roof=qs_roof, \
            sfr_wall=sfr_wall, statelimit_wall=statelimit_wall, \
            soilstorecap_wall=soilstorecap_wall, wetthresh_wall=wetthresh_wall, \
            state_wall_in=state_wall_in, soilstore_wall_in=soilstore_wall_in, \
            qn_wall=qn_wall, qs_wall=qs_wall, state_surf_out=state_surf_out, \
            soilstore_surf_out=soilstore_surf_out, ev_surf=ev_surf, \
            state_roof_out=state_roof_out, soilstore_roof_out=soilstore_roof_out, \
            ev_roof=ev_roof, state_wall_out=state_wall_out, \
            soilstore_wall_out=soilstore_wall_out, ev_wall=ev_wall, ev0_surf=ev0_surf, \
            qe0_surf=qe0_surf, qe_surf=qe_surf, qe_roof=qe_roof, qe_wall=qe_wall, \
            rss_surf=rss_surf)
        return state_grid, nwstate_grid, qe, ev_grid, runoff_grid, surf_chang_grid, \
            runoffpipes_grid, runoffwaterbody_grid, runoffagveg_grid, \
            runoffagimpervious_grid
    
    @staticmethod
    def suews_cal_qh(qhmethod, nlayer, storageheatmethod, qn, qf, qmrain, qe, qs, \
        qmfreez, qm, avdens, avcp, sfr_surf, sfr_roof, sfr_wall, tsfc_surf, \
        tsfc_roof, tsfc_wall, temp_c, ra, qh_resist_surf, qh_resist_roof, \
        qh_resist_wall):
        """
        qh, qh_residual, qh_resist = suews_cal_qh(qhmethod, nlayer, storageheatmethod, \
            qn, qf, qmrain, qe, qs, qmfreez, qm, avdens, avcp, sfr_surf, sfr_roof, \
            sfr_wall, tsfc_surf, tsfc_roof, tsfc_wall, temp_c, ra, qh_resist_surf, \
            qh_resist_roof, qh_resist_wall)
        
        
        Defined at suews_ctrl_driver.fpp lines 2939-3005
        
        Parameters
        ----------
        qhmethod : int
        nlayer : int
        storageheatmethod : int
        qn : float
        qf : float
        qmrain : float
        qe : float
        qs : float
        qmfreez : float
        qm : float
        avdens : float
        avcp : float
        sfr_surf : float array
        sfr_roof : float array
        sfr_wall : float array
        tsfc_surf : float array
        tsfc_roof : float array
        tsfc_wall : float array
        temp_c : float
        ra : float
        qh_resist_surf : float array
        qh_resist_roof : float array
        qh_resist_wall : float array
        
        Returns
        -------
        qh : float
        qh_residual : float
        qh_resist : float
        
        """
        qh, qh_residual, qh_resist = \
            _supy_driver.f90wrap_suews_cal_qh(qhmethod=qhmethod, nlayer=nlayer, \
            storageheatmethod=storageheatmethod, qn=qn, qf=qf, qmrain=qmrain, qe=qe, \
            qs=qs, qmfreez=qmfreez, qm=qm, avdens=avdens, avcp=avcp, sfr_surf=sfr_surf, \
            sfr_roof=sfr_roof, sfr_wall=sfr_wall, tsfc_surf=tsfc_surf, \
            tsfc_roof=tsfc_roof, tsfc_wall=tsfc_wall, temp_c=temp_c, ra=ra, \
            qh_resist_surf=qh_resist_surf, qh_resist_roof=qh_resist_roof, \
            qh_resist_wall=qh_resist_wall)
        return qh, qh_residual, qh_resist
    
    @staticmethod
    def suews_cal_resistance(stabilitymethod, diagnose, aerodynamicresistancemethod, \
        roughlenheatmethod, snowuse, id, it, gsmodel, smdmethod, avdens, avcp, \
        qh_init, zzd, z0m, zdm, avu1, temp_c, vegfraction, avkdn, kmax, g_max, g_k, \
        g_q_base, g_q_shape, g_t, g_sm, s1, s2, th, tl, dq, xsmd, vsmd, \
        maxconductance, laimax, lai_id, snowfrac, sfr_surf):
        """
        g_kdown, g_dq, g_ta, g_smd, g_lai, ustar, tstar, l_mod, zl, gsc, rs, ra, rasnow, \
            rb, z0v, z0vsnow = suews_cal_resistance(stabilitymethod, diagnose, \
            aerodynamicresistancemethod, roughlenheatmethod, snowuse, id, it, gsmodel, \
            smdmethod, avdens, avcp, qh_init, zzd, z0m, zdm, avu1, temp_c, vegfraction, \
            avkdn, kmax, g_max, g_k, g_q_base, g_q_shape, g_t, g_sm, s1, s2, th, tl, dq, \
            xsmd, vsmd, maxconductance, laimax, lai_id, snowfrac, sfr_surf)
        
        
        Defined at suews_ctrl_driver.fpp lines 3022-3143
        
        Parameters
        ----------
        stabilitymethod : int
        diagnose : int
        aerodynamicresistancemethod : int
        roughlenheatmethod : int
        snowuse : int
        id : int
        it : int
        gsmodel : int
        smdmethod : int
        avdens : float
        avcp : float
        qh_init : float
        zzd : float
        z0m : float
        zdm : float
        avu1 : float
        temp_c : float
        vegfraction : float
        avkdn : float
        kmax : float
        g_max : float
        g_k : float
        g_q_base : float
        g_q_shape : float
        g_t : float
        g_sm : float
        s1 : float
        s2 : float
        th : float
        tl : float
        dq : float
        xsmd : float
        vsmd : float
        maxconductance : float array
        laimax : float array
        lai_id : float array
        snowfrac : float array
        sfr_surf : float array
        
        Returns
        -------
        g_kdown : float
        g_dq : float
        g_ta : float
        g_smd : float
        g_lai : float
        ustar : float
        tstar : float
        l_mod : float
        zl : float
        gsc : float
        rs : float
        ra : float
        rasnow : float
        rb : float
        z0v : float
        z0vsnow : float
        
        """
        g_kdown, g_dq, g_ta, g_smd, g_lai, ustar, tstar, l_mod, zl, gsc, rs, ra, rasnow, \
            rb, z0v, z0vsnow = \
            _supy_driver.f90wrap_suews_cal_resistance(stabilitymethod=stabilitymethod, \
            diagnose=diagnose, aerodynamicresistancemethod=aerodynamicresistancemethod, \
            roughlenheatmethod=roughlenheatmethod, snowuse=snowuse, id=id, it=it, \
            gsmodel=gsmodel, smdmethod=smdmethod, avdens=avdens, avcp=avcp, \
            qh_init=qh_init, zzd=zzd, z0m=z0m, zdm=zdm, avu1=avu1, temp_c=temp_c, \
            vegfraction=vegfraction, avkdn=avkdn, kmax=kmax, g_max=g_max, g_k=g_k, \
            g_q_base=g_q_base, g_q_shape=g_q_shape, g_t=g_t, g_sm=g_sm, s1=s1, s2=s2, \
            th=th, tl=tl, dq=dq, xsmd=xsmd, vsmd=vsmd, maxconductance=maxconductance, \
            laimax=laimax, lai_id=lai_id, snowfrac=snowfrac, sfr_surf=sfr_surf)
        return g_kdown, g_dq, g_ta, g_smd, g_lai, ustar, tstar, l_mod, zl, gsc, rs, ra, \
            rasnow, rb, z0v, z0vsnow
    
    @staticmethod
    def suews_update_outputline(additionalwater, alb, avkdn, avu10_ms, azimuth, \
        chsnow_per_interval, dectime, drain_per_tstep, e_mod, ev_per_tstep, ext_wu, \
        fc, fc_build, fcld, fc_metab, fc_photo, fc_respi, fc_point, fc_traff, \
        flowchange, h_mod, id, imin, int_wu, it, iy, kup, lai_id, ldown, l_mod, lup, \
        mwh, mwstore, nsh_real, nwstate_per_tstep, precip, q2_gkg, qeout, qf, qh, \
        qh_resist, qm, qmfreez, qmrain, qn, qn_snow, qn_snowfree, qs, ra, \
        resistsurf, rh2, runoffagimpervious, runoffagveg, runoff_per_tstep, \
        runoffpipes, runoffsoil_per_tstep, runoffwaterbody, sfr_surf, smd, \
        smd_nsurf, snowalb, snowremoval, state_id, state_per_tstep, \
        surf_chang_per_tstep, swe, t2_c, tskin_c, tot_chang_per_tstep, tsurf, ustar, \
        wu_nsurf, z0m, zdm, zenith_deg, datetimeline, dataoutlinesuews):
        """
        suews_update_outputline(additionalwater, alb, avkdn, avu10_ms, azimuth, \
            chsnow_per_interval, dectime, drain_per_tstep, e_mod, ev_per_tstep, ext_wu, \
            fc, fc_build, fcld, fc_metab, fc_photo, fc_respi, fc_point, fc_traff, \
            flowchange, h_mod, id, imin, int_wu, it, iy, kup, lai_id, ldown, l_mod, lup, \
            mwh, mwstore, nsh_real, nwstate_per_tstep, precip, q2_gkg, qeout, qf, qh, \
            qh_resist, qm, qmfreez, qmrain, qn, qn_snow, qn_snowfree, qs, ra, \
            resistsurf, rh2, runoffagimpervious, runoffagveg, runoff_per_tstep, \
            runoffpipes, runoffsoil_per_tstep, runoffwaterbody, sfr_surf, smd, \
            smd_nsurf, snowalb, snowremoval, state_id, state_per_tstep, \
            surf_chang_per_tstep, swe, t2_c, tskin_c, tot_chang_per_tstep, tsurf, ustar, \
            wu_nsurf, z0m, zdm, zenith_deg, datetimeline, dataoutlinesuews)
        
        
        Defined at suews_ctrl_driver.fpp lines 3165-3313
        
        Parameters
        ----------
        additionalwater : float
        alb : float array
        avkdn : float
        avu10_ms : float
        azimuth : float
        chsnow_per_interval : float
        dectime : float
        drain_per_tstep : float
        e_mod : float
        ev_per_tstep : float
        ext_wu : float
        fc : float
        fc_build : float
        fcld : float
        fc_metab : float
        fc_photo : float
        fc_respi : float
        fc_point : float
        fc_traff : float
        flowchange : float
        h_mod : float
        id : int
        imin : int
        int_wu : float
        it : int
        iy : int
        kup : float
        lai_id : float array
        ldown : float
        l_mod : float
        lup : float
        mwh : float
        mwstore : float
        nsh_real : float
        nwstate_per_tstep : float
        precip : float
        q2_gkg : float
        qeout : float
        qf : float
        qh : float
        qh_resist : float
        qm : float
        qmfreez : float
        qmrain : float
        qn : float
        qn_snow : float
        qn_snowfree : float
        qs : float
        ra : float
        resistsurf : float
        rh2 : float
        runoffagimpervious : float
        runoffagveg : float
        runoff_per_tstep : float
        runoffpipes : float
        runoffsoil_per_tstep : float
        runoffwaterbody : float
        sfr_surf : float array
        smd : float
        smd_nsurf : float array
        snowalb : float
        snowremoval : float array
        state_id : float array
        state_per_tstep : float
        surf_chang_per_tstep : float
        swe : float
        t2_c : float
        tskin_c : float
        tot_chang_per_tstep : float
        tsurf : float
        ustar : float
        wu_nsurf : float array
        z0m : float
        zdm : float
        zenith_deg : float
        datetimeline : float array
        dataoutlinesuews : float array
        
        =====================================================================
        ====================== Prepare data for output ======================
         values outside of reasonable range are set as NAN-like numbers. TS 10 Jun 2018
         Remove non-existing surface type from surface and soil outputs
         Added back in with NANs by HCW 24 Aug 2016
        """
        _supy_driver.f90wrap_suews_update_outputline(additionalwater=additionalwater, \
            alb=alb, avkdn=avkdn, avu10_ms=avu10_ms, azimuth=azimuth, \
            chsnow_per_interval=chsnow_per_interval, dectime=dectime, \
            drain_per_tstep=drain_per_tstep, e_mod=e_mod, ev_per_tstep=ev_per_tstep, \
            ext_wu=ext_wu, fc=fc, fc_build=fc_build, fcld=fcld, fc_metab=fc_metab, \
            fc_photo=fc_photo, fc_respi=fc_respi, fc_point=fc_point, fc_traff=fc_traff, \
            flowchange=flowchange, h_mod=h_mod, id=id, imin=imin, int_wu=int_wu, it=it, \
            iy=iy, kup=kup, lai_id=lai_id, ldown=ldown, l_mod=l_mod, lup=lup, mwh=mwh, \
            mwstore=mwstore, nsh_real=nsh_real, nwstate_per_tstep=nwstate_per_tstep, \
            precip=precip, q2_gkg=q2_gkg, qeout=qeout, qf=qf, qh=qh, \
            qh_resist=qh_resist, qm=qm, qmfreez=qmfreez, qmrain=qmrain, qn=qn, \
            qn_snow=qn_snow, qn_snowfree=qn_snowfree, qs=qs, ra=ra, \
            resistsurf=resistsurf, rh2=rh2, runoffagimpervious=runoffagimpervious, \
            runoffagveg=runoffagveg, runoff_per_tstep=runoff_per_tstep, \
            runoffpipes=runoffpipes, runoffsoil_per_tstep=runoffsoil_per_tstep, \
            runoffwaterbody=runoffwaterbody, sfr_surf=sfr_surf, smd=smd, \
            smd_nsurf=smd_nsurf, snowalb=snowalb, snowremoval=snowremoval, \
            state_id=state_id, state_per_tstep=state_per_tstep, \
            surf_chang_per_tstep=surf_chang_per_tstep, swe=swe, t2_c=t2_c, \
            tskin_c=tskin_c, tot_chang_per_tstep=tot_chang_per_tstep, tsurf=tsurf, \
            ustar=ustar, wu_nsurf=wu_nsurf, z0m=z0m, zdm=zdm, zenith_deg=zenith_deg, \
            datetimeline=datetimeline, dataoutlinesuews=dataoutlinesuews)
    
    @staticmethod
    def estmext_update_outputline(iy, id, it, imin, dectime, nlayer, tsfc_out_surf, \
        qs_surf, tsfc_out_roof, qn_roof, qs_roof, qe_roof, qh_roof, state_roof, \
        soilstore_roof, tsfc_out_wall, qn_wall, qs_wall, qe_wall, qh_wall, \
        state_wall, soilstore_wall, datetimeline, dataoutlineestmext):
        """
        estmext_update_outputline(iy, id, it, imin, dectime, nlayer, tsfc_out_surf, \
            qs_surf, tsfc_out_roof, qn_roof, qs_roof, qe_roof, qh_roof, state_roof, \
            soilstore_roof, tsfc_out_wall, qn_wall, qs_wall, qe_wall, qh_wall, \
            state_wall, soilstore_wall, datetimeline, dataoutlineestmext)
        
        
        Defined at suews_ctrl_driver.fpp lines 3334-3401
        
        Parameters
        ----------
        iy : int
        id : int
        it : int
        imin : int
        dectime : float
        nlayer : int
        tsfc_out_surf : float array
        qs_surf : float array
        tsfc_out_roof : float array
        qn_roof : float array
        qs_roof : float array
        qe_roof : float array
        qh_roof : float array
        state_roof : float array
        soilstore_roof : float array
        tsfc_out_wall : float array
        qn_wall : float array
        qs_wall : float array
        qe_wall : float array
        qh_wall : float array
        state_wall : float array
        soilstore_wall : float array
        datetimeline : float array
        dataoutlineestmext : float array
        
        ====================update output line end==============================
        """
        _supy_driver.f90wrap_estmext_update_outputline(iy=iy, id=id, it=it, imin=imin, \
            dectime=dectime, nlayer=nlayer, tsfc_out_surf=tsfc_out_surf, \
            qs_surf=qs_surf, tsfc_out_roof=tsfc_out_roof, qn_roof=qn_roof, \
            qs_roof=qs_roof, qe_roof=qe_roof, qh_roof=qh_roof, state_roof=state_roof, \
            soilstore_roof=soilstore_roof, tsfc_out_wall=tsfc_out_wall, qn_wall=qn_wall, \
            qs_wall=qs_wall, qe_wall=qe_wall, qh_wall=qh_wall, state_wall=state_wall, \
            soilstore_wall=soilstore_wall, datetimeline=datetimeline, \
            dataoutlineestmext=dataoutlineestmext)
    
    @staticmethod
    def fill_result_x(res_valid, n_fill):
        """
        res_filled = fill_result_x(res_valid, n_fill)
        
        
        Defined at suews_ctrl_driver.fpp lines 3404-3410
        
        Parameters
        ----------
        res_valid : float array
        n_fill : int
        
        Returns
        -------
        res_filled : float array
        
        """
        res_filled = _supy_driver.f90wrap_fill_result_x(res_valid=res_valid, \
            n_fill=n_fill)
        return res_filled
    
    @staticmethod
    def suews_update_output(snowuse, storageheatmethod, readlinesmetdata, \
        numberofgrids, ir, gridiv, dataoutlinesuews, dataoutlinesnow, \
        dataoutlineestm, dataoutlinersl, dataoutlinebeers, dataoutlinedebug, \
        dataoutlinespartacus, dataoutlineestmext, dataoutsuews, dataoutsnow, \
        dataoutestm, dataoutrsl, dataoutbeers, dataoutdebug, dataoutspartacus, \
        dataoutestmext):
        """
        suews_update_output(snowuse, storageheatmethod, readlinesmetdata, numberofgrids, \
            ir, gridiv, dataoutlinesuews, dataoutlinesnow, dataoutlineestm, \
            dataoutlinersl, dataoutlinebeers, dataoutlinedebug, dataoutlinespartacus, \
            dataoutlineestmext, dataoutsuews, dataoutsnow, dataoutestm, dataoutrsl, \
            dataoutbeers, dataoutdebug, dataoutspartacus, dataoutestmext)
        
        
        Defined at suews_ctrl_driver.fpp lines 3420-3465
        
        Parameters
        ----------
        snowuse : int
        storageheatmethod : int
        readlinesmetdata : int
        numberofgrids : int
        ir : int
        gridiv : int
        dataoutlinesuews : float array
        dataoutlinesnow : float array
        dataoutlineestm : float array
        dataoutlinersl : float array
        dataoutlinebeers : float array
        dataoutlinedebug : float array
        dataoutlinespartacus : float array
        dataoutlineestmext : float array
        dataoutsuews : float array
        dataoutsnow : float array
        dataoutestm : float array
        dataoutrsl : float array
        dataoutbeers : float array
        dataoutdebug : float array
        dataoutspartacus : float array
        dataoutestmext : float array
        
        ====================== update output arrays ==============================
        Define the overall output matrix to be printed out step by step
        """
        _supy_driver.f90wrap_suews_update_output(snowuse=snowuse, \
            storageheatmethod=storageheatmethod, readlinesmetdata=readlinesmetdata, \
            numberofgrids=numberofgrids, ir=ir, gridiv=gridiv, \
            dataoutlinesuews=dataoutlinesuews, dataoutlinesnow=dataoutlinesnow, \
            dataoutlineestm=dataoutlineestm, dataoutlinersl=dataoutlinersl, \
            dataoutlinebeers=dataoutlinebeers, dataoutlinedebug=dataoutlinedebug, \
            dataoutlinespartacus=dataoutlinespartacus, \
            dataoutlineestmext=dataoutlineestmext, dataoutsuews=dataoutsuews, \
            dataoutsnow=dataoutsnow, dataoutestm=dataoutestm, dataoutrsl=dataoutrsl, \
            dataoutbeers=dataoutbeers, dataoutdebug=dataoutdebug, \
            dataoutspartacus=dataoutspartacus, dataoutestmext=dataoutestmext)
    
    @staticmethod
    def suews_cal_surf(storageheatmethod, netradiationmethod, nlayer, sfr_surf, \
        building_frac, building_scale, height, sfr_roof, sfr_wall):
        """
        vegfraction, impervfraction, pervfraction, nonwaterfraction = \
            suews_cal_surf(storageheatmethod, netradiationmethod, nlayer, sfr_surf, \
            building_frac, building_scale, height, sfr_roof, sfr_wall)
        
        
        Defined at suews_ctrl_driver.fpp lines 3535-3578
        
        Parameters
        ----------
        storageheatmethod : int
        netradiationmethod : int
        nlayer : int
        sfr_surf : float array
        building_frac : float array
        building_scale : float array
        height : float array
        sfr_roof : float array
        sfr_wall : float array
        
        Returns
        -------
        vegfraction : float
        impervfraction : float
        pervfraction : float
        nonwaterfraction : float
        
        """
        vegfraction, impervfraction, pervfraction, nonwaterfraction = \
            _supy_driver.f90wrap_suews_cal_surf(storageheatmethod=storageheatmethod, \
            netradiationmethod=netradiationmethod, nlayer=nlayer, sfr_surf=sfr_surf, \
            building_frac=building_frac, building_scale=building_scale, height=height, \
            sfr_roof=sfr_roof, sfr_wall=sfr_wall)
        return vegfraction, impervfraction, pervfraction, nonwaterfraction
    
    @staticmethod
    def set_nan(x):
        """
        xx = set_nan(x)
        
        
        Defined at suews_ctrl_driver.fpp lines 3697-3710
        
        Parameters
        ----------
        x : float
        
        Returns
        -------
        xx : float
        
        """
        xx = _supy_driver.f90wrap_set_nan(x=x)
        return xx
    
    @staticmethod
    def square(x):
        """
        xx = square(x)
        
        
        Defined at suews_ctrl_driver.fpp lines 3714-3721
        
        Parameters
        ----------
        x : float
        
        Returns
        -------
        xx : float
        
        """
        xx = _supy_driver.f90wrap_square(x=x)
        return xx
    
    @staticmethod
    def square_real(x):
        """
        xx = square_real(x)
        
        
        Defined at suews_ctrl_driver.fpp lines 3723-3730
        
        Parameters
        ----------
        x : float
        
        Returns
        -------
        xx : float
        
        """
        xx = _supy_driver.f90wrap_square_real(x=x)
        return xx
    
    @staticmethod
    def output_name_n(i):
        """
        name, group, aggreg, outlevel = output_name_n(i)
        
        
        Defined at suews_ctrl_driver.fpp lines 3732-3752
        
        Parameters
        ----------
        i : int
        
        Returns
        -------
        name : str
        group : str
        aggreg : str
        outlevel : int
        
        """
        name, group, aggreg, outlevel = _supy_driver.f90wrap_output_name_n(i=i)
        return name, group, aggreg, outlevel
    
    @staticmethod
    def output_size():
        """
        nvar = output_size()
        
        
        Defined at suews_ctrl_driver.fpp lines 3754-3823
        
        
        Returns
        -------
        nvar : int
        
        """
        nvar = _supy_driver.f90wrap_output_size()
        return nvar
    
    @staticmethod
    def suews_cal_multitsteps(metforcingblock, len_sim, ah_min, ahprof_24hr, \
        ah_slope_cooling, ah_slope_heating, alb, albmax_dectr, albmax_evetr, \
        albmax_grass, albmin_dectr, albmin_evetr, albmin_grass, alpha_bioco2, \
        alpha_enh_bioco2, alt, baset, basete, beta_bioco2, beta_enh_bioco2, bldgh, \
        capmax_dec, capmin_dec, chanohm, co2pointsource, cpanohm, crwmax, crwmin, \
        daywat, daywatper, dectreeh, diagmethod, diagnose, drainrt, dt_since_start, \
        dqndt, qn_av, dqnsdt, qn_s_av, ef_umolco2perj, emis, emissionsmethod, \
        enef_v_jkm, enddls, evetreeh, faibldg, faidectree, faievetree, faut, \
        fcef_v_kgkm, flowchange, frfossilfuel_heat, frfossilfuel_nonheat, g_max, \
        g_k, g_q_base, g_q_shape, g_t, g_sm, gdd_id, gddfull, gridiv, gsmodel, \
        h_maintain, hdd_id, humactivity_24hr, icefrac, ie_a, ie_end, ie_m, ie_start, \
        internalwateruse_h, irrfracpaved, irrfracbldgs, irrfracevetr, irrfracdectr, \
        irrfracgrass, irrfracbsoil, irrfracwater, kkanohm, kmax, lai_id, laimax, \
        laimin, laipower, laitype, lat, lng, maxconductance, maxfcmetab, maxqfmetab, \
        snowwater, minfcmetab, minqfmetab, min_res_bioco2, narp_emis_snow, \
        narp_trans_site, netradiationmethod, ohm_coef, ohmincqf, ohm_threshsw, \
        ohm_threshwd, pipecapacity, popdensdaytime, popdensnighttime, popprof_24hr, \
        pormax_dec, pormin_dec, preciplimit, preciplimitalb, qf0_beu, qf_a, qf_b, \
        qf_c, nlayer, n_vegetation_region_urban, n_stream_sw_urban, \
        n_stream_lw_urban, sw_dn_direct_frac, air_ext_sw, air_ssa_sw, veg_ssa_sw, \
        air_ext_lw, air_ssa_lw, veg_ssa_lw, veg_fsd_const, \
        veg_contact_fraction_const, ground_albedo_dir_mult_fact, \
        use_sw_direct_albedo, height, building_frac, veg_frac, building_scale, \
        veg_scale, alb_roof, emis_roof, alb_wall, emis_wall, \
        roof_albedo_dir_mult_fact, wall_specular_frac, radmeltfact, raincover, \
        rainmaxres, resp_a, resp_b, roughlenheatmethod, roughlenmommethod, \
        runofftowater, s1, s2, sathydraulicconduct, sddfull, sdd_id, smdmethod, \
        snowalb, snowalbmax, snowalbmin, snowpacklimit, snowdens, snowdensmax, \
        snowdensmin, snowfallcum, snowfrac, snowlimbldg, snowlimpaved, snowpack, \
        snowprof_24hr, snowuse, soildepth, stabilitymethod, startdls, \
        soilstore_surf, soilstorecap_surf, state_surf, statelimit_surf, \
        wetthresh_surf, soilstore_roof, soilstorecap_roof, state_roof, \
        statelimit_roof, wetthresh_roof, soilstore_wall, soilstorecap_wall, \
        state_wall, statelimit_wall, wetthresh_wall, storageheatmethod, \
        storedrainprm, surfacearea, tair_av, tau_a, tau_f, tau_r, baset_cooling, \
        baset_heating, tempmeltfact, th, theta_bioco2, timezone, tl, trafficrate, \
        trafficunits, sfr_surf, tsfc_roof, tsfc_wall, tsfc_surf, temp_roof, \
        temp_wall, temp_surf, tin_roof, tin_wall, tin_surf, k_wall, k_roof, k_surf, \
        cp_wall, cp_roof, cp_surf, dz_wall, dz_roof, dz_surf, tmin_id, tmax_id, \
        lenday_id, traffprof_24hr, ts5mindata_ir, tstep, tstep_prev, veg_type, \
        waterdist, waterusemethod, wuday_id, decidcap_id, albdectr_id, albevetr_id, \
        albgrass_id, porosity_id, wuprofa_24hr, wuprofm_24hr, z, z0m_in, zdm_in):
        """
        output_block_suews = suews_cal_multitsteps(metforcingblock, len_sim, ah_min, \
            ahprof_24hr, ah_slope_cooling, ah_slope_heating, alb, albmax_dectr, \
            albmax_evetr, albmax_grass, albmin_dectr, albmin_evetr, albmin_grass, \
            alpha_bioco2, alpha_enh_bioco2, alt, baset, basete, beta_bioco2, \
            beta_enh_bioco2, bldgh, capmax_dec, capmin_dec, chanohm, co2pointsource, \
            cpanohm, crwmax, crwmin, daywat, daywatper, dectreeh, diagmethod, diagnose, \
            drainrt, dt_since_start, dqndt, qn_av, dqnsdt, qn_s_av, ef_umolco2perj, \
            emis, emissionsmethod, enef_v_jkm, enddls, evetreeh, faibldg, faidectree, \
            faievetree, faut, fcef_v_kgkm, flowchange, frfossilfuel_heat, \
            frfossilfuel_nonheat, g_max, g_k, g_q_base, g_q_shape, g_t, g_sm, gdd_id, \
            gddfull, gridiv, gsmodel, h_maintain, hdd_id, humactivity_24hr, icefrac, \
            ie_a, ie_end, ie_m, ie_start, internalwateruse_h, irrfracpaved, \
            irrfracbldgs, irrfracevetr, irrfracdectr, irrfracgrass, irrfracbsoil, \
            irrfracwater, kkanohm, kmax, lai_id, laimax, laimin, laipower, laitype, lat, \
            lng, maxconductance, maxfcmetab, maxqfmetab, snowwater, minfcmetab, \
            minqfmetab, min_res_bioco2, narp_emis_snow, narp_trans_site, \
            netradiationmethod, ohm_coef, ohmincqf, ohm_threshsw, ohm_threshwd, \
            pipecapacity, popdensdaytime, popdensnighttime, popprof_24hr, pormax_dec, \
            pormin_dec, preciplimit, preciplimitalb, qf0_beu, qf_a, qf_b, qf_c, nlayer, \
            n_vegetation_region_urban, n_stream_sw_urban, n_stream_lw_urban, \
            sw_dn_direct_frac, air_ext_sw, air_ssa_sw, veg_ssa_sw, air_ext_lw, \
            air_ssa_lw, veg_ssa_lw, veg_fsd_const, veg_contact_fraction_const, \
            ground_albedo_dir_mult_fact, use_sw_direct_albedo, height, building_frac, \
            veg_frac, building_scale, veg_scale, alb_roof, emis_roof, alb_wall, \
            emis_wall, roof_albedo_dir_mult_fact, wall_specular_frac, radmeltfact, \
            raincover, rainmaxres, resp_a, resp_b, roughlenheatmethod, \
            roughlenmommethod, runofftowater, s1, s2, sathydraulicconduct, sddfull, \
            sdd_id, smdmethod, snowalb, snowalbmax, snowalbmin, snowpacklimit, snowdens, \
            snowdensmax, snowdensmin, snowfallcum, snowfrac, snowlimbldg, snowlimpaved, \
            snowpack, snowprof_24hr, snowuse, soildepth, stabilitymethod, startdls, \
            soilstore_surf, soilstorecap_surf, state_surf, statelimit_surf, \
            wetthresh_surf, soilstore_roof, soilstorecap_roof, state_roof, \
            statelimit_roof, wetthresh_roof, soilstore_wall, soilstorecap_wall, \
            state_wall, statelimit_wall, wetthresh_wall, storageheatmethod, \
            storedrainprm, surfacearea, tair_av, tau_a, tau_f, tau_r, baset_cooling, \
            baset_heating, tempmeltfact, th, theta_bioco2, timezone, tl, trafficrate, \
            trafficunits, sfr_surf, tsfc_roof, tsfc_wall, tsfc_surf, temp_roof, \
            temp_wall, temp_surf, tin_roof, tin_wall, tin_surf, k_wall, k_roof, k_surf, \
            cp_wall, cp_roof, cp_surf, dz_wall, dz_roof, dz_surf, tmin_id, tmax_id, \
            lenday_id, traffprof_24hr, ts5mindata_ir, tstep, tstep_prev, veg_type, \
            waterdist, waterusemethod, wuday_id, decidcap_id, albdectr_id, albevetr_id, \
            albgrass_id, porosity_id, wuprofa_24hr, wuprofm_24hr, z, z0m_in, zdm_in)
        
        
        Defined at suews_ctrl_driver.fpp lines 3825-4549
        
        Parameters
        ----------
        metforcingblock : float array
        len_sim : int
        ah_min : float array
        ahprof_24hr : float array
        ah_slope_cooling : float array
        ah_slope_heating : float array
        alb : float array
        albmax_dectr : float
        albmax_evetr : float
        albmax_grass : float
        albmin_dectr : float
        albmin_evetr : float
        albmin_grass : float
        alpha_bioco2 : float array
        alpha_enh_bioco2 : float array
        alt : float
        baset : float array
        basete : float array
        beta_bioco2 : float array
        beta_enh_bioco2 : float array
        bldgh : float
        capmax_dec : float
        capmin_dec : float
        chanohm : float array
        co2pointsource : float
        cpanohm : float array
        crwmax : float
        crwmin : float
        daywat : float array
        daywatper : float array
        dectreeh : float
        diagmethod : int
        diagnose : int
        drainrt : float
        dt_since_start : int
        dqndt : float
        qn_av : float
        dqnsdt : float
        qn_s_av : float
        ef_umolco2perj : float
        emis : float array
        emissionsmethod : int
        enef_v_jkm : float
        enddls : int
        evetreeh : float
        faibldg : float
        faidectree : float
        faievetree : float
        faut : float
        fcef_v_kgkm : float array
        flowchange : float
        frfossilfuel_heat : float
        frfossilfuel_nonheat : float
        g_max : float
        g_k : float
        g_q_base : float
        g_q_shape : float
        g_t : float
        g_sm : float
        gdd_id : float array
        gddfull : float array
        gridiv : int
        gsmodel : int
        h_maintain : float
        hdd_id : float array
        humactivity_24hr : float array
        icefrac : float array
        ie_a : float array
        ie_end : int
        ie_m : float array
        ie_start : int
        internalwateruse_h : float
        irrfracpaved : float
        irrfracbldgs : float
        irrfracevetr : float
        irrfracdectr : float
        irrfracgrass : float
        irrfracbsoil : float
        irrfracwater : float
        kkanohm : float array
        kmax : float
        lai_id : float array
        laimax : float array
        laimin : float array
        laipower : float array
        laitype : int array
        lat : float
        lng : float
        maxconductance : float array
        maxfcmetab : float
        maxqfmetab : float
        snowwater : float array
        minfcmetab : float
        minqfmetab : float
        min_res_bioco2 : float array
        narp_emis_snow : float
        narp_trans_site : float
        netradiationmethod : int
        ohm_coef : float array
        ohmincqf : int
        ohm_threshsw : float array
        ohm_threshwd : float array
        pipecapacity : float
        popdensdaytime : float array
        popdensnighttime : float
        popprof_24hr : float array
        pormax_dec : float
        pormin_dec : float
        preciplimit : float
        preciplimitalb : float
        qf0_beu : float array
        qf_a : float array
        qf_b : float array
        qf_c : float array
        nlayer : int
        n_vegetation_region_urban : int
        n_stream_sw_urban : int
        n_stream_lw_urban : int
        sw_dn_direct_frac : float
        air_ext_sw : float
        air_ssa_sw : float
        veg_ssa_sw : float
        air_ext_lw : float
        air_ssa_lw : float
        veg_ssa_lw : float
        veg_fsd_const : float
        veg_contact_fraction_const : float
        ground_albedo_dir_mult_fact : float
        use_sw_direct_albedo : bool
        height : float array
        building_frac : float array
        veg_frac : float array
        building_scale : float array
        veg_scale : float array
        alb_roof : float array
        emis_roof : float array
        alb_wall : float array
        emis_wall : float array
        roof_albedo_dir_mult_fact : float array
        wall_specular_frac : float array
        radmeltfact : float
        raincover : float
        rainmaxres : float
        resp_a : float array
        resp_b : float array
        roughlenheatmethod : int
        roughlenmommethod : int
        runofftowater : float
        s1 : float
        s2 : float
        sathydraulicconduct : float array
        sddfull : float array
        sdd_id : float array
        smdmethod : int
        snowalb : float
        snowalbmax : float
        snowalbmin : float
        snowpacklimit : float array
        snowdens : float array
        snowdensmax : float
        snowdensmin : float
        snowfallcum : float
        snowfrac : float array
        snowlimbldg : float
        snowlimpaved : float
        snowpack : float array
        snowprof_24hr : float array
        snowuse : int
        soildepth : float array
        stabilitymethod : int
        startdls : int
        soilstore_surf : float array
        soilstorecap_surf : float array
        state_surf : float array
        statelimit_surf : float array
        wetthresh_surf : float array
        soilstore_roof : float array
        soilstorecap_roof : float array
        state_roof : float array
        statelimit_roof : float array
        wetthresh_roof : float array
        soilstore_wall : float array
        soilstorecap_wall : float array
        state_wall : float array
        statelimit_wall : float array
        wetthresh_wall : float array
        storageheatmethod : int
        storedrainprm : float array
        surfacearea : float
        tair_av : float
        tau_a : float
        tau_f : float
        tau_r : float
        baset_cooling : float array
        baset_heating : float array
        tempmeltfact : float
        th : float
        theta_bioco2 : float array
        timezone : float
        tl : float
        trafficrate : float array
        trafficunits : float
        sfr_surf : float array
        tsfc_roof : float array
        tsfc_wall : float array
        tsfc_surf : float array
        temp_roof : float array
        temp_wall : float array
        temp_surf : float array
        tin_roof : float array
        tin_wall : float array
        tin_surf : float array
        k_wall : float array
        k_roof : float array
        k_surf : float array
        cp_wall : float array
        cp_roof : float array
        cp_surf : float array
        dz_wall : float array
        dz_roof : float array
        dz_surf : float array
        tmin_id : float
        tmax_id : float
        lenday_id : float
        traffprof_24hr : float array
        ts5mindata_ir : float array
        tstep : int
        tstep_prev : int
        veg_type : int
        waterdist : float array
        waterusemethod : int
        wuday_id : float array
        decidcap_id : float
        albdectr_id : float
        albevetr_id : float
        albgrass_id : float
        porosity_id : float
        wuprofa_24hr : float array
        wuprofm_24hr : float array
        z : float
        z0m_in : float
        zdm_in : float
        
        Returns
        -------
        output_block_suews : Output_Block
        
        ================================================
         below is for debugging
         WRITE(year_txt, '(I4)') INT(iy)
         WRITE(id_text, '(I3)') INT(id)
         WRITE(it_text, '(I4)') INT(it)
         WRITE(imin_text, '(I4)') INT(imin)
         FileStateInit = './'//TRIM(ADJUSTL(year_txt))//'_'&
         //TRIM(ADJUSTL(id_text))//'_'&
         //TRIM(ADJUSTL(it_text))//'_'&
         //TRIM(ADJUSTL(imin_text))//'_'&
         //'state_init.nml'
         OPEN(12, file=FileStateInit, position='rewind')
         write(12, *) '&state_init'
         write(12, *) 'aerodynamicresistancemethod=', aerodynamicresistancemethod
         write(12, *) 'ah_min=', ah_min
         write(12, *) 'ahprof_24hr=', ahprof_24hr
         write(12, *) 'ah_slope_cooling=', ah_slope_cooling
         write(12, *) 'ah_slope_heating=', ah_slope_heating
         write(12, *) 'alb=', alb
         write(12, *) 'albmax_dectr=', albmax_dectr
         write(12, *) 'albmax_evetr=', albmax_evetr
         write(12, *) 'albmax_grass=', albmax_grass
         write(12, *) 'albmin_dectr=', albmin_dectr
         write(12, *) 'albmin_evetr=', albmin_evetr
         write(12, *) 'albmin_grass=', albmin_grass
         write(12, *) 'alpha_bioco2=', alpha_bioco2
         write(12, *) 'alpha_enh_bioco2=', alpha_enh_bioco2
         write(12, *) 'alt=', alt
         write(12, *) 'avkdn=', avkdn
         write(12, *) 'avrh=', avrh
         write(12, *) 'avu1=', avu1
         write(12, *) 'baset=', baset
         write(12, *) 'basete=', basete
         write(12, *) 'BaseT_HC=', BaseT_HC
         write(12, *) 'beta_bioco2=', beta_bioco2
         write(12, *) 'beta_enh_bioco2=', beta_enh_bioco2
         write(12, *) 'bldgh=', bldgh
         write(12, *) 'capmax_dec=', capmax_dec
         write(12, *) 'capmin_dec=', capmin_dec
         write(12, *) 'chanohm=', chanohm
         write(12, *) 'co2pointsource=', co2pointsource
         write(12, *) 'cpanohm=', cpanohm
         write(12, *) 'crwmax=', crwmax
         write(12, *) 'crwmin=', crwmin
         write(12, *) 'daywat=', daywat
         write(12, *) 'daywatper=', daywatper
         write(12, *) 'dectreeh=', dectreeh
         write(12, *) 'diagnose=', diagnose
         write(12, *) 'diagqn=', diagqn
         write(12, *) 'diagqs=', diagqs
         write(12, *) 'drainrt=', drainrt
         write(12, *) 'dt_since_start=', dt_since_start
         write(12, *) 'dqndt=', dqndt
         write(12, *) 'qn_av=', qn_av
         write(12, *) 'dqnsdt=', dqnsdt
         write(12, *) 'qn1_s_av=', qn1_s_av
         write(12, *) 'ef_umolco2perj=', ef_umolco2perj
         write(12, *) 'emis=', emis
         write(12, *) 'emissionsmethod=', emissionsmethod
         write(12, *) 'enef_v_jkm=', enef_v_jkm
         write(12, *) 'enddls=', enddls
         write(12, *) 'evetreeh=', evetreeh
         write(12, *) 'faibldg=', faibldg
         write(12, *) 'faidectree=', faidectree
         write(12, *) 'faievetree=', faievetree
         write(12, *) 'faut=', faut
         write(12, *) 'fcef_v_kgkm=', fcef_v_kgkm
         write(12, *) 'fcld_obs=', fcld_obs
         write(12, *) 'flowchange=', flowchange
         write(12, *) 'frfossilfuel_heat=', frfossilfuel_heat
         write(12, *) 'frfossilfuel_nonheat=', frfossilfuel_nonheat
         write(12, *) 'g1=', g1
         write(12, *) 'g2=', g2
         write(12, *) 'g3=', g3
         write(12, *) 'g4=', g4
         write(12, *) 'g5=', g5
         write(12, *) 'g6=', g6
         write(12, *) 'gdd_id=', gdd_id
         write(12, *) 'gddfull=', gddfull
         write(12, *) 'gridiv=', gridiv
         write(12, *) 'gsmodel=', gsmodel
         write(12, *) 'hdd_id=', hdd_id
         write(12, *) 'humactivity_24hr=', humactivity_24hr
         write(12, *) 'icefrac=', icefrac
         write(12, *) 'id=', id
         write(12, *) 'ie_a=', ie_a
         write(12, *) 'ie_end=', ie_end
         write(12, *) 'ie_m=', ie_m
         write(12, *) 'ie_start=', ie_start
         write(12, *) 'imin=', imin
         write(12, *) 'internalwateruse_h=', internalwateruse_h
         write(12, *) 'IrrFracEveTr=', IrrFracEveTr
         write(12, *) 'IrrFracDecTr=', IrrFracDecTr
         write(12, *) 'irrfracgrass=', irrfracgrass
         write(12, *) 'isec=', isec
         write(12, *) 'it=', it
         write(12, *) 'evapmethod=', evapmethod
         write(12, *) 'iy=', iy
         write(12, *) 'kkanohm=', kkanohm
         write(12, *) 'kmax=', kmax
         write(12, *) 'lai_id=', lai_id
         write(12, *) 'laicalcyes=', laicalcyes
         write(12, *) 'laimax=', laimax
         write(12, *) 'laimin=', laimin
         write(12, *) 'lai_obs=', lai_obs
         write(12, *) 'laipower=', laipower
         write(12, *) 'laitype=', laitype
         write(12, *) 'lat=', lat
         write(12, *) 'lenday_id=', lenday_id
         write(12, *) 'ldown_obs=', ldown_obs
         write(12, *) 'lng=', lng
         write(12, *) 'maxconductance=', maxconductance
         write(12, *) 'maxfcmetab=', maxfcmetab
         write(12, *) 'maxqfmetab=', maxqfmetab
         write(12, *) 'snowwater=', snowwater
         write(12, *) 'metforcingdata_grid=', metforcingdata_grid
         write(12, *) 'minfcmetab=', minfcmetab
         write(12, *) 'minqfmetab=', minqfmetab
         write(12, *) 'min_res_bioco2=', min_res_bioco2
         write(12, *) 'narp_emis_snow=', narp_emis_snow
         write(12, *) 'narp_trans_site=', narp_trans_site
         write(12, *) 'netradiationmethod=', netradiationmethod
         write(12, *) 'ohm_coef=', ohm_coef
         write(12, *) 'ohmincqf=', ohmincqf
         write(12, *) 'ohm_threshsw=', ohm_threshsw
         write(12, *) 'ohm_threshwd=', ohm_threshwd
         write(12, *) 'pipecapacity=', pipecapacity
         write(12, *) 'popdensdaytime=', popdensdaytime
         write(12, *) 'popdensnighttime=', popdensnighttime
         write(12, *) 'popprof_24hr=', popprof_24hr
         write(12, *) 'pormax_dec=', pormax_dec
         write(12, *) 'pormin_dec=', pormin_dec
         write(12, *) 'precip=', precip
         write(12, *) 'preciplimit=', preciplimit
         write(12, *) 'preciplimitalb=', preciplimitalb
         write(12, *) 'press_hpa=', press_hpa
         write(12, *) 'qf0_beu=', qf0_beu
         write(12, *) 'qf_a=', qf_a
         write(12, *) 'qf_b=', qf_b
         write(12, *) 'qf_c=', qf_c
         write(12, *) 'qn1_obs=', qn1_obs
         write(12, *) 'qh_obs=', qh_obs
         write(12, *) 'qs_obs=', qs_obs
         write(12, *) 'qf_obs=', qf_obs
         write(12, *) 'radmeltfact=', radmeltfact
         write(12, *) 'raincover=', raincover
         write(12, *) 'rainmaxres=', rainmaxres
         write(12, *) 'resp_a=', resp_a
         write(12, *) 'resp_b=', resp_b
         write(12, *) 'roughlenheatmethod=', roughlenheatmethod
         write(12, *) 'roughlenmommethod=', roughlenmommethod
         write(12, *) 'runofftowater=', runofftowater
         write(12, *) 's1=', s1
         write(12, *) 's2=', s2
         write(12, *) 'sathydraulicconduct=', sathydraulicconduct
         write(12, *) 'sddfull=', sddfull
         write(12, *) 'sdd_id=', sdd_id
         write(12, *) 'sfr_surf=', sfr_surf
         write(12, *) 'smdmethod=', smdmethod
         write(12, *) 'snowalb=', snowalb
         write(12, *) 'snowalbmax=', snowalbmax
         write(12, *) 'snowalbmin=', snowalbmin
         write(12, *) 'snowpacklimit=', snowpacklimit
         write(12, *) 'snowdens=', snowdens
         write(12, *) 'snowdensmax=', snowdensmax
         write(12, *) 'snowdensmin=', snowdensmin
         write(12, *) 'snowfallcum=', snowfallcum
         write(12, *) 'snowfrac=', snowfrac
         write(12, *) 'snowlimbldg=', snowlimbldg
         write(12, *) 'snowlimpaved=', snowlimpaved
         write(12, *) 'snowfrac_obs=', snowfrac_obs
         write(12, *) 'snowpack=', snowpack
         write(12, *) 'snowprof_24hr=', snowprof_24hr
         write(12, *) 'SnowUse=', SnowUse
         write(12, *) 'soildepth=', soildepth
         write(12, *) 'soilstore_id=', soilstore_id
         write(12, *) 'soilstorecap=', soilstorecap
         write(12, *) 'stabilitymethod=', stabilitymethod
         write(12, *) 'startdls=', startdls
         write(12, *) 'state_id=', state_id
         write(12, *) 'statelimit=', statelimit
         write(12, *) 'storageheatmethod=', storageheatmethod
         write(12, *) 'storedrainprm=', storedrainprm
         write(12, *) 'surfacearea=', surfacearea
         write(12, *) 'tair_av=', tair_av
         write(12, *) 'tau_a=', tau_a
         write(12, *) 'tau_f=', tau_f
         write(12, *) 'tau_r=', tau_r
         write(12, *) 'tmax_id=', tmax_id
         write(12, *) 'tmin_id=', tmin_id
         write(12, *) 'BaseT_Cooling=', BaseT_Cooling
         write(12, *) 'BaseT_Heating=', BaseT_Heating
         write(12, *) 'temp_c=', temp_c
         write(12, *) 'tempmeltfact=', tempmeltfact
         write(12, *) 'th=', th
         write(12, *) 'theta_bioco2=', theta_bioco2
         write(12, *) 'timezone=', timezone
         write(12, *) 'tl=', tl
         write(12, *) 'trafficrate=', trafficrate
         write(12, *) 'trafficunits=', trafficunits
         write(12, *) 'traffprof_24hr=', traffprof_24hr
         write(12, *) 'ts5mindata_ir=', ts5mindata_ir
         write(12, *) 'tstep=', tstep
         write(12, *) 'tstep_prev=', tstep_prev
         write(12, *) 'veg_type=', veg_type
         write(12, *) 'waterdist=', waterdist
         write(12, *) 'waterusemethod=', waterusemethod
         write(12, *) 'wetthresh=', wetthresh
         write(12, *) 'wu_m3=', wu_m3
         write(12, *) 'wuday_id=', wuday_id
         write(12, *) 'decidcap_id=', decidcap_id
         write(12, *) 'albdectr_id=', albdectr_id
         write(12, *) 'albevetr_id=', albevetr_id
         write(12, *) 'albgrass_id=', albgrass_id
         write(12, *) 'porosity_id=', porosity_id
         write(12, *) 'wuprofa_24hr=', wuprofa_24hr
         write(12, *) 'wuprofm_24hr=', wuprofm_24hr
         write(12, *) 'xsmd=', xsmd
         write(12, *) 'z=', z
         write(12, *) 'z0m_in=', z0m_in
         write(12, *) 'zdm_in=', zdm_in
         write(12, *) '/'
         WRITE(12, *) ''
         CLOSE(12)
        ================================================
        """
        output_block_suews = \
            _supy_driver.f90wrap_suews_cal_multitsteps(metforcingblock=metforcingblock, \
            len_sim=len_sim, ah_min=ah_min, ahprof_24hr=ahprof_24hr, \
            ah_slope_cooling=ah_slope_cooling, ah_slope_heating=ah_slope_heating, \
            alb=alb, albmax_dectr=albmax_dectr, albmax_evetr=albmax_evetr, \
            albmax_grass=albmax_grass, albmin_dectr=albmin_dectr, \
            albmin_evetr=albmin_evetr, albmin_grass=albmin_grass, \
            alpha_bioco2=alpha_bioco2, alpha_enh_bioco2=alpha_enh_bioco2, alt=alt, \
            baset=baset, basete=basete, beta_bioco2=beta_bioco2, \
            beta_enh_bioco2=beta_enh_bioco2, bldgh=bldgh, capmax_dec=capmax_dec, \
            capmin_dec=capmin_dec, chanohm=chanohm, co2pointsource=co2pointsource, \
            cpanohm=cpanohm, crwmax=crwmax, crwmin=crwmin, daywat=daywat, \
            daywatper=daywatper, dectreeh=dectreeh, diagmethod=diagmethod, \
            diagnose=diagnose, drainrt=drainrt, dt_since_start=dt_since_start, \
            dqndt=dqndt, qn_av=qn_av, dqnsdt=dqnsdt, qn_s_av=qn_s_av, \
            ef_umolco2perj=ef_umolco2perj, emis=emis, emissionsmethod=emissionsmethod, \
            enef_v_jkm=enef_v_jkm, enddls=enddls, evetreeh=evetreeh, faibldg=faibldg, \
            faidectree=faidectree, faievetree=faievetree, faut=faut, \
            fcef_v_kgkm=fcef_v_kgkm, flowchange=flowchange, \
            frfossilfuel_heat=frfossilfuel_heat, \
            frfossilfuel_nonheat=frfossilfuel_nonheat, g_max=g_max, g_k=g_k, \
            g_q_base=g_q_base, g_q_shape=g_q_shape, g_t=g_t, g_sm=g_sm, gdd_id=gdd_id, \
            gddfull=gddfull, gridiv=gridiv, gsmodel=gsmodel, h_maintain=h_maintain, \
            hdd_id=hdd_id, humactivity_24hr=humactivity_24hr, icefrac=icefrac, \
            ie_a=ie_a, ie_end=ie_end, ie_m=ie_m, ie_start=ie_start, \
            internalwateruse_h=internalwateruse_h, irrfracpaved=irrfracpaved, \
            irrfracbldgs=irrfracbldgs, irrfracevetr=irrfracevetr, \
            irrfracdectr=irrfracdectr, irrfracgrass=irrfracgrass, \
            irrfracbsoil=irrfracbsoil, irrfracwater=irrfracwater, kkanohm=kkanohm, \
            kmax=kmax, lai_id=lai_id, laimax=laimax, laimin=laimin, laipower=laipower, \
            laitype=laitype, lat=lat, lng=lng, maxconductance=maxconductance, \
            maxfcmetab=maxfcmetab, maxqfmetab=maxqfmetab, snowwater=snowwater, \
            minfcmetab=minfcmetab, minqfmetab=minqfmetab, min_res_bioco2=min_res_bioco2, \
            narp_emis_snow=narp_emis_snow, narp_trans_site=narp_trans_site, \
            netradiationmethod=netradiationmethod, ohm_coef=ohm_coef, ohmincqf=ohmincqf, \
            ohm_threshsw=ohm_threshsw, ohm_threshwd=ohm_threshwd, \
            pipecapacity=pipecapacity, popdensdaytime=popdensdaytime, \
            popdensnighttime=popdensnighttime, popprof_24hr=popprof_24hr, \
            pormax_dec=pormax_dec, pormin_dec=pormin_dec, preciplimit=preciplimit, \
            preciplimitalb=preciplimitalb, qf0_beu=qf0_beu, qf_a=qf_a, qf_b=qf_b, \
            qf_c=qf_c, nlayer=nlayer, \
            n_vegetation_region_urban=n_vegetation_region_urban, \
            n_stream_sw_urban=n_stream_sw_urban, n_stream_lw_urban=n_stream_lw_urban, \
            sw_dn_direct_frac=sw_dn_direct_frac, air_ext_sw=air_ext_sw, \
            air_ssa_sw=air_ssa_sw, veg_ssa_sw=veg_ssa_sw, air_ext_lw=air_ext_lw, \
            air_ssa_lw=air_ssa_lw, veg_ssa_lw=veg_ssa_lw, veg_fsd_const=veg_fsd_const, \
            veg_contact_fraction_const=veg_contact_fraction_const, \
            ground_albedo_dir_mult_fact=ground_albedo_dir_mult_fact, \
            use_sw_direct_albedo=use_sw_direct_albedo, height=height, \
            building_frac=building_frac, veg_frac=veg_frac, \
            building_scale=building_scale, veg_scale=veg_scale, alb_roof=alb_roof, \
            emis_roof=emis_roof, alb_wall=alb_wall, emis_wall=emis_wall, \
            roof_albedo_dir_mult_fact=roof_albedo_dir_mult_fact, \
            wall_specular_frac=wall_specular_frac, radmeltfact=radmeltfact, \
            raincover=raincover, rainmaxres=rainmaxres, resp_a=resp_a, resp_b=resp_b, \
            roughlenheatmethod=roughlenheatmethod, roughlenmommethod=roughlenmommethod, \
            runofftowater=runofftowater, s1=s1, s2=s2, \
            sathydraulicconduct=sathydraulicconduct, sddfull=sddfull, sdd_id=sdd_id, \
            smdmethod=smdmethod, snowalb=snowalb, snowalbmax=snowalbmax, \
            snowalbmin=snowalbmin, snowpacklimit=snowpacklimit, snowdens=snowdens, \
            snowdensmax=snowdensmax, snowdensmin=snowdensmin, snowfallcum=snowfallcum, \
            snowfrac=snowfrac, snowlimbldg=snowlimbldg, snowlimpaved=snowlimpaved, \
            snowpack=snowpack, snowprof_24hr=snowprof_24hr, snowuse=snowuse, \
            soildepth=soildepth, stabilitymethod=stabilitymethod, startdls=startdls, \
            soilstore_surf=soilstore_surf, soilstorecap_surf=soilstorecap_surf, \
            state_surf=state_surf, statelimit_surf=statelimit_surf, \
            wetthresh_surf=wetthresh_surf, soilstore_roof=soilstore_roof, \
            soilstorecap_roof=soilstorecap_roof, state_roof=state_roof, \
            statelimit_roof=statelimit_roof, wetthresh_roof=wetthresh_roof, \
            soilstore_wall=soilstore_wall, soilstorecap_wall=soilstorecap_wall, \
            state_wall=state_wall, statelimit_wall=statelimit_wall, \
            wetthresh_wall=wetthresh_wall, storageheatmethod=storageheatmethod, \
            storedrainprm=storedrainprm, surfacearea=surfacearea, tair_av=tair_av, \
            tau_a=tau_a, tau_f=tau_f, tau_r=tau_r, baset_cooling=baset_cooling, \
            baset_heating=baset_heating, tempmeltfact=tempmeltfact, th=th, \
            theta_bioco2=theta_bioco2, timezone=timezone, tl=tl, \
            trafficrate=trafficrate, trafficunits=trafficunits, sfr_surf=sfr_surf, \
            tsfc_roof=tsfc_roof, tsfc_wall=tsfc_wall, tsfc_surf=tsfc_surf, \
            temp_roof=temp_roof, temp_wall=temp_wall, temp_surf=temp_surf, \
            tin_roof=tin_roof, tin_wall=tin_wall, tin_surf=tin_surf, k_wall=k_wall, \
            k_roof=k_roof, k_surf=k_surf, cp_wall=cp_wall, cp_roof=cp_roof, \
            cp_surf=cp_surf, dz_wall=dz_wall, dz_roof=dz_roof, dz_surf=dz_surf, \
            tmin_id=tmin_id, tmax_id=tmax_id, lenday_id=lenday_id, \
            traffprof_24hr=traffprof_24hr, ts5mindata_ir=ts5mindata_ir, tstep=tstep, \
            tstep_prev=tstep_prev, veg_type=veg_type, waterdist=waterdist, \
            waterusemethod=waterusemethod, wuday_id=wuday_id, decidcap_id=decidcap_id, \
            albdectr_id=albdectr_id, albevetr_id=albevetr_id, albgrass_id=albgrass_id, \
            porosity_id=porosity_id, wuprofa_24hr=wuprofa_24hr, \
            wuprofm_24hr=wuprofm_24hr, z=z, z0m_in=z0m_in, zdm_in=zdm_in)
        output_block_suews = \
            f90wrap.runtime.lookup_class("supy_driver.output_block").from_handle(output_block_suews, \
            alloc=True)
        return output_block_suews
    
    @staticmethod
    def suews_cal_sunposition(year, idectime, utc, locationlatitude, \
        locationlongitude, locationaltitude):
        """
        sunazimuth, sunzenith = suews_cal_sunposition(year, idectime, utc, \
            locationlatitude, locationlongitude, locationaltitude)
        
        
        Defined at suews_ctrl_driver.fpp lines 4554-4561
        
        Parameters
        ----------
        year : float
        idectime : float
        utc : float
        locationlatitude : float
        locationlongitude : float
        locationaltitude : float
        
        Returns
        -------
        sunazimuth : float
        sunzenith : float
        
        """
        sunazimuth, sunzenith = _supy_driver.f90wrap_suews_cal_sunposition(year=year, \
            idectime=idectime, utc=utc, locationlatitude=locationlatitude, \
            locationlongitude=locationlongitude, locationaltitude=locationaltitude)
        return sunazimuth, sunzenith
    
    @staticmethod
    def cal_tair_av(tair_av_prev, dt_since_start, tstep, temp_c):
        """
        tair_av_next = cal_tair_av(tair_av_prev, dt_since_start, tstep, temp_c)
        
        
        Defined at suews_ctrl_driver.fpp lines 4568-4589
        
        Parameters
        ----------
        tair_av_prev : float
        dt_since_start : int
        tstep : int
        temp_c : float
        
        Returns
        -------
        tair_av_next : float
        
        """
        tair_av_next = _supy_driver.f90wrap_cal_tair_av(tair_av_prev=tair_av_prev, \
            dt_since_start=dt_since_start, tstep=tstep, temp_c=temp_c)
        return tair_av_next
    
    @staticmethod
    def cal_tsfc(qh, avdens, avcp, ra, temp_c):
        """
        tsfc_c = cal_tsfc(qh, avdens, avcp, ra, temp_c)
        
        
        Defined at suews_ctrl_driver.fpp lines 4591-4601
        
        Parameters
        ----------
        qh : float
        avdens : float
        avcp : float
        ra : float
        temp_c : float
        
        Returns
        -------
        tsfc_c : float
        
        """
        tsfc_c = _supy_driver.f90wrap_cal_tsfc(qh=qh, avdens=avdens, avcp=avcp, ra=ra, \
            temp_c=temp_c)
        return tsfc_c
    
    _dt_array_initialisers = []
    

suews_driver = Suews_Driver()

class Narp_Module(f90wrap.runtime.FortranModule):
    """
    Module narp_module
    
    
    Defined at suews_phys_narp.fpp lines 5-1269
    
    """
    @staticmethod
    def radmethod(netradiationmethod, snowuse):
        """
        netradiationmethod_use, albedochoice, ldown_option = \
            radmethod(netradiationmethod, snowuse)
        
        
        Defined at suews_phys_narp.fpp lines 47-109
        
        Parameters
        ----------
        netradiationmethod : int
        snowuse : int
        
        Returns
        -------
        netradiationmethod_use : int
        albedochoice : int
        ldown_option : int
        
        """
        netradiationmethod_use, albedochoice, ldown_option = \
            _supy_driver.f90wrap_radmethod(netradiationmethod=netradiationmethod, \
            snowuse=snowuse)
        return netradiationmethod_use, albedochoice, ldown_option
    
    @staticmethod
    def narp(storageheatmethod, nsurf, sfr_surf, tsfc_surf, snowfrac, alb, emis, \
        icefrac, narp_trans_site, narp_emis_snow, dtime, zenith_deg, tsurf_0, kdown, \
        temp_c, rh, press_hpa, qn1_obs, ldown_obs, snowalb, albedochoice, \
        ldown_option, netradiationmethod_use, diagqn, qn_surf, qn1_ind_snow, \
        kup_ind_snow, tsurf_ind_snow, tsurf_surf):
        """
        qstarall, qstar_sf, qstar_s, kclear, kupall, ldown, lupall, fcld, tsurfall, \
            albedo_snowfree, albedo_snow = narp(storageheatmethod, nsurf, sfr_surf, \
            tsfc_surf, snowfrac, alb, emis, icefrac, narp_trans_site, narp_emis_snow, \
            dtime, zenith_deg, tsurf_0, kdown, temp_c, rh, press_hpa, qn1_obs, \
            ldown_obs, snowalb, albedochoice, ldown_option, netradiationmethod_use, \
            diagqn, qn_surf, qn1_ind_snow, kup_ind_snow, tsurf_ind_snow, tsurf_surf)
        
        
        Defined at suews_phys_narp.fpp lines 123-459
        
        Parameters
        ----------
        storageheatmethod : int
        nsurf : int
        sfr_surf : float array
        tsfc_surf : float array
        snowfrac : float array
        alb : float array
        emis : float array
        icefrac : float array
        narp_trans_site : float
        narp_emis_snow : float
        dtime : float
        zenith_deg : float
        tsurf_0 : float
        kdown : float
        temp_c : float
        rh : float
        press_hpa : float
        qn1_obs : float
        ldown_obs : float
        snowalb : float
        albedochoice : int
        ldown_option : int
        netradiationmethod_use : int
        diagqn : int
        qn_surf : float array
        qn1_ind_snow : float array
        kup_ind_snow : float array
        tsurf_ind_snow : float array
        tsurf_surf : float array
        
        Returns
        -------
        qstarall : float
        qstar_sf : float
        qstar_s : float
        kclear : float
        kupall : float
        ldown : float
        lupall : float
        fcld : float
        tsurfall : float
        albedo_snowfree : float
        albedo_snow : float
        
        -------------------------------------------------------------------------------
         USE allocateArray
         use gis_data
         use data_in
         Included 20140701, FL
         use moist
         Included 20140701, FL
         use time
         Included 20140701, FL
        """
        qstarall, qstar_sf, qstar_s, kclear, kupall, ldown, lupall, fcld, tsurfall, \
            albedo_snowfree, albedo_snow = \
            _supy_driver.f90wrap_narp(storageheatmethod=storageheatmethod, nsurf=nsurf, \
            sfr_surf=sfr_surf, tsfc_surf=tsfc_surf, snowfrac=snowfrac, alb=alb, \
            emis=emis, icefrac=icefrac, narp_trans_site=narp_trans_site, \
            narp_emis_snow=narp_emis_snow, dtime=dtime, zenith_deg=zenith_deg, \
            tsurf_0=tsurf_0, kdown=kdown, temp_c=temp_c, rh=rh, press_hpa=press_hpa, \
            qn1_obs=qn1_obs, ldown_obs=ldown_obs, snowalb=snowalb, \
            albedochoice=albedochoice, ldown_option=ldown_option, \
            netradiationmethod_use=netradiationmethod_use, diagqn=diagqn, \
            qn_surf=qn_surf, qn1_ind_snow=qn1_ind_snow, kup_ind_snow=kup_ind_snow, \
            tsurf_ind_snow=tsurf_ind_snow, tsurf_surf=tsurf_surf)
        return qstarall, qstar_sf, qstar_s, kclear, kupall, ldown, lupall, fcld, \
            tsurfall, albedo_snowfree, albedo_snow
    
    @staticmethod
    def narp_cal_sunposition(year, idectime, utc, locationlatitude, \
        locationlongitude, locationaltitude):
        """
        sunazimuth, sunzenith = narp_cal_sunposition(year, idectime, utc, \
            locationlatitude, locationlongitude, locationaltitude)
        
        
        Defined at suews_phys_narp.fpp lines 464-547
        
        Parameters
        ----------
        year : float
        idectime : float
        utc : float
        locationlatitude : float
        locationlongitude : float
        locationaltitude : float
        
        Returns
        -------
        sunazimuth : float
        sunzenith : float
        
        """
        sunazimuth, sunzenith = _supy_driver.f90wrap_narp_cal_sunposition(year=year, \
            idectime=idectime, utc=utc, locationlatitude=locationlatitude, \
            locationlongitude=locationlongitude, locationaltitude=locationaltitude)
        return sunazimuth, sunzenith
    
    @staticmethod
    def julian_calculation(year, month, day, hour, min_bn, sec, utc, juliancentury, \
        julianday, julianephemeris_century, julianephemeris_day, \
        julianephemeris_millenium):
        """
        julian_calculation(year, month, day, hour, min_bn, sec, utc, juliancentury, \
            julianday, julianephemeris_century, julianephemeris_day, \
            julianephemeris_millenium)
        
        
        Defined at suews_phys_narp.fpp lines 551-608
        
        Parameters
        ----------
        year : float
        month : int
        day : int
        hour : int
        min_bn : int
        sec : float
        utc : float
        juliancentury : float
        julianday : float
        julianephemeris_century : float
        julianephemeris_day : float
        julianephemeris_millenium : float
        
        """
        _supy_driver.f90wrap_julian_calculation(year=year, month=month, day=day, \
            hour=hour, min_bn=min_bn, sec=sec, utc=utc, juliancentury=juliancentury, \
            julianday=julianday, julianephemeris_century=julianephemeris_century, \
            julianephemeris_day=julianephemeris_day, \
            julianephemeris_millenium=julianephemeris_millenium)
    
    @staticmethod
    def earth_heliocentric_position_calculation(julianephemeris_millenium, \
        earth_heliocentric_positionlatitude, earth_heliocentric_positionlongitude, \
        earth_heliocentric_positionradius):
        """
        earth_heliocentric_position_calculation(julianephemeris_millenium, \
            earth_heliocentric_positionlatitude, earth_heliocentric_positionlongitude, \
            earth_heliocentric_positionradius)
        
        
        Defined at suews_phys_narp.fpp lines 610-776
        
        Parameters
        ----------
        julianephemeris_millenium : float
        earth_heliocentric_positionlatitude : float
        earth_heliocentric_positionlongitude : float
        earth_heliocentric_positionradius : float
        
        """
        _supy_driver.f90wrap_earth_heliocentric_position_calculation(julianephemeris_millenium=julianephemeris_millenium, \
            earth_heliocentric_positionlatitude=earth_heliocentric_positionlatitude, \
            earth_heliocentric_positionlongitude=earth_heliocentric_positionlongitude, \
            earth_heliocentric_positionradius=earth_heliocentric_positionradius)
    
    @staticmethod
    def sun_geocentric_position_calculation(earth_heliocentric_positionlongitude, \
        earth_heliocentric_positionlatitude, sun_geocentric_positionlatitude, \
        sun_geocentric_positionlongitude):
        """
        sun_geocentric_position_calculation(earth_heliocentric_positionlongitude, \
            earth_heliocentric_positionlatitude, sun_geocentric_positionlatitude, \
            sun_geocentric_positionlongitude)
        
        
        Defined at suews_phys_narp.fpp lines 778-790
        
        Parameters
        ----------
        earth_heliocentric_positionlongitude : float
        earth_heliocentric_positionlatitude : float
        sun_geocentric_positionlatitude : float
        sun_geocentric_positionlongitude : float
        
        """
        _supy_driver.f90wrap_sun_geocentric_position_calculation(earth_heliocentric_positionlongitude=earth_heliocentric_positionlongitude, \
            earth_heliocentric_positionlatitude=earth_heliocentric_positionlatitude, \
            sun_geocentric_positionlatitude=sun_geocentric_positionlatitude, \
            sun_geocentric_positionlongitude=sun_geocentric_positionlongitude)
    
    @staticmethod
    def nutation_calculation(julianephemeris_century, nutationlongitude, \
        nutationobliquity):
        """
        nutation_calculation(julianephemeris_century, nutationlongitude, \
            nutationobliquity)
        
        
        Defined at suews_phys_narp.fpp lines 792-896
        
        Parameters
        ----------
        julianephemeris_century : float
        nutationlongitude : float
        nutationobliquity : float
        
        """
        _supy_driver.f90wrap_nutation_calculation(julianephemeris_century=julianephemeris_century, \
            nutationlongitude=nutationlongitude, nutationobliquity=nutationobliquity)
    
    @staticmethod
    def corr_obliquity_calculation(julianephemeris_millenium, nutationobliquity):
        """
        corr_obliquity = corr_obliquity_calculation(julianephemeris_millenium, \
            nutationobliquity)
        
        
        Defined at suews_phys_narp.fpp lines 898-913
        
        Parameters
        ----------
        julianephemeris_millenium : float
        nutationobliquity : float
        
        Returns
        -------
        corr_obliquity : float
        
        """
        corr_obliquity = \
            _supy_driver.f90wrap_corr_obliquity_calculation(julianephemeris_millenium=julianephemeris_millenium, \
            nutationobliquity=nutationobliquity)
        return corr_obliquity
    
    @staticmethod
    def abberation_correction_calculation(earth_heliocentric_positionradius):
        """
        aberration_correction = \
            abberation_correction_calculation(earth_heliocentric_positionradius)
        
        
        Defined at suews_phys_narp.fpp lines 915-922
        
        Parameters
        ----------
        earth_heliocentric_positionradius : float
        
        Returns
        -------
        aberration_correction : float
        
        """
        aberration_correction = \
            _supy_driver.f90wrap_abberation_correction_calculation(earth_heliocentric_positionradius=earth_heliocentric_positionradius)
        return aberration_correction
    
    @staticmethod
    def apparent_sun_longitude_calculation(sun_geocentric_positionlongitude, \
        nutationlongitude, aberration_correction):
        """
        apparent_sun_longitude = \
            apparent_sun_longitude_calculation(sun_geocentric_positionlongitude, \
            nutationlongitude, aberration_correction)
        
        
        Defined at suews_phys_narp.fpp lines 924-932
        
        Parameters
        ----------
        sun_geocentric_positionlongitude : float
        nutationlongitude : float
        aberration_correction : float
        
        Returns
        -------
        apparent_sun_longitude : float
        
        """
        apparent_sun_longitude = \
            _supy_driver.f90wrap_apparent_sun_longitude_calculation(sun_geocentric_positionlongitude=sun_geocentric_positionlongitude, \
            nutationlongitude=nutationlongitude, \
            aberration_correction=aberration_correction)
        return apparent_sun_longitude
    
    @staticmethod
    def apparent_stime_at_greenwich_calculation(julianday, juliancentury, \
        nutationlongitude, corr_obliquity):
        """
        apparent_stime_at_greenwich = apparent_stime_at_greenwich_calculation(julianday, \
            juliancentury, nutationlongitude, corr_obliquity)
        
        
        Defined at suews_phys_narp.fpp lines 934-953
        
        Parameters
        ----------
        julianday : float
        juliancentury : float
        nutationlongitude : float
        corr_obliquity : float
        
        Returns
        -------
        apparent_stime_at_greenwich : float
        
        """
        apparent_stime_at_greenwich = \
            _supy_driver.f90wrap_apparent_stime_at_greenwich_calculation(julianday=julianday, \
            juliancentury=juliancentury, nutationlongitude=nutationlongitude, \
            corr_obliquity=corr_obliquity)
        return apparent_stime_at_greenwich
    
    @staticmethod
    def sun_rigth_ascension_calculation(apparent_sun_longitude, corr_obliquity, \
        sun_geocentric_positionlatitude):
        """
        sun_rigth_ascension = sun_rigth_ascension_calculation(apparent_sun_longitude, \
            corr_obliquity, sun_geocentric_positionlatitude)
        
        
        Defined at suews_phys_narp.fpp lines 955-971
        
        Parameters
        ----------
        apparent_sun_longitude : float
        corr_obliquity : float
        sun_geocentric_positionlatitude : float
        
        Returns
        -------
        sun_rigth_ascension : float
        
        """
        sun_rigth_ascension = \
            _supy_driver.f90wrap_sun_rigth_ascension_calculation(apparent_sun_longitude=apparent_sun_longitude, \
            corr_obliquity=corr_obliquity, \
            sun_geocentric_positionlatitude=sun_geocentric_positionlatitude)
        return sun_rigth_ascension
    
    @staticmethod
    def sun_geocentric_declination_calculation(apparent_sun_longitude, \
        corr_obliquity, sun_geocentric_positionlatitude):
        """
        sun_geocentric_declination = \
            sun_geocentric_declination_calculation(apparent_sun_longitude, \
            corr_obliquity, sun_geocentric_positionlatitude)
        
        
        Defined at suews_phys_narp.fpp lines 973-984
        
        Parameters
        ----------
        apparent_sun_longitude : float
        corr_obliquity : float
        sun_geocentric_positionlatitude : float
        
        Returns
        -------
        sun_geocentric_declination : float
        
        """
        sun_geocentric_declination = \
            _supy_driver.f90wrap_sun_geocentric_declination_calculation(apparent_sun_longitude=apparent_sun_longitude, \
            corr_obliquity=corr_obliquity, \
            sun_geocentric_positionlatitude=sun_geocentric_positionlatitude)
        return sun_geocentric_declination
    
    @staticmethod
    def observer_local_hour_calculation(apparent_stime_at_greenwich, \
        locationlongitude, sun_rigth_ascension):
        """
        observer_local_hour = \
            observer_local_hour_calculation(apparent_stime_at_greenwich, \
            locationlongitude, sun_rigth_ascension)
        
        
        Defined at suews_phys_narp.fpp lines 986-997
        
        Parameters
        ----------
        apparent_stime_at_greenwich : float
        locationlongitude : float
        sun_rigth_ascension : float
        
        Returns
        -------
        observer_local_hour : float
        
        """
        observer_local_hour = \
            _supy_driver.f90wrap_observer_local_hour_calculation(apparent_stime_at_greenwich=apparent_stime_at_greenwich, \
            locationlongitude=locationlongitude, \
            sun_rigth_ascension=sun_rigth_ascension)
        return observer_local_hour
    
    @staticmethod
    def topocentric_sun_position_calculate(topocentric_sun_positionrigth_ascension, \
        topocentric_sun_positionrigth_ascension_parallax, \
        topocentric_sun_positiondeclination, locationaltitude, locationlatitude, \
        observer_local_hour, sun_rigth_ascension, sun_geocentric_declination, \
        earth_heliocentric_positionradius):
        """
        topocentric_sun_position_calculate(topocentric_sun_positionrigth_ascension, \
            topocentric_sun_positionrigth_ascension_parallax, \
            topocentric_sun_positiondeclination, locationaltitude, locationlatitude, \
            observer_local_hour, sun_rigth_ascension, sun_geocentric_declination, \
            earth_heliocentric_positionradius)
        
        
        Defined at suews_phys_narp.fpp lines 999-1044
        
        Parameters
        ----------
        topocentric_sun_positionrigth_ascension : float
        topocentric_sun_positionrigth_ascension_parallax : float
        topocentric_sun_positiondeclination : float
        locationaltitude : float
        locationlatitude : float
        observer_local_hour : float
        sun_rigth_ascension : float
        sun_geocentric_declination : float
        earth_heliocentric_positionradius : float
        
        """
        _supy_driver.f90wrap_topocentric_sun_position_calculate(topocentric_sun_positionrigth_ascension=topocentric_sun_positionrigth_ascension, \
            topocentric_sun_positionrigth_ascension_parallax=topocentric_sun_positionrigth_ascension_parallax, \
            topocentric_sun_positiondeclination=topocentric_sun_positiondeclination, \
            locationaltitude=locationaltitude, locationlatitude=locationlatitude, \
            observer_local_hour=observer_local_hour, \
            sun_rigth_ascension=sun_rigth_ascension, \
            sun_geocentric_declination=sun_geocentric_declination, \
            earth_heliocentric_positionradius=earth_heliocentric_positionradius)
    
    @staticmethod
    def topocentric_local_hour_calculate(observer_local_hour, \
        topocentric_sun_positionrigth_ascension_parallax):
        """
        topocentric_local_hour = topocentric_local_hour_calculate(observer_local_hour, \
            topocentric_sun_positionrigth_ascension_parallax)
        
        
        Defined at suews_phys_narp.fpp lines 1046-1053
        
        Parameters
        ----------
        observer_local_hour : float
        topocentric_sun_positionrigth_ascension_parallax : float
        
        Returns
        -------
        topocentric_local_hour : float
        
        """
        topocentric_local_hour = \
            _supy_driver.f90wrap_topocentric_local_hour_calculate(observer_local_hour=observer_local_hour, \
            topocentric_sun_positionrigth_ascension_parallax=topocentric_sun_positionrigth_ascension_parallax)
        return topocentric_local_hour
    
    @staticmethod
    def sun_topocentric_zenith_angle_calculate(locationlatitude, \
        topocentric_sun_positiondeclination, topocentric_local_hour, sunazimuth, \
        sunzenith):
        """
        sun_topocentric_zenith_angle_calculate(locationlatitude, \
            topocentric_sun_positiondeclination, topocentric_local_hour, sunazimuth, \
            sunzenith)
        
        
        Defined at suews_phys_narp.fpp lines 1055-1094
        
        Parameters
        ----------
        locationlatitude : float
        topocentric_sun_positiondeclination : float
        topocentric_local_hour : float
        sunazimuth : float
        sunzenith : float
        
        """
        _supy_driver.f90wrap_sun_topocentric_zenith_angle_calculate(locationlatitude=locationlatitude, \
            topocentric_sun_positiondeclination=topocentric_sun_positiondeclination, \
            topocentric_local_hour=topocentric_local_hour, sunazimuth=sunazimuth, \
            sunzenith=sunzenith)
    
    @staticmethod
    def set_to_range(var):
        """
        vari = set_to_range(var)
        
        
        Defined at suews_phys_narp.fpp lines 1096-1108
        
        Parameters
        ----------
        var : float
        
        Returns
        -------
        vari : float
        
        """
        vari = _supy_driver.f90wrap_set_to_range(var=var)
        return vari
    
    @staticmethod
    def dewpoint_narp(temp_c, rh):
        """
        td = dewpoint_narp(temp_c, rh)
        
        
        Defined at suews_phys_narp.fpp lines 1111-1121
        
        Parameters
        ----------
        temp_c : float
        rh : float
        
        Returns
        -------
        td : float
        
        """
        td = _supy_driver.f90wrap_dewpoint_narp(temp_c=temp_c, rh=rh)
        return td
    
    @staticmethod
    def prata_emis(temp_k, ea_hpa):
        """
        emis_a = prata_emis(temp_k, ea_hpa)
        
        
        Defined at suews_phys_narp.fpp lines 1124-1129
        
        Parameters
        ----------
        temp_k : float
        ea_hpa : float
        
        Returns
        -------
        emis_a : float
        
        """
        emis_a = _supy_driver.f90wrap_prata_emis(temp_k=temp_k, ea_hpa=ea_hpa)
        return emis_a
    
    @staticmethod
    def emis_cloud(emis_a, fcld):
        """
        em_adj = emis_cloud(emis_a, fcld)
        
        
        Defined at suews_phys_narp.fpp lines 1132-1137
        
        Parameters
        ----------
        emis_a : float
        fcld : float
        
        Returns
        -------
        em_adj : float
        
        """
        em_adj = _supy_driver.f90wrap_emis_cloud(emis_a=emis_a, fcld=fcld)
        return em_adj
    
    @staticmethod
    def emis_cloud_sq(emis_a, fcld):
        """
        em_adj = emis_cloud_sq(emis_a, fcld)
        
        
        Defined at suews_phys_narp.fpp lines 1140-1143
        
        Parameters
        ----------
        emis_a : float
        fcld : float
        
        Returns
        -------
        em_adj : float
        
        """
        em_adj = _supy_driver.f90wrap_emis_cloud_sq(emis_a=emis_a, fcld=fcld)
        return em_adj
    
    @staticmethod
    def cloud_fraction(kdown, kclear):
        """
        fcld = cloud_fraction(kdown, kclear)
        
        
        Defined at suews_phys_narp.fpp lines 1146-1150
        
        Parameters
        ----------
        kdown : float
        kclear : float
        
        Returns
        -------
        fcld : float
        
        """
        fcld = _supy_driver.f90wrap_cloud_fraction(kdown=kdown, kclear=kclear)
        return fcld
    
    @staticmethod
    def wc_fraction(rh, temp):
        """
        fwc = wc_fraction(rh, temp)
        
        
        Defined at suews_phys_narp.fpp lines 1153-1168
        
        Parameters
        ----------
        rh : float
        temp : float
        
        Returns
        -------
        fwc : float
        
        """
        fwc = _supy_driver.f90wrap_wc_fraction(rh=rh, temp=temp)
        return fwc
    
    @staticmethod
    def isurface(doy, zenith):
        """
        isurf = isurface(doy, zenith)
        
        
        Defined at suews_phys_narp.fpp lines 1191-1207
        
        Parameters
        ----------
        doy : int
        zenith : float
        
        Returns
        -------
        isurf : float
        
        """
        isurf = _supy_driver.f90wrap_isurface(doy=doy, zenith=zenith)
        return isurf
    
    @staticmethod
    def solar_esdist(doy):
        """
        rse = solar_esdist(doy)
        
        
        Defined at suews_phys_narp.fpp lines 1210-1219
        
        Parameters
        ----------
        doy : int
        
        Returns
        -------
        rse : float
        
        """
        rse = _supy_driver.f90wrap_solar_esdist(doy=doy)
        return rse
    
    @staticmethod
    def smithlambda(lat):
        """
        g = smithlambda(lat)
        
        
        Defined at suews_phys_narp.fpp lines 1222-1241
        
        Parameters
        ----------
        lat : int
        
        Returns
        -------
        g : float array
        
        """
        g = _supy_driver.f90wrap_smithlambda(lat=lat)
        return g
    
    @staticmethod
    def transmissivity(press_hpa, temp_c_dew, g, zenith):
        """
        trans = transmissivity(press_hpa, temp_c_dew, g, zenith)
        
        
        Defined at suews_phys_narp.fpp lines 1244-1268
        
        Parameters
        ----------
        press_hpa : float
        temp_c_dew : float
        g : float
        zenith : float
        
        Returns
        -------
        trans : float
        
        """
        trans = _supy_driver.f90wrap_transmissivity(press_hpa=press_hpa, \
            temp_c_dew=temp_c_dew, g=g, zenith=zenith)
        return trans
    
    _dt_array_initialisers = []
    

narp_module = Narp_Module()

class Atmmoiststab_Module(f90wrap.runtime.FortranModule):
    """
    Module atmmoiststab_module
    
    
    Defined at suews_phys_atmmoiststab.fpp lines 5-861
    
    """
    @staticmethod
    def cal_atmmoist(temp_c, press_hpa, avrh, dectime):
        """
        lv_j_kg, lvs_j_kg, es_hpa, ea_hpa, vpd_hpa, vpd_pa, dq, dens_dry, avcp, air_dens \
            = cal_atmmoist(temp_c, press_hpa, avrh, dectime)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 21-82
        
        Parameters
        ----------
        temp_c : float
        press_hpa : float
        avrh : float
        dectime : float
        
        Returns
        -------
        lv_j_kg : float
        lvs_j_kg : float
        es_hpa : float
        ea_hpa : float
        vpd_hpa : float
        vpd_pa : float
        dq : float
        dens_dry : float
        avcp : float
        air_dens : float
        
        """
        lv_j_kg, lvs_j_kg, es_hpa, ea_hpa, vpd_hpa, vpd_pa, dq, dens_dry, avcp, air_dens \
            = _supy_driver.f90wrap_cal_atmmoist(temp_c=temp_c, press_hpa=press_hpa, \
            avrh=avrh, dectime=dectime)
        return lv_j_kg, lvs_j_kg, es_hpa, ea_hpa, vpd_hpa, vpd_pa, dq, dens_dry, avcp, \
            air_dens
    
    @staticmethod
    def cal_stab(stabilitymethod, zzd, z0m, zdm, avu1, temp_c, qh_init, avdens, \
        avcp):
        """
        l_mod, tstar, ustar, zl = cal_stab(stabilitymethod, zzd, z0m, zdm, avu1, temp_c, \
            qh_init, avdens, avcp)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 109-224
        
        Parameters
        ----------
        stabilitymethod : int
        zzd : float
        z0m : float
        zdm : float
        avu1 : float
        temp_c : float
        qh_init : float
        avdens : float
        avcp : float
        
        Returns
        -------
        l_mod : float
        tstar : float
        ustar : float
        zl : float
        
        """
        l_mod, tstar, ustar, zl = \
            _supy_driver.f90wrap_cal_stab(stabilitymethod=stabilitymethod, zzd=zzd, \
            z0m=z0m, zdm=zdm, avu1=avu1, temp_c=temp_c, qh_init=qh_init, avdens=avdens, \
            avcp=avcp)
        return l_mod, tstar, ustar, zl
    
    @staticmethod
    def stab_psi_mom(stabilitymethod, zl):
        """
        psim = stab_psi_mom(stabilitymethod, zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 230-241
        
        Parameters
        ----------
        stabilitymethod : int
        zl : float
        
        Returns
        -------
        psim : float
        
        """
        psim = _supy_driver.f90wrap_stab_psi_mom(stabilitymethod=stabilitymethod, zl=zl)
        return psim
    
    @staticmethod
    def stab_psi_heat(stabilitymethod, zl):
        """
        psih = stab_psi_heat(stabilitymethod, zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 244-255
        
        Parameters
        ----------
        stabilitymethod : int
        zl : float
        
        Returns
        -------
        psih : float
        
        """
        psih = _supy_driver.f90wrap_stab_psi_heat(stabilitymethod=stabilitymethod, \
            zl=zl)
        return psih
    
    @staticmethod
    def stab_phi_mom(stabilitymethod, zl):
        """
        phim = stab_phi_mom(stabilitymethod, zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 258-269
        
        Parameters
        ----------
        stabilitymethod : int
        zl : float
        
        Returns
        -------
        phim : float
        
        """
        phim = _supy_driver.f90wrap_stab_phi_mom(stabilitymethod=stabilitymethod, zl=zl)
        return phim
    
    @staticmethod
    def stab_phi_heat(stabilitymethod, zl):
        """
        phih = stab_phi_heat(stabilitymethod, zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 272-283
        
        Parameters
        ----------
        stabilitymethod : int
        zl : float
        
        Returns
        -------
        phih : float
        
        """
        phih = _supy_driver.f90wrap_stab_phi_heat(stabilitymethod=stabilitymethod, \
            zl=zl)
        return phih
    
    @staticmethod
    def psi_mom_j12(zl):
        """
        psim = psi_mom_j12(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 288-302
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psim : float
        
        """
        psim = _supy_driver.f90wrap_psi_mom_j12(zl=zl)
        return psim
    
    @staticmethod
    def phi_mom_j12(zl):
        """
        phim = phi_mom_j12(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 304-316
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phim : float
        
        """
        phim = _supy_driver.f90wrap_phi_mom_j12(zl=zl)
        return phim
    
    @staticmethod
    def psi_heat_j12(zl):
        """
        psih = psi_heat_j12(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 318-330
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psih : float
        
        """
        psih = _supy_driver.f90wrap_psi_heat_j12(zl=zl)
        return psih
    
    @staticmethod
    def phi_heat_j12(zl):
        """
        phih = phi_heat_j12(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 332-340
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phih : float
        
        """
        phih = _supy_driver.f90wrap_phi_heat_j12(zl=zl)
        return phih
    
    @staticmethod
    def psi_mom_g00(zl):
        """
        psim = psi_mom_g00(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 348-365
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psim : float
        
        """
        psim = _supy_driver.f90wrap_psi_mom_g00(zl=zl)
        return psim
    
    @staticmethod
    def psi_heat_g00(zl):
        """
        psih = psi_heat_g00(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 367-384
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psih : float
        
        """
        psih = _supy_driver.f90wrap_psi_heat_g00(zl=zl)
        return psih
    
    @staticmethod
    def phi_mom_g00(zl):
        """
        phim = phi_mom_g00(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 392-413
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phim : float
        
        """
        phim = _supy_driver.f90wrap_phi_mom_g00(zl=zl)
        return phim
    
    @staticmethod
    def phi_heat_g00(zl):
        """
        phih = phi_heat_g00(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 415-433
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phih : float
        
        """
        phih = _supy_driver.f90wrap_phi_heat_g00(zl=zl)
        return phih
    
    @staticmethod
    def psi_conv(zl, ax):
        """
        psic = psi_conv(zl, ax)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 435-440
        
        Parameters
        ----------
        zl : float
        ax : float
        
        Returns
        -------
        psic : float
        
        """
        psic = _supy_driver.f90wrap_psi_conv(zl=zl, ax=ax)
        return psic
    
    @staticmethod
    def phi_conv(zl, ax):
        """
        phic = phi_conv(zl, ax)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 442-450
        
        Parameters
        ----------
        zl : float
        ax : float
        
        Returns
        -------
        phic : float
        
        """
        phic = _supy_driver.f90wrap_phi_conv(zl=zl, ax=ax)
        return phic
    
    @staticmethod
    def dpsi_dzl_g00(zl, psik, phik, psic, phic):
        """
        dpsi = dpsi_dzl_g00(zl, psik, phik, psic, phic)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 452-467
        
        Parameters
        ----------
        zl : float
        psik : float
        phik : float
        psic : float
        phic : float
        
        Returns
        -------
        dpsi : float
        
        """
        dpsi = _supy_driver.f90wrap_dpsi_dzl_g00(zl=zl, psik=psik, phik=phik, psic=psic, \
            phic=phic)
        return dpsi
    
    @staticmethod
    def psi_cb05(zl, k1, k2):
        """
        psi = psi_cb05(zl, k1, k2)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 474-477
        
        Parameters
        ----------
        zl : float
        k1 : float
        k2 : float
        
        Returns
        -------
        psi : float
        
        """
        psi = _supy_driver.f90wrap_psi_cb05(zl=zl, k1=k1, k2=k2)
        return psi
    
    @staticmethod
    def psi_mom_cb05(zl):
        """
        psim = psi_mom_cb05(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 479-488
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psim : float
        
        """
        psim = _supy_driver.f90wrap_psi_mom_cb05(zl=zl)
        return psim
    
    @staticmethod
    def psi_heat_cb05(zl):
        """
        psih = psi_heat_cb05(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 490-499
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psih : float
        
        """
        psih = _supy_driver.f90wrap_psi_heat_cb05(zl=zl)
        return psih
    
    @staticmethod
    def phi_cb05(zl, k1, k2):
        """
        phi = phi_cb05(zl, k1, k2)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 501-508
        
        Parameters
        ----------
        zl : float
        k1 : float
        k2 : float
        
        Returns
        -------
        phi : float
        
        """
        phi = _supy_driver.f90wrap_phi_cb05(zl=zl, k1=k1, k2=k2)
        return phi
    
    @staticmethod
    def phi_mom_cb05(zl):
        """
        phim = phi_mom_cb05(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 510-519
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phim : float
        
        """
        phim = _supy_driver.f90wrap_phi_mom_cb05(zl=zl)
        return phim
    
    @staticmethod
    def phi_heat_cb05(zl):
        """
        phih = phi_heat_cb05(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 521-531
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phih : float
        
        """
        phih = _supy_driver.f90wrap_phi_heat_cb05(zl=zl)
        return phih
    
    @staticmethod
    def phi_mom_k75(zl):
        """
        phim = phi_mom_k75(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 537-546
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phim : float
        
        """
        phim = _supy_driver.f90wrap_phi_mom_k75(zl=zl)
        return phim
    
    @staticmethod
    def phi_heat_k75(zl):
        """
        phih = phi_heat_k75(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 548-557
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phih : float
        
        """
        phih = _supy_driver.f90wrap_phi_heat_k75(zl=zl)
        return phih
    
    @staticmethod
    def psi_mom_k75(zl):
        """
        psim = psi_mom_k75(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 559-568
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psim : float
        
        """
        psim = _supy_driver.f90wrap_psi_mom_k75(zl=zl)
        return psim
    
    @staticmethod
    def psi_heat_k75(zl):
        """
        psih = psi_heat_k75(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 570-579
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psih : float
        
        """
        psih = _supy_driver.f90wrap_psi_heat_k75(zl=zl)
        return psih
    
    @staticmethod
    def phi_mom_b71(zl):
        """
        phim = phi_mom_b71(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 585-595
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phim : float
        
        """
        phim = _supy_driver.f90wrap_phi_mom_b71(zl=zl)
        return phim
    
    @staticmethod
    def phi_heat_b71(zl):
        """
        phih = phi_heat_b71(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 597-607
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        phih : float
        
        """
        phih = _supy_driver.f90wrap_phi_heat_b71(zl=zl)
        return phih
    
    @staticmethod
    def psi_mom_b71(zl):
        """
        psim = psi_mom_b71(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 609-621
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psim : float
        
        """
        psim = _supy_driver.f90wrap_psi_mom_b71(zl=zl)
        return psim
    
    @staticmethod
    def psi_heat_b71(zl):
        """
        psih = psi_heat_b71(zl)
        
        
        Defined at suews_phys_atmmoiststab.fpp lines 623-637
        
        Parameters
        ----------
        zl : float
        
        Returns
        -------
        psih : float
        
        """
        psih = _supy_driver.f90wrap_psi_heat_b71(zl=zl)
        return psih
    
    @property
    def neut_limit(self):
        """
        Element neut_limit ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_phys_atmmoiststab.fpp line 7
        
        """
        return _supy_driver.f90wrap_atmmoiststab_module__get__neut_limit()
    
    @property
    def k(self):
        """
        Element k ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_phys_atmmoiststab.fpp line 8
        
        """
        return _supy_driver.f90wrap_atmmoiststab_module__get__k()
    
    @property
    def grav(self):
        """
        Element grav ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_phys_atmmoiststab.fpp line 9
        
        """
        return _supy_driver.f90wrap_atmmoiststab_module__get__grav()
    
    @property
    def j12(self):
        """
        Element j12 ftype=integer pytype=int
        
        
        Defined at suews_phys_atmmoiststab.fpp line 11
        
        """
        return _supy_driver.f90wrap_atmmoiststab_module__get__j12()
    
    @property
    def k75(self):
        """
        Element k75 ftype=integer pytype=int
        
        
        Defined at suews_phys_atmmoiststab.fpp line 12
        
        """
        return _supy_driver.f90wrap_atmmoiststab_module__get__k75()
    
    @property
    def b71(self):
        """
        Element b71 ftype=integer pytype=int
        
        
        Defined at suews_phys_atmmoiststab.fpp line 13
        
        """
        return _supy_driver.f90wrap_atmmoiststab_module__get__b71()
    
    def __str__(self):
        ret = ['<atmmoiststab_module>{\n']
        ret.append('    neut_limit : ')
        ret.append(repr(self.neut_limit))
        ret.append(',\n    k : ')
        ret.append(repr(self.k))
        ret.append(',\n    grav : ')
        ret.append(repr(self.grav))
        ret.append(',\n    j12 : ')
        ret.append(repr(self.j12))
        ret.append(',\n    k75 : ')
        ret.append(repr(self.k75))
        ret.append(',\n    b71 : ')
        ret.append(repr(self.b71))
        ret.append('}')
        return ''.join(ret)
    
    _dt_array_initialisers = []
    

atmmoiststab_module = Atmmoiststab_Module()

class Waterdist_Module(f90wrap.runtime.FortranModule):
    """
    Module waterdist_module
    
    
    Defined at suews_phys_waterdist.fpp lines 5-1175
    
    """
    @staticmethod
    def drainage(is_, state_is, storcap, draineq, draincoef1, draincoef2, nsh_real):
        """
        drain_is = drainage(is_, state_is, storcap, draineq, draincoef1, draincoef2, \
            nsh_real)
        
        
        Defined at suews_phys_waterdist.fpp lines 30-78
        
        Parameters
        ----------
        is_ : int
        state_is : float
        storcap : float
        draineq : float
        draincoef1 : float
        draincoef2 : float
        nsh_real : float
        
        Returns
        -------
        drain_is : float
        
        ------------------------------------------------------------------------------
        """
        drain_is = _supy_driver.f90wrap_drainage(is_=is_, state_is=state_is, \
            storcap=storcap, draineq=draineq, draincoef1=draincoef1, \
            draincoef2=draincoef2, nsh_real=nsh_real)
        return drain_is
    
    @staticmethod
    def cal_water_storage(is_, sfr_surf, pipecapacity, runofftowater, pin, wu_surf, \
        drain_surf, addwater, addimpervious, nsh_real, state_in, frac_water2runoff, \
        pervfraction, addveg, soilstorecap, addwaterbody, flowchange, statelimit, \
        runoffagimpervious, runoffagveg, runoffpipes, ev, soilstore_id, \
        surpluswaterbody, surplusevap, runoffwaterbody, runoff, state_out):
        """
        cal_water_storage(is_, sfr_surf, pipecapacity, runofftowater, pin, wu_surf, \
            drain_surf, addwater, addimpervious, nsh_real, state_in, frac_water2runoff, \
            pervfraction, addveg, soilstorecap, addwaterbody, flowchange, statelimit, \
            runoffagimpervious, runoffagveg, runoffpipes, ev, soilstore_id, \
            surpluswaterbody, surplusevap, runoffwaterbody, runoff, state_out)
        
        
        Defined at suews_phys_waterdist.fpp lines 89-338
        
        Parameters
        ----------
        is_ : int
        sfr_surf : float array
        pipecapacity : float
        runofftowater : float
        pin : float
        wu_surf : float array
        drain_surf : float array
        addwater : float array
        addimpervious : float
        nsh_real : float
        state_in : float array
        frac_water2runoff : float array
        pervfraction : float
        addveg : float
        soilstorecap : float array
        addwaterbody : float
        flowchange : float
        statelimit : float array
        runoffagimpervious : float
        runoffagveg : float
        runoffpipes : float
        ev : float
        soilstore_id : float array
        surpluswaterbody : float
        surplusevap : float array
        runoffwaterbody : float
        runoff : float array
        state_out : float array
        
        ------------------------------------------------------------------------------
        Calculation of storage change
         TS 30 Nov 2019
           - Allow irrigation on all surfaces(previously only on vegetated surfaces)
         LJ 27 Jan 2016
           - Removed tabs and cleaned the code
         HCW 08 Dec 2015
           -Added if-loop check for no Paved surfaces
         LJ 6 May 2015
           - Calculations of the piperunoff exceedings moved to separate subroutine \
               updateFlood.
           - Now also called from snow subroutine
           - Evaporation is modified using EvapPart
           - when no water on impervious surfaces, evap occurs above pervious surfaces \
               instead
         Rewritten by HCW 12 Feb 2015
           - Old variable 'p' for water input to the surface renamed to 'p_mm'
           - All water now added to p_mm first, before threshold checks or other \
               calculations
           - Water from other grids now added to p_mm(instead of state_id for impervious \
               surfaces)
           - Removed division of runoff by nsh, as whole model now runs at the same \
               timestep
           - Adjusted transfer of ev between surfaces to conserve mass(not depth)
           - Volumes used for water transport between grids to account for SurfaceArea \
               changing between grids
           - Added threshold check for state_id(WaterSurf) - was going negative
         Last modified HCW 09 Feb 2015
           - Removed StorCap input because it is provided by module allocateArray
           - Tidied and commented code
         Modified by LJ in November 2012:
           - P>10 was not taken into account for impervious surfaces - Was fixed.
           - Above impervious surfaces possibility of the state_id to exceed max capacity \
               was limited
             although this should be possible - was fixed
         Modified by LJ 10/2010
         Rewritten mostly by LJ in 2010
         To do:
           - Finish area normalisation for RG2G & finish coding GridConnections
           - What is the 10 mm hr-1 threshold for?
          - Decide upon and correct storage capacities here & in evap subroutine
          - FlowChange units should be mm hr-1 - need to update everywhere
           - Add SurfaceFlood(is)?
           - What happens if sfr_surf(is) = 0 or 1?
           - Consider how irrigated trees actually works...
        ------------------------------------------------------------------------------
        """
        _supy_driver.f90wrap_cal_water_storage(is_=is_, sfr_surf=sfr_surf, \
            pipecapacity=pipecapacity, runofftowater=runofftowater, pin=pin, \
            wu_surf=wu_surf, drain_surf=drain_surf, addwater=addwater, \
            addimpervious=addimpervious, nsh_real=nsh_real, state_in=state_in, \
            frac_water2runoff=frac_water2runoff, pervfraction=pervfraction, \
            addveg=addveg, soilstorecap=soilstorecap, addwaterbody=addwaterbody, \
            flowchange=flowchange, statelimit=statelimit, \
            runoffagimpervious=runoffagimpervious, runoffagveg=runoffagveg, \
            runoffpipes=runoffpipes, ev=ev, soilstore_id=soilstore_id, \
            surpluswaterbody=surpluswaterbody, surplusevap=surplusevap, \
            runoffwaterbody=runoffwaterbody, runoff=runoff, state_out=state_out)
    
    @staticmethod
    def cal_water_storage_surf(pin, nsh_real, pipecapacity, runofftowater, \
        addimpervious, addveg, addwaterbody, flowchange, soilstorecap_surf, \
        statelimit_surf, pervfraction, sfr_surf, drain_surf, addwater_surf, \
        frac_water2runoff_surf, wu_surf, ev_surf_in, state_surf_in, \
        soilstore_surf_in, ev_surf_out, state_surf_out, soilstore_surf_out, \
        runoff_surf):
        """
        runoffagimpervious_grid, runoffagveg_grid, runoffpipes_grid, \
            runoffwaterbody_grid = cal_water_storage_surf(pin, nsh_real, pipecapacity, \
            runofftowater, addimpervious, addveg, addwaterbody, flowchange, \
            soilstorecap_surf, statelimit_surf, pervfraction, sfr_surf, drain_surf, \
            addwater_surf, frac_water2runoff_surf, wu_surf, ev_surf_in, state_surf_in, \
            soilstore_surf_in, ev_surf_out, state_surf_out, soilstore_surf_out, \
            runoff_surf)
        
        
        Defined at suews_phys_waterdist.fpp lines 353-445
        
        Parameters
        ----------
        pin : float
        nsh_real : float
        pipecapacity : float
        runofftowater : float
        addimpervious : float
        addveg : float
        addwaterbody : float
        flowchange : float
        soilstorecap_surf : float array
        statelimit_surf : float array
        pervfraction : float
        sfr_surf : float array
        drain_surf : float array
        addwater_surf : float array
        frac_water2runoff_surf : float array
        wu_surf : float array
        ev_surf_in : float array
        state_surf_in : float array
        soilstore_surf_in : float array
        ev_surf_out : float array
        state_surf_out : float array
        soilstore_surf_out : float array
        runoff_surf : float array
        
        Returns
        -------
        runoffagimpervious_grid : float
        runoffagveg_grid : float
        runoffpipes_grid : float
        runoffwaterbody_grid : float
        
        """
        runoffagimpervious_grid, runoffagveg_grid, runoffpipes_grid, \
            runoffwaterbody_grid = _supy_driver.f90wrap_cal_water_storage_surf(pin=pin, \
            nsh_real=nsh_real, pipecapacity=pipecapacity, runofftowater=runofftowater, \
            addimpervious=addimpervious, addveg=addveg, addwaterbody=addwaterbody, \
            flowchange=flowchange, soilstorecap_surf=soilstorecap_surf, \
            statelimit_surf=statelimit_surf, pervfraction=pervfraction, \
            sfr_surf=sfr_surf, drain_surf=drain_surf, addwater_surf=addwater_surf, \
            frac_water2runoff_surf=frac_water2runoff_surf, wu_surf=wu_surf, \
            ev_surf_in=ev_surf_in, state_surf_in=state_surf_in, \
            soilstore_surf_in=soilstore_surf_in, ev_surf_out=ev_surf_out, \
            state_surf_out=state_surf_out, soilstore_surf_out=soilstore_surf_out, \
            runoff_surf=runoff_surf)
        return runoffagimpervious_grid, runoffagveg_grid, runoffpipes_grid, \
            runoffwaterbody_grid
    
    @staticmethod
    def cal_water_storage_building(pin, nsh_real, nlayer, sfr_roof, statelimit_roof, \
        soilstorecap_roof, wetthresh_roof, ev_roof_in, state_roof_in, \
        soilstore_roof_in, sfr_wall, statelimit_wall, soilstorecap_wall, \
        wetthresh_wall, ev_wall_in, state_wall_in, soilstore_wall_in, ev_roof_out, \
        state_roof_out, soilstore_roof_out, runoff_roof, ev_wall_out, \
        state_wall_out, soilstore_wall_out, runoff_wall):
        """
        state_building, soilstore_building, runoff_building, soilstorecap_building = \
            cal_water_storage_building(pin, nsh_real, nlayer, sfr_roof, statelimit_roof, \
            soilstorecap_roof, wetthresh_roof, ev_roof_in, state_roof_in, \
            soilstore_roof_in, sfr_wall, statelimit_wall, soilstorecap_wall, \
            wetthresh_wall, ev_wall_in, state_wall_in, soilstore_wall_in, ev_roof_out, \
            state_roof_out, soilstore_roof_out, runoff_roof, ev_wall_out, \
            state_wall_out, soilstore_wall_out, runoff_wall)
        
        
        Defined at suews_phys_waterdist.fpp lines 447-608
        
        Parameters
        ----------
        pin : float
        nsh_real : float
        nlayer : int
        sfr_roof : float array
        statelimit_roof : float array
        soilstorecap_roof : float array
        wetthresh_roof : float array
        ev_roof_in : float array
        state_roof_in : float array
        soilstore_roof_in : float array
        sfr_wall : float array
        statelimit_wall : float array
        soilstorecap_wall : float array
        wetthresh_wall : float array
        ev_wall_in : float array
        state_wall_in : float array
        soilstore_wall_in : float array
        ev_roof_out : float array
        state_roof_out : float array
        soilstore_roof_out : float array
        runoff_roof : float array
        ev_wall_out : float array
        state_wall_out : float array
        soilstore_wall_out : float array
        runoff_wall : float array
        
        Returns
        -------
        state_building : float
        soilstore_building : float
        runoff_building : float
        soilstorecap_building : float
        
        """
        state_building, soilstore_building, runoff_building, soilstorecap_building = \
            _supy_driver.f90wrap_cal_water_storage_building(pin=pin, nsh_real=nsh_real, \
            nlayer=nlayer, sfr_roof=sfr_roof, statelimit_roof=statelimit_roof, \
            soilstorecap_roof=soilstorecap_roof, wetthresh_roof=wetthresh_roof, \
            ev_roof_in=ev_roof_in, state_roof_in=state_roof_in, \
            soilstore_roof_in=soilstore_roof_in, sfr_wall=sfr_wall, \
            statelimit_wall=statelimit_wall, soilstorecap_wall=soilstorecap_wall, \
            wetthresh_wall=wetthresh_wall, ev_wall_in=ev_wall_in, \
            state_wall_in=state_wall_in, soilstore_wall_in=soilstore_wall_in, \
            ev_roof_out=ev_roof_out, state_roof_out=state_roof_out, \
            soilstore_roof_out=soilstore_roof_out, runoff_roof=runoff_roof, \
            ev_wall_out=ev_wall_out, state_wall_out=state_wall_out, \
            soilstore_wall_out=soilstore_wall_out, runoff_wall=runoff_wall)
        return state_building, soilstore_building, runoff_building, \
            soilstorecap_building
    
    @staticmethod
    def updateflood(is_, runoff, sfr_surf, pipecapacity, runofftowater, \
        runoffagimpervious, surpluswaterbody, runoffagveg, runoffpipes):
        """
        updateflood(is_, runoff, sfr_surf, pipecapacity, runofftowater, \
            runoffagimpervious, surpluswaterbody, runoffagveg, runoffpipes)
        
        
        Defined at suews_phys_waterdist.fpp lines 614-647
        
        Parameters
        ----------
        is_ : int
        runoff : float array
        sfr_surf : float array
        pipecapacity : float
        runofftowater : float
        runoffagimpervious : float
        surpluswaterbody : float
        runoffagveg : float
        runoffpipes : float
        
        ------Paved and building surface
        """
        _supy_driver.f90wrap_updateflood(is_=is_, runoff=runoff, sfr_surf=sfr_surf, \
            pipecapacity=pipecapacity, runofftowater=runofftowater, \
            runoffagimpervious=runoffagimpervious, surpluswaterbody=surpluswaterbody, \
            runoffagveg=runoffagveg, runoffpipes=runoffpipes)
    
    @staticmethod
    def redistributewater(snowuse, waterdist, sfr_surf, drain, addwaterrunoff, \
        addwater):
        """
        redistributewater(snowuse, waterdist, sfr_surf, drain, addwaterrunoff, addwater)
        
        
        Defined at suews_phys_waterdist.fpp lines 653-688
        
        Parameters
        ----------
        snowuse : int
        waterdist : float array
        sfr_surf : float array
        drain : float array
        addwaterrunoff : float array
        addwater : float array
        
        -------------------------------------------------------------------
        """
        _supy_driver.f90wrap_redistributewater(snowuse=snowuse, waterdist=waterdist, \
            sfr_surf=sfr_surf, drain=drain, addwaterrunoff=addwaterrunoff, \
            addwater=addwater)
    
    @staticmethod
    def suews_update_soilmoist(nonwaterfraction, soilstorecap, sfr_surf, \
        soilstore_id):
        """
        soilmoistcap, soilstate, vsmd, smd = suews_update_soilmoist(nonwaterfraction, \
            soilstorecap, sfr_surf, soilstore_id)
        
        
        Defined at suews_phys_waterdist.fpp lines 696-732
        
        Parameters
        ----------
        nonwaterfraction : float
        soilstorecap : float array
        sfr_surf : float array
        soilstore_id : float array
        
        Returns
        -------
        soilmoistcap : float
        soilstate : float
        vsmd : float
        smd : float
        
        """
        soilmoistcap, soilstate, vsmd, smd = \
            _supy_driver.f90wrap_suews_update_soilmoist(nonwaterfraction=nonwaterfraction, \
            soilstorecap=soilstorecap, sfr_surf=sfr_surf, soilstore_id=soilstore_id)
        return soilmoistcap, soilstate, vsmd, smd
    
    @staticmethod
    def cal_smd_veg(soilstorecap, soilstore_id, sfr_surf):
        """
        vsmd = cal_smd_veg(soilstorecap, soilstore_id, sfr_surf)
        
        
        Defined at suews_phys_waterdist.fpp lines 736-751
        
        Parameters
        ----------
        soilstorecap : float array
        soilstore_id : float array
        sfr_surf : float array
        
        Returns
        -------
        vsmd : float
        
        """
        vsmd = _supy_driver.f90wrap_cal_smd_veg(soilstorecap=soilstorecap, \
            soilstore_id=soilstore_id, sfr_surf=sfr_surf)
        return vsmd
    
    @staticmethod
    def suews_cal_soilstate(smdmethod, xsmd, nonwaterfraction, soilmoistcap, \
        soilstorecap, surf_chang_per_tstep, soilstore_id, soilstoreold, sfr_surf, \
        smd_nsurf):
        """
        smd, tot_chang_per_tstep, soilstate = suews_cal_soilstate(smdmethod, xsmd, \
            nonwaterfraction, soilmoistcap, soilstorecap, surf_chang_per_tstep, \
            soilstore_id, soilstoreold, sfr_surf, smd_nsurf)
        
        
        Defined at suews_phys_waterdist.fpp lines 758-809
        
        Parameters
        ----------
        smdmethod : int
        xsmd : float
        nonwaterfraction : float
        soilmoistcap : float
        soilstorecap : float array
        surf_chang_per_tstep : float
        soilstore_id : float array
        soilstoreold : float array
        sfr_surf : float array
        smd_nsurf : float array
        
        Returns
        -------
        smd : float
        tot_chang_per_tstep : float
        soilstate : float
        
        """
        smd, tot_chang_per_tstep, soilstate = \
            _supy_driver.f90wrap_suews_cal_soilstate(smdmethod=smdmethod, xsmd=xsmd, \
            nonwaterfraction=nonwaterfraction, soilmoistcap=soilmoistcap, \
            soilstorecap=soilstorecap, surf_chang_per_tstep=surf_chang_per_tstep, \
            soilstore_id=soilstore_id, soilstoreold=soilstoreold, sfr_surf=sfr_surf, \
            smd_nsurf=smd_nsurf)
        return smd, tot_chang_per_tstep, soilstate
    
    @staticmethod
    def suews_cal_horizontalsoilwater(sfr_surf, soilstorecap, soildepth, \
        sathydraulicconduct, surfacearea, nonwaterfraction, tstep_real, \
        soilstore_id, runoffsoil):
        """
        runoffsoil_per_tstep = suews_cal_horizontalsoilwater(sfr_surf, soilstorecap, \
            soildepth, sathydraulicconduct, surfacearea, nonwaterfraction, tstep_real, \
            soilstore_id, runoffsoil)
        
        
        Defined at suews_phys_waterdist.fpp lines 823-1003
        
        Parameters
        ----------
        sfr_surf : float array
        soilstorecap : float array
        soildepth : float array
        sathydraulicconduct : float array
        surfacearea : float
        nonwaterfraction : float
        tstep_real : float
        soilstore_id : float array
        runoffsoil : float array
        
        Returns
        -------
        runoffsoil_per_tstep : float
        
        ------------------------------------------------------
         use SUES_data
         use gis_data
         use time
         use allocateArray
        """
        runoffsoil_per_tstep = \
            _supy_driver.f90wrap_suews_cal_horizontalsoilwater(sfr_surf=sfr_surf, \
            soilstorecap=soilstorecap, soildepth=soildepth, \
            sathydraulicconduct=sathydraulicconduct, surfacearea=surfacearea, \
            nonwaterfraction=nonwaterfraction, tstep_real=tstep_real, \
            soilstore_id=soilstore_id, runoffsoil=runoffsoil)
        return runoffsoil_per_tstep
    
    @staticmethod
    def suews_cal_wateruse(nsh_real, wu_m3, surfacearea, sfr_surf, irrfracpaved, \
        irrfracbldgs, irrfracevetr, irrfracdectr, irrfracgrass, irrfracbsoil, \
        irrfracwater, dayofweek_id, wuprofa_24hr, wuprofm_24hr, internalwateruse_h, \
        hdd_id, wuday_id, waterusemethod, nsh, it, imin, dls, wu_surf):
        """
        wu_int, wu_ext = suews_cal_wateruse(nsh_real, wu_m3, surfacearea, sfr_surf, \
            irrfracpaved, irrfracbldgs, irrfracevetr, irrfracdectr, irrfracgrass, \
            irrfracbsoil, irrfracwater, dayofweek_id, wuprofa_24hr, wuprofm_24hr, \
            internalwateruse_h, hdd_id, wuday_id, waterusemethod, nsh, it, imin, dls, \
            wu_surf)
        
        
        Defined at suews_phys_waterdist.fpp lines 1016-1174
        
        Parameters
        ----------
        nsh_real : float
        wu_m3 : float
        surfacearea : float
        sfr_surf : float array
        irrfracpaved : float
        irrfracbldgs : float
        irrfracevetr : float
        irrfracdectr : float
        irrfracgrass : float
        irrfracbsoil : float
        irrfracwater : float
        dayofweek_id : int array
        wuprofa_24hr : float array
        wuprofm_24hr : float array
        internalwateruse_h : float
        hdd_id : float array
        wuday_id : float array
        waterusemethod : int
        nsh : int
        it : int
        imin : int
        dls : int
        wu_surf : float array
        
        Returns
        -------
        wu_int : float
        wu_ext : float
        
        """
        wu_int, wu_ext = _supy_driver.f90wrap_suews_cal_wateruse(nsh_real=nsh_real, \
            wu_m3=wu_m3, surfacearea=surfacearea, sfr_surf=sfr_surf, \
            irrfracpaved=irrfracpaved, irrfracbldgs=irrfracbldgs, \
            irrfracevetr=irrfracevetr, irrfracdectr=irrfracdectr, \
            irrfracgrass=irrfracgrass, irrfracbsoil=irrfracbsoil, \
            irrfracwater=irrfracwater, dayofweek_id=dayofweek_id, \
            wuprofa_24hr=wuprofa_24hr, wuprofm_24hr=wuprofm_24hr, \
            internalwateruse_h=internalwateruse_h, hdd_id=hdd_id, wuday_id=wuday_id, \
            waterusemethod=waterusemethod, nsh=nsh, it=it, imin=imin, dls=dls, \
            wu_surf=wu_surf)
        return wu_int, wu_ext
    
    _dt_array_initialisers = []
    

waterdist_module = Waterdist_Module()

class Resist_Module(f90wrap.runtime.FortranModule):
    """
    Module resist_module
    
    
    Defined at suews_phys_resist.fpp lines 5-505
    
    """
    @staticmethod
    def aerodynamicresistance(zzd, z0m, avu1, l_mod, ustar, vegfraction, \
        aerodynamicresistancemethod, stabilitymethod, roughlenheatmethod):
        """
        ra_h, z0v = aerodynamicresistance(zzd, z0m, avu1, l_mod, ustar, vegfraction, \
            aerodynamicresistancemethod, stabilitymethod, roughlenheatmethod)
        
        
        Defined at suews_phys_resist.fpp lines 18-101
        
        Parameters
        ----------
        zzd : float
        z0m : float
        avu1 : float
        l_mod : float
        ustar : float
        vegfraction : float
        aerodynamicresistancemethod : int
        stabilitymethod : int
        roughlenheatmethod : int
        
        Returns
        -------
        ra_h : float
        z0v : float
        
        """
        ra_h, z0v = _supy_driver.f90wrap_aerodynamicresistance(zzd=zzd, z0m=z0m, \
            avu1=avu1, l_mod=l_mod, ustar=ustar, vegfraction=vegfraction, \
            aerodynamicresistancemethod=aerodynamicresistancemethod, \
            stabilitymethod=stabilitymethod, roughlenheatmethod=roughlenheatmethod)
        return ra_h, z0v
    
    @staticmethod
    def surfaceresistance(id, it, smdmethod, snowfrac, sfr_surf, avkdn, temp_c, dq, \
        xsmd, vsmd, maxconductance, laimax, lai_id, gsmodel, kmax, g_max, g_k, \
        g_q_base, g_q_shape, g_t, g_sm, th, tl, s1, s2):
        """
        g_kdown, g_dq, g_ta, g_smd, g_lai, gfunc, gsc, rs = surfaceresistance(id, it, \
            smdmethod, snowfrac, sfr_surf, avkdn, temp_c, dq, xsmd, vsmd, \
            maxconductance, laimax, lai_id, gsmodel, kmax, g_max, g_k, g_q_base, \
            g_q_shape, g_t, g_sm, th, tl, s1, s2)
        
        
        Defined at suews_phys_resist.fpp lines 103-340
        
        Parameters
        ----------
        id : int
        it : int
        smdmethod : int
        snowfrac : float array
        sfr_surf : float array
        avkdn : float
        temp_c : float
        dq : float
        xsmd : float
        vsmd : float
        maxconductance : float array
        laimax : float array
        lai_id : float array
        gsmodel : int
        kmax : float
        g_max : float
        g_k : float
        g_q_base : float
        g_q_shape : float
        g_t : float
        g_sm : float
        th : float
        tl : float
        s1 : float
        s2 : float
        
        Returns
        -------
        g_kdown : float
        g_dq : float
        g_ta : float
        g_smd : float
        g_lai : float
        gfunc : float
        gsc : float
        rs : float
        
        """
        g_kdown, g_dq, g_ta, g_smd, g_lai, gfunc, gsc, rs = \
            _supy_driver.f90wrap_surfaceresistance(id=id, it=it, smdmethod=smdmethod, \
            snowfrac=snowfrac, sfr_surf=sfr_surf, avkdn=avkdn, temp_c=temp_c, dq=dq, \
            xsmd=xsmd, vsmd=vsmd, maxconductance=maxconductance, laimax=laimax, \
            lai_id=lai_id, gsmodel=gsmodel, kmax=kmax, g_max=g_max, g_k=g_k, \
            g_q_base=g_q_base, g_q_shape=g_q_shape, g_t=g_t, g_sm=g_sm, th=th, tl=tl, \
            s1=s1, s2=s2)
        return g_kdown, g_dq, g_ta, g_smd, g_lai, gfunc, gsc, rs
    
    @staticmethod
    def boundarylayerresistance(zzd, z0m, avu1, ustar):
        """
        rb = boundarylayerresistance(zzd, z0m, avu1, ustar)
        
        
        Defined at suews_phys_resist.fpp lines 342-361
        
        Parameters
        ----------
        zzd : float
        z0m : float
        avu1 : float
        ustar : float
        
        Returns
        -------
        rb : float
        
        """
        rb = _supy_driver.f90wrap_boundarylayerresistance(zzd=zzd, z0m=z0m, avu1=avu1, \
            ustar=ustar)
        return rb
    
    @staticmethod
    def suews_cal_roughnessparameters(roughlenmommethod, sfr_surf, bldgh, evetreeh, \
        dectreeh, porosity_dectr, faibldg, faievetree, faidectree, z0m_in, zdm_in, \
        z):
        """
        fai, pai, zh, z0m, zdm, zzd = suews_cal_roughnessparameters(roughlenmommethod, \
            sfr_surf, bldgh, evetreeh, dectreeh, porosity_dectr, faibldg, faievetree, \
            faidectree, z0m_in, zdm_in, z)
        
        
        Defined at suews_phys_resist.fpp lines 363-466
        
        Parameters
        ----------
        roughlenmommethod : int
        sfr_surf : float array
        bldgh : float
        evetreeh : float
        dectreeh : float
        porosity_dectr : float
        faibldg : float
        faievetree : float
        faidectree : float
        z0m_in : float
        zdm_in : float
        z : float
        
        Returns
        -------
        fai : float
        pai : float
        zh : float
        z0m : float
        zdm : float
        zzd : float
        
        --------------------------------------------------------------------------------
        """
        fai, pai, zh, z0m, zdm, zzd = \
            _supy_driver.f90wrap_suews_cal_roughnessparameters(roughlenmommethod=roughlenmommethod, \
            sfr_surf=sfr_surf, bldgh=bldgh, evetreeh=evetreeh, dectreeh=dectreeh, \
            porosity_dectr=porosity_dectr, faibldg=faibldg, faievetree=faievetree, \
            faidectree=faidectree, z0m_in=z0m_in, zdm_in=zdm_in, z=z)
        return fai, pai, zh, z0m, zdm, zzd
    
    @staticmethod
    def cal_z0v(roughlenheatmethod, z0m, vegfraction, ustar):
        """
        z0v = cal_z0v(roughlenheatmethod, z0m, vegfraction, ustar)
        
        
        Defined at suews_phys_resist.fpp lines 468-499
        
        Parameters
        ----------
        roughlenheatmethod : int
        z0m : float
        vegfraction : float
        ustar : float
        
        Returns
        -------
        z0v : float
        
        """
        z0v = _supy_driver.f90wrap_cal_z0v(roughlenheatmethod=roughlenheatmethod, \
            z0m=z0m, vegfraction=vegfraction, ustar=ustar)
        return z0v
    
    @staticmethod
    def sigmoid(x):
        """
        res = sigmoid(x)
        
        
        Defined at suews_phys_resist.fpp lines 501-505
        
        Parameters
        ----------
        x : float
        
        Returns
        -------
        res : float
        
        """
        res = _supy_driver.f90wrap_sigmoid(x=x)
        return res
    
    _dt_array_initialisers = []
    

resist_module = Resist_Module()

class Evap_Module(f90wrap.runtime.FortranModule):
    """
    Module evap_module
    
    
    Defined at suews_phys_evap.fpp lines 5-146
    
    """
    @staticmethod
    def cal_evap(evapmethod, state_is, wetthresh_is, capstore_is, vpd_hpa, avdens, \
        avcp, qn_e, s_hpa, psyc_hpa, rs, ra, rb, tlv):
        """
        rss, ev, qe = cal_evap(evapmethod, state_is, wetthresh_is, capstore_is, vpd_hpa, \
            avdens, avcp, qn_e, s_hpa, psyc_hpa, rs, ra, rb, tlv)
        
        
        Defined at suews_phys_evap.fpp lines 11-106
        
        Parameters
        ----------
        evapmethod : int
        state_is : float
        wetthresh_is : float
        capstore_is : float
        vpd_hpa : float
        avdens : float
        avcp : float
        qn_e : float
        s_hpa : float
        psyc_hpa : float
        rs : float
        ra : float
        rb : float
        tlv : float
        
        Returns
        -------
        rss : float
        ev : float
        qe : float
        
        ------------------------------------------------------------------------------
        -Calculates evaporation for each surface from modified Penman-Monteith eqn
        -State determines whether each surface type is dry or wet(wet/transition)
        -Wet surfaces below storage capacity are in transition
         and QE depends on the state and storage capacity(i.e. varies with surface);
         for wet or dry surfaces QE does not vary between surface types
        -See Sect 2.4 of Jarvi et al. (2011) Ja11
        Last modified:
          HCW 06 Jul 2016
           Moved rss declaration to LUMPS_Module_Constants so it can be written out
          HCW 11 Jun 2015
           Added WetThresh to distinguish wet/partially wet surfaces from the storage \
               capacities used in SUEWS_drain
          HCW 30 Jan 2015
           Removed StorCap input because it is provided by module allocateArray
           Tidied and commented code
          LJ 10/2010
        ------------------------------------------------------------------------------
        """
        rss, ev, qe = _supy_driver.f90wrap_cal_evap(evapmethod=evapmethod, \
            state_is=state_is, wetthresh_is=wetthresh_is, capstore_is=capstore_is, \
            vpd_hpa=vpd_hpa, avdens=avdens, avcp=avcp, qn_e=qn_e, s_hpa=s_hpa, \
            psyc_hpa=psyc_hpa, rs=rs, ra=ra, rb=rb, tlv=tlv)
        return rss, ev, qe
    
    @staticmethod
    def cal_evap_multi(evapmethod, sfr_multi, state_multi, wetthresh_multi, \
        capstore_multi, vpd_hpa, avdens, avcp, qn_e_multi, s_hpa, psyc_hpa, rs, ra, \
        rb, tlv, rss_multi, ev_multi, qe_multi):
        """
        cal_evap_multi(evapmethod, sfr_multi, state_multi, wetthresh_multi, \
            capstore_multi, vpd_hpa, avdens, avcp, qn_e_multi, s_hpa, psyc_hpa, rs, ra, \
            rb, tlv, rss_multi, ev_multi, qe_multi)
        
        
        Defined at suews_phys_evap.fpp lines 108-146
        
        Parameters
        ----------
        evapmethod : int
        sfr_multi : float array
        state_multi : float array
        wetthresh_multi : float array
        capstore_multi : float array
        vpd_hpa : float
        avdens : float
        avcp : float
        qn_e_multi : float array
        s_hpa : float
        psyc_hpa : float
        rs : float
        ra : float
        rb : float
        tlv : float
        rss_multi : float array
        ev_multi : float array
        qe_multi : float array
        
        """
        _supy_driver.f90wrap_cal_evap_multi(evapmethod=evapmethod, sfr_multi=sfr_multi, \
            state_multi=state_multi, wetthresh_multi=wetthresh_multi, \
            capstore_multi=capstore_multi, vpd_hpa=vpd_hpa, avdens=avdens, avcp=avcp, \
            qn_e_multi=qn_e_multi, s_hpa=s_hpa, psyc_hpa=psyc_hpa, rs=rs, ra=ra, rb=rb, \
            tlv=tlv, rss_multi=rss_multi, ev_multi=ev_multi, qe_multi=qe_multi)
    
    _dt_array_initialisers = []
    

evap_module = Evap_Module()

class Dailystate_Module(f90wrap.runtime.FortranModule):
    """
    Module dailystate_module
    
    
    Defined at suews_phys_dailystate.fpp lines 5-949
    
    """
    @staticmethod
    def suews_cal_dailystate(iy, id, it, imin, isec, tstep, tstep_prev, \
        dt_since_start, dayofweek_id, tmin_id_prev, tmax_id_prev, lenday_id_prev, \
        basetmethod, waterusemethod, ie_start, ie_end, laicalcyes, laitype, \
        nsh_real, avkdn, temp_c, precip, baset_hc, baset_heating, baset_cooling, \
        lat, faut, lai_obs, albmax_dectr, albmax_evetr, albmax_grass, albmin_dectr, \
        albmin_evetr, albmin_grass, capmax_dec, capmin_dec, pormax_dec, pormin_dec, \
        ie_a, ie_m, daywatper, daywat, baset, basete, gddfull, sddfull, laimin, \
        laimax, laipower, decidcap_id_prev, storedrainprm_prev, lai_id_prev, \
        gdd_id_prev, sdd_id_prev, albdectr_id_prev, albevetr_id_prev, \
        albgrass_id_prev, porosity_id_prev, hdd_id_prev, state_id, soilstore_id, \
        soilstorecap, h_maintain, hdd_id_next, porosity_id_next, storedrainprm_next, \
        lai_id_next, gdd_id_next, sdd_id_next, wuday_id):
        """
        tmin_id_next, tmax_id_next, lenday_id_next, albdectr_id_next, albevetr_id_next, \
            albgrass_id_next, decidcap_id_next = suews_cal_dailystate(iy, id, it, imin, \
            isec, tstep, tstep_prev, dt_since_start, dayofweek_id, tmin_id_prev, \
            tmax_id_prev, lenday_id_prev, basetmethod, waterusemethod, ie_start, ie_end, \
            laicalcyes, laitype, nsh_real, avkdn, temp_c, precip, baset_hc, \
            baset_heating, baset_cooling, lat, faut, lai_obs, albmax_dectr, \
            albmax_evetr, albmax_grass, albmin_dectr, albmin_evetr, albmin_grass, \
            capmax_dec, capmin_dec, pormax_dec, pormin_dec, ie_a, ie_m, daywatper, \
            daywat, baset, basete, gddfull, sddfull, laimin, laimax, laipower, \
            decidcap_id_prev, storedrainprm_prev, lai_id_prev, gdd_id_prev, sdd_id_prev, \
            albdectr_id_prev, albevetr_id_prev, albgrass_id_prev, porosity_id_prev, \
            hdd_id_prev, state_id, soilstore_id, soilstorecap, h_maintain, hdd_id_next, \
            porosity_id_next, storedrainprm_next, lai_id_next, gdd_id_next, sdd_id_next, \
            wuday_id)
        
        
        Defined at suews_phys_dailystate.fpp lines 79-337
        
        Parameters
        ----------
        iy : int
        id : int
        it : int
        imin : int
        isec : int
        tstep : int
        tstep_prev : int
        dt_since_start : int
        dayofweek_id : int array
        tmin_id_prev : float
        tmax_id_prev : float
        lenday_id_prev : float
        basetmethod : int
        waterusemethod : int
        ie_start : int
        ie_end : int
        laicalcyes : int
        laitype : int array
        nsh_real : float
        avkdn : float
        temp_c : float
        precip : float
        baset_hc : float
        baset_heating : float array
        baset_cooling : float array
        lat : float
        faut : float
        lai_obs : float
        albmax_dectr : float
        albmax_evetr : float
        albmax_grass : float
        albmin_dectr : float
        albmin_evetr : float
        albmin_grass : float
        capmax_dec : float
        capmin_dec : float
        pormax_dec : float
        pormin_dec : float
        ie_a : float array
        ie_m : float array
        daywatper : float array
        	of houses following daily water
        
        daywat : float array
        baset : float array
        basete : float array
        gddfull : float array
        sddfull : float array
        laimin : float array
        laimax : float array
        laipower : float array
        decidcap_id_prev : float
        storedrainprm_prev : float array
        lai_id_prev : float array
        gdd_id_prev : float array
        sdd_id_prev : float array
        albdectr_id_prev : float
        albevetr_id_prev : float
        albgrass_id_prev : float
        porosity_id_prev : float
        hdd_id_prev : float array
        state_id : float array
        soilstore_id : float array
        soilstorecap : float array
        h_maintain : float
        hdd_id_next : float array
        porosity_id_next : float
        storedrainprm_next : float array
        lai_id_next : float array
        gdd_id_next : float array
        sdd_id_next : float array
        wuday_id : float array
        
        Returns
        -------
        tmin_id_next : float
        tmax_id_next : float
        lenday_id_next : float
        albdectr_id_next : float
        albevetr_id_next : float
        albgrass_id_next : float
        decidcap_id_next : float
        
        """
        tmin_id_next, tmax_id_next, lenday_id_next, albdectr_id_next, albevetr_id_next, \
            albgrass_id_next, decidcap_id_next = \
            _supy_driver.f90wrap_suews_cal_dailystate(iy=iy, id=id, it=it, imin=imin, \
            isec=isec, tstep=tstep, tstep_prev=tstep_prev, \
            dt_since_start=dt_since_start, dayofweek_id=dayofweek_id, \
            tmin_id_prev=tmin_id_prev, tmax_id_prev=tmax_id_prev, \
            lenday_id_prev=lenday_id_prev, basetmethod=basetmethod, \
            waterusemethod=waterusemethod, ie_start=ie_start, ie_end=ie_end, \
            laicalcyes=laicalcyes, laitype=laitype, nsh_real=nsh_real, avkdn=avkdn, \
            temp_c=temp_c, precip=precip, baset_hc=baset_hc, \
            baset_heating=baset_heating, baset_cooling=baset_cooling, lat=lat, \
            faut=faut, lai_obs=lai_obs, albmax_dectr=albmax_dectr, \
            albmax_evetr=albmax_evetr, albmax_grass=albmax_grass, \
            albmin_dectr=albmin_dectr, albmin_evetr=albmin_evetr, \
            albmin_grass=albmin_grass, capmax_dec=capmax_dec, capmin_dec=capmin_dec, \
            pormax_dec=pormax_dec, pormin_dec=pormin_dec, ie_a=ie_a, ie_m=ie_m, \
            daywatper=daywatper, daywat=daywat, baset=baset, basete=basete, \
            gddfull=gddfull, sddfull=sddfull, laimin=laimin, laimax=laimax, \
            laipower=laipower, decidcap_id_prev=decidcap_id_prev, \
            storedrainprm_prev=storedrainprm_prev, lai_id_prev=lai_id_prev, \
            gdd_id_prev=gdd_id_prev, sdd_id_prev=sdd_id_prev, \
            albdectr_id_prev=albdectr_id_prev, albevetr_id_prev=albevetr_id_prev, \
            albgrass_id_prev=albgrass_id_prev, porosity_id_prev=porosity_id_prev, \
            hdd_id_prev=hdd_id_prev, state_id=state_id, soilstore_id=soilstore_id, \
            soilstorecap=soilstorecap, h_maintain=h_maintain, hdd_id_next=hdd_id_next, \
            porosity_id_next=porosity_id_next, storedrainprm_next=storedrainprm_next, \
            lai_id_next=lai_id_next, gdd_id_next=gdd_id_next, sdd_id_next=sdd_id_next, \
            wuday_id=wuday_id)
        return tmin_id_next, tmax_id_next, lenday_id_next, albdectr_id_next, \
            albevetr_id_next, albgrass_id_next, decidcap_id_next
    
    @staticmethod
    def update_dailystate_end(id, it, imin, tstep, dt_since_start, tmin_id, tmax_id, \
        lenday_id, laitype, ie_end, ie_start, laicalcyes, waterusemethod, \
        dayofweek_id, albmax_dectr, albmax_evetr, albmax_grass, albmin_dectr, \
        albmin_evetr, albmin_grass, baset, basete, capmax_dec, capmin_dec, daywat, \
        daywatper, faut, gddfull, ie_a, ie_m, laimax, laimin, laipower, lat, \
        pormax_dec, pormin_dec, sddfull, lai_obs, state_id, soilstore_id, \
        soilstorecap, h_maintain, gdd_id, sdd_id, hdd_id, lai_id, decidcap_id, \
        albdectr_id, albevetr_id, albgrass_id, porosity_id, storedrainprm, \
        wuday_id):
        """
        update_dailystate_end(id, it, imin, tstep, dt_since_start, tmin_id, tmax_id, \
            lenday_id, laitype, ie_end, ie_start, laicalcyes, waterusemethod, \
            dayofweek_id, albmax_dectr, albmax_evetr, albmax_grass, albmin_dectr, \
            albmin_evetr, albmin_grass, baset, basete, capmax_dec, capmin_dec, daywat, \
            daywatper, faut, gddfull, ie_a, ie_m, laimax, laimin, laipower, lat, \
            pormax_dec, pormin_dec, sddfull, lai_obs, state_id, soilstore_id, \
            soilstorecap, h_maintain, gdd_id, sdd_id, hdd_id, lai_id, decidcap_id, \
            albdectr_id, albevetr_id, albgrass_id, porosity_id, storedrainprm, wuday_id)
        
        
        Defined at suews_phys_dailystate.fpp lines 339-452
        
        Parameters
        ----------
        id : int
        it : int
        imin : int
        tstep : int
        dt_since_start : int
        tmin_id : float
        tmax_id : float
        lenday_id : float
        laitype : int array
        ie_end : int
        ie_start : int
        laicalcyes : int
        waterusemethod : int
        dayofweek_id : int array
        albmax_dectr : float
        albmax_evetr : float
        albmax_grass : float
        albmin_dectr : float
        albmin_evetr : float
        albmin_grass : float
        baset : float array
        basete : float array
        capmax_dec : float
        capmin_dec : float
        daywat : float array
        daywatper : float array
        faut : float
        gddfull : float array
        ie_a : float array
        ie_m : float array
        laimax : float array
        laimin : float array
        laipower : float array
        lat : float
        pormax_dec : float
        pormin_dec : float
        sddfull : float array
        lai_obs : float
        state_id : float array
        soilstore_id : float array
        soilstorecap : float array
        h_maintain : float
        gdd_id : float array
        sdd_id : float array
        hdd_id : float array
        lai_id : float array
        decidcap_id : float
        albdectr_id : float
        albevetr_id : float
        albgrass_id : float
        porosity_id : float
        storedrainprm : float array
        wuday_id : float array
        
        ------------------------------------------------------------------------------
         Calculation of LAI from growing degree days
         This was revised and checked on 16 Feb 2014 by LJ
        ------------------------------------------------------------------------------
         save initial LAI_id
        """
        _supy_driver.f90wrap_update_dailystate_end(id=id, it=it, imin=imin, tstep=tstep, \
            dt_since_start=dt_since_start, tmin_id=tmin_id, tmax_id=tmax_id, \
            lenday_id=lenday_id, laitype=laitype, ie_end=ie_end, ie_start=ie_start, \
            laicalcyes=laicalcyes, waterusemethod=waterusemethod, \
            dayofweek_id=dayofweek_id, albmax_dectr=albmax_dectr, \
            albmax_evetr=albmax_evetr, albmax_grass=albmax_grass, \
            albmin_dectr=albmin_dectr, albmin_evetr=albmin_evetr, \
            albmin_grass=albmin_grass, baset=baset, basete=basete, \
            capmax_dec=capmax_dec, capmin_dec=capmin_dec, daywat=daywat, \
            daywatper=daywatper, faut=faut, gddfull=gddfull, ie_a=ie_a, ie_m=ie_m, \
            laimax=laimax, laimin=laimin, laipower=laipower, lat=lat, \
            pormax_dec=pormax_dec, pormin_dec=pormin_dec, sddfull=sddfull, \
            lai_obs=lai_obs, state_id=state_id, soilstore_id=soilstore_id, \
            soilstorecap=soilstorecap, h_maintain=h_maintain, gdd_id=gdd_id, \
            sdd_id=sdd_id, hdd_id=hdd_id, lai_id=lai_id, decidcap_id=decidcap_id, \
            albdectr_id=albdectr_id, albevetr_id=albevetr_id, albgrass_id=albgrass_id, \
            porosity_id=porosity_id, storedrainprm=storedrainprm, wuday_id=wuday_id)
    
    @staticmethod
    def update_dailystate_day(basetmethod, dayofweek_id, avkdn, temp_c, precip, \
        baset_hc, baset_heating, baset_cooling, nsh_real, tmin_id, tmax_id, \
        lenday_id, hdd_id):
        """
        update_dailystate_day(basetmethod, dayofweek_id, avkdn, temp_c, precip, \
            baset_hc, baset_heating, baset_cooling, nsh_real, tmin_id, tmax_id, \
            lenday_id, hdd_id)
        
        
        Defined at suews_phys_dailystate.fpp lines 454-522
        
        Parameters
        ----------
        basetmethod : int
        dayofweek_id : int array
        avkdn : float
        temp_c : float
        precip : float
        baset_hc : float
        baset_heating : float array
        baset_cooling : float array
        nsh_real : float
        tmin_id : float
        tmax_id : float
        lenday_id : float
        hdd_id : float array
        
        """
        _supy_driver.f90wrap_update_dailystate_day(basetmethod=basetmethod, \
            dayofweek_id=dayofweek_id, avkdn=avkdn, temp_c=temp_c, precip=precip, \
            baset_hc=baset_hc, baset_heating=baset_heating, baset_cooling=baset_cooling, \
            nsh_real=nsh_real, tmin_id=tmin_id, tmax_id=tmax_id, lenday_id=lenday_id, \
            hdd_id=hdd_id)
    
    @staticmethod
    def update_veg(laimax, laimin, albmax_dectr, albmax_evetr, albmax_grass, \
        albmin_dectr, albmin_evetr, albmin_grass, capmax_dec, capmin_dec, \
        pormax_dec, pormin_dec, lai_id, lai_id_prev, decidcap_id, albdectr_id, \
        albevetr_id, albgrass_id, porosity_id, storedrainprm):
        """
        update_veg(laimax, laimin, albmax_dectr, albmax_evetr, albmax_grass, \
            albmin_dectr, albmin_evetr, albmin_grass, capmax_dec, capmin_dec, \
            pormax_dec, pormin_dec, lai_id, lai_id_prev, decidcap_id, albdectr_id, \
            albevetr_id, albgrass_id, porosity_id, storedrainprm)
        
        
        Defined at suews_phys_dailystate.fpp lines 524-606
        
        Parameters
        ----------
        laimax : float array
        laimin : float array
        albmax_dectr : float
        albmax_evetr : float
        albmax_grass : float
        albmin_dectr : float
        albmin_evetr : float
        albmin_grass : float
        capmax_dec : float
        capmin_dec : float
        pormax_dec : float
        pormin_dec : float
        lai_id : float array
        lai_id_prev : float array
        decidcap_id : float
        albdectr_id : float
        albevetr_id : float
        albgrass_id : float
        porosity_id : float
        storedrainprm : float array
        
        """
        _supy_driver.f90wrap_update_veg(laimax=laimax, laimin=laimin, \
            albmax_dectr=albmax_dectr, albmax_evetr=albmax_evetr, \
            albmax_grass=albmax_grass, albmin_dectr=albmin_dectr, \
            albmin_evetr=albmin_evetr, albmin_grass=albmin_grass, capmax_dec=capmax_dec, \
            capmin_dec=capmin_dec, pormax_dec=pormax_dec, pormin_dec=pormin_dec, \
            lai_id=lai_id, lai_id_prev=lai_id_prev, decidcap_id=decidcap_id, \
            albdectr_id=albdectr_id, albevetr_id=albevetr_id, albgrass_id=albgrass_id, \
            porosity_id=porosity_id, storedrainprm=storedrainprm)
    
    @staticmethod
    def update_gddlai(id, laicalcyes, lat, lai_obs, tmin_id_prev, tmax_id_prev, \
        lenday_id_prev, baset, basete, gddfull, sddfull, laimin, laimax, laipower, \
        laitype, lai_id_prev, gdd_id, sdd_id, lai_id_next):
        """
        update_gddlai(id, laicalcyes, lat, lai_obs, tmin_id_prev, tmax_id_prev, \
            lenday_id_prev, baset, basete, gddfull, sddfull, laimin, laimax, laipower, \
            laitype, lai_id_prev, gdd_id, sdd_id, lai_id_next)
        
        
        Defined at suews_phys_dailystate.fpp lines 608-744
        
        Parameters
        ----------
        id : int
        laicalcyes : int
        lat : float
        lai_obs : float
        tmin_id_prev : float
        tmax_id_prev : float
        lenday_id_prev : float
        baset : float array
        basete : float array
        gddfull : float array
        sddfull : float array
        laimin : float array
        laimax : float array
        laipower : float array
        laitype : int array
        lai_id_prev : float array
        gdd_id : float array
        sdd_id : float array
        lai_id_next : float array
        
        ------------------------------------------------------------------------------
         Calculation of LAI from growing degree days
         This was revised and checked on 16 Feb 2014 by LJ
        ------------------------------------------------------------------------------
        """
        _supy_driver.f90wrap_update_gddlai(id=id, laicalcyes=laicalcyes, lat=lat, \
            lai_obs=lai_obs, tmin_id_prev=tmin_id_prev, tmax_id_prev=tmax_id_prev, \
            lenday_id_prev=lenday_id_prev, baset=baset, basete=basete, gddfull=gddfull, \
            sddfull=sddfull, laimin=laimin, laimax=laimax, laipower=laipower, \
            laitype=laitype, lai_id_prev=lai_id_prev, gdd_id=gdd_id, sdd_id=sdd_id, \
            lai_id_next=lai_id_next)
    
    @staticmethod
    def update_wateruse(id, waterusemethod, dayofweek_id, lat, frirriauto, hdd_id, \
        state_id, soilstore_id, soilstorecap, h_maintain, ie_a, ie_m, ie_start, \
        ie_end, daywatper, daywat, wuday_id):
        """
        update_wateruse(id, waterusemethod, dayofweek_id, lat, frirriauto, hdd_id, \
            state_id, soilstore_id, soilstorecap, h_maintain, ie_a, ie_m, ie_start, \
            ie_end, daywatper, daywat, wuday_id)
        
        
        Defined at suews_phys_dailystate.fpp lines 746-822
        
        Parameters
        ----------
        id : int
        waterusemethod : int
        dayofweek_id : int array
        lat : float
        frirriauto : float
        hdd_id : float array
        state_id : float array
        soilstore_id : float array
        soilstorecap : float array
        h_maintain : float
        ie_a : float array
        ie_m : float array
        ie_start : int
        ie_end : int
        daywatper : float array
        	of houses following daily water
        
        daywat : float array
        wuday_id : float array
        
        """
        _supy_driver.f90wrap_update_wateruse(id=id, waterusemethod=waterusemethod, \
            dayofweek_id=dayofweek_id, lat=lat, frirriauto=frirriauto, hdd_id=hdd_id, \
            state_id=state_id, soilstore_id=soilstore_id, soilstorecap=soilstorecap, \
            h_maintain=h_maintain, ie_a=ie_a, ie_m=ie_m, ie_start=ie_start, \
            ie_end=ie_end, daywatper=daywatper, daywat=daywat, wuday_id=wuday_id)
    
    @staticmethod
    def update_hdd(dt_since_start, it, imin, tstep, hdd_id):
        """
        update_hdd(dt_since_start, it, imin, tstep, hdd_id)
        
        
        Defined at suews_phys_dailystate.fpp lines 824-850
        
        Parameters
        ----------
        dt_since_start : int
        it : int
        imin : int
        tstep : int
        hdd_id : float array
        
        """
        _supy_driver.f90wrap_update_hdd(dt_since_start=dt_since_start, it=it, imin=imin, \
            tstep=tstep, hdd_id=hdd_id)
    
    @staticmethod
    def update_dailystate_start(it, imin, hdd_id):
        """
        update_dailystate_start(it, imin, hdd_id)
        
        
        Defined at suews_phys_dailystate.fpp lines 852-871
        
        Parameters
        ----------
        it : int
        imin : int
        hdd_id : float array
        
        """
        _supy_driver.f90wrap_update_dailystate_start(it=it, imin=imin, hdd_id=hdd_id)
    
    @staticmethod
    def suews_update_dailystate(id, datetimeline, gridiv, numberofgrids, \
        dailystateline, dataoutdailystate):
        """
        suews_update_dailystate(id, datetimeline, gridiv, numberofgrids, dailystateline, \
            dataoutdailystate)
        
        
        Defined at suews_phys_dailystate.fpp lines 873-887
        
        Parameters
        ----------
        id : int
        datetimeline : float array
        gridiv : int
        numberofgrids : int
        dailystateline : float array
        dataoutdailystate : float array
        
        """
        _supy_driver.f90wrap_suews_update_dailystate(id=id, datetimeline=datetimeline, \
            gridiv=gridiv, numberofgrids=numberofgrids, dailystateline=dailystateline, \
            dataoutdailystate=dataoutdailystate)
    
    @staticmethod
    def update_dailystateline(it, imin, nsh_real, gdd_id, hdd_id, lai_id, sdd_id, \
        tmin_id, tmax_id, lenday_id, decidcap_id, albdectr_id, albevetr_id, \
        albgrass_id, porosity_id, wuday_id, vegphenlumps, snowalb, snowdens, a1, a2, \
        a3, dailystateline):
        """
        update_dailystateline(it, imin, nsh_real, gdd_id, hdd_id, lai_id, sdd_id, \
            tmin_id, tmax_id, lenday_id, decidcap_id, albdectr_id, albevetr_id, \
            albgrass_id, porosity_id, wuday_id, vegphenlumps, snowalb, snowdens, a1, a2, \
            a3, dailystateline)
        
        
        Defined at suews_phys_dailystate.fpp lines 904-949
        
        Parameters
        ----------
        it : int
        imin : int
        nsh_real : float
        gdd_id : float array
        hdd_id : float array
        lai_id : float array
        sdd_id : float array
        tmin_id : float
        tmax_id : float
        lenday_id : float
        decidcap_id : float
        albdectr_id : float
        albevetr_id : float
        albgrass_id : float
        porosity_id : float
        wuday_id : float array
        vegphenlumps : float
        snowalb : float
        snowdens : float array
        a1 : float
        a2 : float
        a3 : float
        dailystateline : float array
        
        """
        _supy_driver.f90wrap_update_dailystateline(it=it, imin=imin, nsh_real=nsh_real, \
            gdd_id=gdd_id, hdd_id=hdd_id, lai_id=lai_id, sdd_id=sdd_id, tmin_id=tmin_id, \
            tmax_id=tmax_id, lenday_id=lenday_id, decidcap_id=decidcap_id, \
            albdectr_id=albdectr_id, albevetr_id=albevetr_id, albgrass_id=albgrass_id, \
            porosity_id=porosity_id, wuday_id=wuday_id, vegphenlumps=vegphenlumps, \
            snowalb=snowalb, snowdens=snowdens, a1=a1, a2=a2, a3=a3, \
            dailystateline=dailystateline)
    
    _dt_array_initialisers = []
    

dailystate_module = Dailystate_Module()

class Anemsn_Module(f90wrap.runtime.FortranModule):
    """
    Module anemsn_module
    
    
    Defined at suews_phys_anemsn.fpp lines 5-282
    
    """
    @staticmethod
    def anthropogenicemissions(co2pointsource, emissionsmethod, it, imin, dls, \
        dayofweek_id, ef_umolco2perj, fcef_v_kgkm, enef_v_jkm, trafficunits, \
        frfossilfuel_heat, frfossilfuel_nonheat, minfcmetab, maxfcmetab, minqfmetab, \
        maxqfmetab, popdensdaytime, popdensnighttime, temp_c, hdd_id, qf_a, qf_b, \
        qf_c, ah_min, ah_slope_heating, ah_slope_cooling, baset_heating, \
        baset_cooling, trafficrate, qf0_beu, ahprof_24hr, humactivity_24hr, \
        traffprof_24hr, popprof_24hr, surfacearea):
        """
        qf_sahp, fc_anthro, fc_metab, fc_traff, fc_build, fc_point = \
            anthropogenicemissions(co2pointsource, emissionsmethod, it, imin, dls, \
            dayofweek_id, ef_umolco2perj, fcef_v_kgkm, enef_v_jkm, trafficunits, \
            frfossilfuel_heat, frfossilfuel_nonheat, minfcmetab, maxfcmetab, minqfmetab, \
            maxqfmetab, popdensdaytime, popdensnighttime, temp_c, hdd_id, qf_a, qf_b, \
            qf_c, ah_min, ah_slope_heating, ah_slope_cooling, baset_heating, \
            baset_cooling, trafficrate, qf0_beu, ahprof_24hr, humactivity_24hr, \
            traffprof_24hr, popprof_24hr, surfacearea)
        
        
        Defined at suews_phys_anemsn.fpp lines 43-281
        
        Parameters
        ----------
        co2pointsource : float
        emissionsmethod : int
        it : int
        imin : int
        dls : int
        dayofweek_id : int array
        ef_umolco2perj : float
        fcef_v_kgkm : float array
        enef_v_jkm : float
        trafficunits : float
        frfossilfuel_heat : float
        frfossilfuel_nonheat : float
        minfcmetab : float
        maxfcmetab : float
        minqfmetab : float
        maxqfmetab : float
        popdensdaytime : float array
        popdensnighttime : float
        temp_c : float
        hdd_id : float array
        qf_a : float array
        qf_b : float array
        qf_c : float array
        ah_min : float array
        ah_slope_heating : float array
        ah_slope_cooling : float array
        baset_heating : float array
        baset_cooling : float array
        trafficrate : float array
        qf0_beu : float array
        ahprof_24hr : float array
        humactivity_24hr : float array
        traffprof_24hr : float array
        popprof_24hr : float array
        surfacearea : float
        
        Returns
        -------
        qf_sahp : float
        fc_anthro : float
        fc_metab : float
        fc_traff : float
        fc_build : float
        fc_point : float
        
        -----------------------------------------------------------------------
         Account for Daylight saving
        """
        qf_sahp, fc_anthro, fc_metab, fc_traff, fc_build, fc_point = \
            _supy_driver.f90wrap_anthropogenicemissions(co2pointsource=co2pointsource, \
            emissionsmethod=emissionsmethod, it=it, imin=imin, dls=dls, \
            dayofweek_id=dayofweek_id, ef_umolco2perj=ef_umolco2perj, \
            fcef_v_kgkm=fcef_v_kgkm, enef_v_jkm=enef_v_jkm, trafficunits=trafficunits, \
            frfossilfuel_heat=frfossilfuel_heat, \
            frfossilfuel_nonheat=frfossilfuel_nonheat, minfcmetab=minfcmetab, \
            maxfcmetab=maxfcmetab, minqfmetab=minqfmetab, maxqfmetab=maxqfmetab, \
            popdensdaytime=popdensdaytime, popdensnighttime=popdensnighttime, \
            temp_c=temp_c, hdd_id=hdd_id, qf_a=qf_a, qf_b=qf_b, qf_c=qf_c, \
            ah_min=ah_min, ah_slope_heating=ah_slope_heating, \
            ah_slope_cooling=ah_slope_cooling, baset_heating=baset_heating, \
            baset_cooling=baset_cooling, trafficrate=trafficrate, qf0_beu=qf0_beu, \
            ahprof_24hr=ahprof_24hr, humactivity_24hr=humactivity_24hr, \
            traffprof_24hr=traffprof_24hr, popprof_24hr=popprof_24hr, \
            surfacearea=surfacearea)
        return qf_sahp, fc_anthro, fc_metab, fc_traff, fc_build, fc_point
    
    _dt_array_initialisers = []
    

anemsn_module = Anemsn_Module()

class Rsl_Module(f90wrap.runtime.FortranModule):
    """
    Module rsl_module
    
    
    Defined at suews_phys_rslprof.fpp lines 5-984
    
    """
    @staticmethod
    def rslprofile(diagmethod, zh, z0m, zdm, z0v, l_mod, sfr_surf, fai, pai, \
        stabilitymethod, ra_h, avcp, lv_j_kg, avdens, avu1, temp_c, avrh, press_hpa, \
        zmeas, qh, qe, dataoutlinersl):
        """
        t2_c, q2_gkg, u10_ms, rh2 = rslprofile(diagmethod, zh, z0m, zdm, z0v, l_mod, \
            sfr_surf, fai, pai, stabilitymethod, ra_h, avcp, lv_j_kg, avdens, avu1, \
            temp_c, avrh, press_hpa, zmeas, qh, qe, dataoutlinersl)
        
        
        Defined at suews_phys_rslprof.fpp lines 22-328
        
        Parameters
        ----------
        diagmethod : int
        zh : float
        z0m : float
        zdm : float
        z0v : float
        l_mod : float
        sfr_surf : float array
        fai : float
        pai : float
        stabilitymethod : int
        ra_h : float
        avcp : float
        lv_j_kg : float
        avdens : float
        avu1 : float
        temp_c : float
        avrh : float
        press_hpa : float
        zmeas : float
        qh : float
        qe : float
        dataoutlinersl : float array
        
        Returns
        -------
        t2_c : float
        q2_gkg : float
        u10_ms : float
        rh2 : float
        
        -----------------------------------------------------
         calculates windprofiles using MOST with a RSL-correction
         based on Harman & Finnigan 2007
         last modified by:
         NT 16 Mar 2019: initial version
         TS 16 Oct 2019: improved consistency in parameters/varaibles within SUEWS
         TODO how to improve the speed of this code
        -----------------------------------------------------
        """
        t2_c, q2_gkg, u10_ms, rh2 = \
            _supy_driver.f90wrap_rslprofile(diagmethod=diagmethod, zh=zh, z0m=z0m, \
            zdm=zdm, z0v=z0v, l_mod=l_mod, sfr_surf=sfr_surf, fai=fai, pai=pai, \
            stabilitymethod=stabilitymethod, ra_h=ra_h, avcp=avcp, lv_j_kg=lv_j_kg, \
            avdens=avdens, avu1=avu1, temp_c=temp_c, avrh=avrh, press_hpa=press_hpa, \
            zmeas=zmeas, qh=qh, qe=qe, dataoutlinersl=dataoutlinersl)
        return t2_c, q2_gkg, u10_ms, rh2
    
    @staticmethod
    def interp_z(z_x, z, v):
        """
        v_x = interp_z(z_x, z, v)
        
        
        Defined at suews_phys_rslprof.fpp lines 330-359
        
        Parameters
        ----------
        z_x : float
        z : float array
        v : float array
        
        Returns
        -------
        v_x : float
        
        """
        v_x = _supy_driver.f90wrap_interp_z(z_x=z_x, z=z, v=v)
        return v_x
    
    @staticmethod
    def cal_elm_rsl(beta, lc):
        """
        elm = cal_elm_rsl(beta, lc)
        
        
        Defined at suews_phys_rslprof.fpp lines 361-371
        
        Parameters
        ----------
        beta : float
        lc : float
        
        Returns
        -------
        elm : float
        
        """
        elm = _supy_driver.f90wrap_cal_elm_rsl(beta=beta, lc=lc)
        return elm
    
    @staticmethod
    def cal_psim_hat(stabilitymethod, psihatm_top, psihatm_mid, z_top, z_mid, z_btm, \
        cm, c2, zh_rsl, zd_rsl, l_mod, beta, elm, lc):
        """
        psihatm_btm = cal_psim_hat(stabilitymethod, psihatm_top, psihatm_mid, z_top, \
            z_mid, z_btm, cm, c2, zh_rsl, zd_rsl, l_mod, beta, elm, lc)
        
        
        Defined at suews_phys_rslprof.fpp lines 373-438
        
        Parameters
        ----------
        stabilitymethod : int
        psihatm_top : float
        psihatm_mid : float
        z_top : float
        z_mid : float
        z_btm : float
        cm : float
        c2 : float
        zh_rsl : float
        zd_rsl : float
        l_mod : float
        beta : float
        elm : float
        lc : float
        
        Returns
        -------
        psihatm_btm : float
        
        """
        psihatm_btm = _supy_driver.f90wrap_cal_psim_hat(stabilitymethod=stabilitymethod, \
            psihatm_top=psihatm_top, psihatm_mid=psihatm_mid, z_top=z_top, z_mid=z_mid, \
            z_btm=z_btm, cm=cm, c2=c2, zh_rsl=zh_rsl, zd_rsl=zd_rsl, l_mod=l_mod, \
            beta=beta, elm=elm, lc=lc)
        return psihatm_btm
    
    @staticmethod
    def cal_psih_hat(stabilitymethod, psihath_top, psihath_mid, z_top, z_mid, z_btm, \
        ch, c2h, zh_rsl, zd_rsl, l_mod, beta, elm, lc):
        """
        psihath_btm = cal_psih_hat(stabilitymethod, psihath_top, psihath_mid, z_top, \
            z_mid, z_btm, ch, c2h, zh_rsl, zd_rsl, l_mod, beta, elm, lc)
        
        
        Defined at suews_phys_rslprof.fpp lines 440-501
        
        Parameters
        ----------
        stabilitymethod : int
        psihath_top : float
        psihath_mid : float
        z_top : float
        z_mid : float
        z_btm : float
        ch : float
        c2h : float
        zh_rsl : float
        zd_rsl : float
        l_mod : float
        beta : float
        elm : float
        lc : float
        
        Returns
        -------
        psihath_btm : float
        
        """
        psihath_btm = _supy_driver.f90wrap_cal_psih_hat(stabilitymethod=stabilitymethod, \
            psihath_top=psihath_top, psihath_mid=psihath_mid, z_top=z_top, z_mid=z_mid, \
            z_btm=z_btm, ch=ch, c2h=c2h, zh_rsl=zh_rsl, zd_rsl=zd_rsl, l_mod=l_mod, \
            beta=beta, elm=elm, lc=lc)
        return psihath_btm
    
    @staticmethod
    def cal_phim_hat(stabilitymethod, z, zh_rsl, l_mod, beta, lc):
        """
        phim_hat = cal_phim_hat(stabilitymethod, z, zh_rsl, l_mod, beta, lc)
        
        
        Defined at suews_phys_rslprof.fpp lines 503-519
        
        Parameters
        ----------
        stabilitymethod : int
        z : float
        zh_rsl : float
        l_mod : float
        beta : float
        lc : float
        
        Returns
        -------
        phim_hat : float
        
        """
        phim_hat = _supy_driver.f90wrap_cal_phim_hat(stabilitymethod=stabilitymethod, \
            z=z, zh_rsl=zh_rsl, l_mod=l_mod, beta=beta, lc=lc)
        return phim_hat
    
    @staticmethod
    def cal_cm(stabilitymethod, zh_rsl, zd_rsl, lc, beta, l_mod):
        """
        c2, cm = cal_cm(stabilitymethod, zh_rsl, zd_rsl, lc, beta, l_mod)
        
        
        Defined at suews_phys_rslprof.fpp lines 521-562
        
        Parameters
        ----------
        stabilitymethod : int
        zh_rsl : float
        zd_rsl : float
        lc : float
        beta : float
        l_mod : float
        
        Returns
        -------
        c2 : float
        cm : float
        
        """
        c2, cm = _supy_driver.f90wrap_cal_cm(stabilitymethod=stabilitymethod, \
            zh_rsl=zh_rsl, zd_rsl=zd_rsl, lc=lc, beta=beta, l_mod=l_mod)
        return c2, cm
    
    @staticmethod
    def cal_ch(stabilitymethod, zh_rsl, zd_rsl, lc, beta, l_mod, scc, f):
        """
        c2h, ch = cal_ch(stabilitymethod, zh_rsl, zd_rsl, lc, beta, l_mod, scc, f)
        
        
        Defined at suews_phys_rslprof.fpp lines 564-604
        
        Parameters
        ----------
        stabilitymethod : int
        zh_rsl : float
        zd_rsl : float
        lc : float
        beta : float
        l_mod : float
        scc : float
        f : float
        
        Returns
        -------
        c2h : float
        ch : float
        
        """
        c2h, ch = _supy_driver.f90wrap_cal_ch(stabilitymethod=stabilitymethod, \
            zh_rsl=zh_rsl, zd_rsl=zd_rsl, lc=lc, beta=beta, l_mod=l_mod, scc=scc, f=f)
        return c2h, ch
    
    @staticmethod
    def cal_zd_rsl(zh_rsl, beta, lc):
        """
        zd_rsl = cal_zd_rsl(zh_rsl, beta, lc)
        
        
        Defined at suews_phys_rslprof.fpp lines 730-738
        
        Parameters
        ----------
        zh_rsl : float
        beta : float
        lc : float
        
        Returns
        -------
        zd_rsl : float
        
        """
        zd_rsl = _supy_driver.f90wrap_cal_zd_rsl(zh_rsl=zh_rsl, beta=beta, lc=lc)
        return zd_rsl
    
    @staticmethod
    def cal_z0_rsl(stabilitymethod, zh_rsl, zd_rsl, beta, l_mod_rsl, psihatm_zh):
        """
        z0_rsl = cal_z0_rsl(stabilitymethod, zh_rsl, zd_rsl, beta, l_mod_rsl, \
            psihatm_zh)
        
        
        Defined at suews_phys_rslprof.fpp lines 740-777
        
        Parameters
        ----------
        stabilitymethod : int
        zh_rsl : float
        zd_rsl : float
        beta : float
        l_mod_rsl : float
        psihatm_zh : float
        
        Returns
        -------
        z0_rsl : float
        
        """
        z0_rsl = _supy_driver.f90wrap_cal_z0_rsl(stabilitymethod=stabilitymethod, \
            zh_rsl=zh_rsl, zd_rsl=zd_rsl, beta=beta, l_mod_rsl=l_mod_rsl, \
            psihatm_zh=psihatm_zh)
        return z0_rsl
    
    @staticmethod
    def rsl_cal_prms(stabilitymethod, nz_above, z_array, zh, l_mod, sfr_surf, fai, \
        pai, psihatm_array, psihath_array):
        """
        zh_rsl, l_mod_rsl, lc, beta, zd_rsl, z0_rsl, elm, scc, fx = \
            rsl_cal_prms(stabilitymethod, nz_above, z_array, zh, l_mod, sfr_surf, fai, \
            pai, psihatm_array, psihath_array)
        
        
        Defined at suews_phys_rslprof.fpp lines 779-915
        
        Parameters
        ----------
        stabilitymethod : int
        nz_above : int
        z_array : float array
        zh : float
        l_mod : float
        sfr_surf : float array
        fai : float
        pai : float
        psihatm_array : float array
        psihath_array : float array
        
        Returns
        -------
        zh_rsl : float
        l_mod_rsl : float
        lc : float
        beta : float
        zd_rsl : float
        z0_rsl : float
        elm : float
        scc : float
        fx : float
        
        """
        zh_rsl, l_mod_rsl, lc, beta, zd_rsl, z0_rsl, elm, scc, fx = \
            _supy_driver.f90wrap_rsl_cal_prms(stabilitymethod=stabilitymethod, \
            nz_above=nz_above, z_array=z_array, zh=zh, l_mod=l_mod, sfr_surf=sfr_surf, \
            fai=fai, pai=pai, psihatm_array=psihatm_array, psihath_array=psihath_array)
        return zh_rsl, l_mod_rsl, lc, beta, zd_rsl, z0_rsl, elm, scc, fx
    
    @staticmethod
    def cal_beta_rsl(stabilitymethod, pai, sfr_tr, lc_over_l):
        """
        beta = cal_beta_rsl(stabilitymethod, pai, sfr_tr, lc_over_l)
        
        
        Defined at suews_phys_rslprof.fpp lines 917-954
        
        Parameters
        ----------
        stabilitymethod : int
        pai : float
        sfr_tr : float
        lc_over_l : float
        
        Returns
        -------
        beta : float
        
        """
        beta = _supy_driver.f90wrap_cal_beta_rsl(stabilitymethod=stabilitymethod, \
            pai=pai, sfr_tr=sfr_tr, lc_over_l=lc_over_l)
        return beta
    
    @staticmethod
    def cal_beta_lc(stabilitymethod, beta0, lc_over_l):
        """
        beta_x = cal_beta_lc(stabilitymethod, beta0, lc_over_l)
        
        
        Defined at suews_phys_rslprof.fpp lines 956-983
        
        Parameters
        ----------
        stabilitymethod : int
        beta0 : float
        lc_over_l : float
        
        Returns
        -------
        beta_x : float
        
        """
        beta_x = _supy_driver.f90wrap_cal_beta_lc(stabilitymethod=stabilitymethod, \
            beta0=beta0, lc_over_l=lc_over_l)
        return beta_x
    
    @property
    def nz(self):
        """
        Element nz ftype=integer pytype=int
        
        
        Defined at suews_phys_rslprof.fpp line 12
        
        """
        return _supy_driver.f90wrap_rsl_module__get__nz()
    
    def __str__(self):
        ret = ['<rsl_module>{\n']
        ret.append('    nz : ')
        ret.append(repr(self.nz))
        ret.append('}')
        return ''.join(ret)
    
    _dt_array_initialisers = []
    

rsl_module = Rsl_Module()

class Meteo(f90wrap.runtime.FortranModule):
    """
    Module meteo
    
    
    Defined at suews_util_meteo.fpp lines 6-446
    
    """
    @staticmethod
    def sat_vap_press(tk, p):
        """
        es = sat_vap_press(tk, p)
        
        
        Defined at suews_util_meteo.fpp lines 25-38
        
        Parameters
        ----------
        tk : float
        p : float
        
        Returns
        -------
        es : float
        
        """
        es = _supy_driver.f90wrap_sat_vap_press(tk=tk, p=p)
        return es
    
    @staticmethod
    def sos_dryair(tk):
        """
        sos_dryair = sos_dryair(tk)
        
        
        Defined at suews_util_meteo.fpp lines 40-43
        
        Parameters
        ----------
        tk : float
        
        Returns
        -------
        sos_dryair : float
        
        """
        sos_dryair = _supy_driver.f90wrap_sos_dryair(tk=tk)
        return sos_dryair
    
    @staticmethod
    def potential_temp(tk, p):
        """
        potential_temp = potential_temp(tk, p)
        
        
        Defined at suews_util_meteo.fpp lines 46-50
        
        Parameters
        ----------
        tk : float
        p : float
        
        Returns
        -------
        potential_temp : float
        
        """
        potential_temp = _supy_driver.f90wrap_potential_temp(tk=tk, p=p)
        return potential_temp
    
    @staticmethod
    def latentheat_v(tk):
        """
        latentheat_v = latentheat_v(tk)
        
        
        Defined at suews_util_meteo.fpp lines 52-56
        
        Parameters
        ----------
        tk : float
        
        Returns
        -------
        latentheat_v : float
        
        """
        latentheat_v = _supy_driver.f90wrap_latentheat_v(tk=tk)
        return latentheat_v
    
    @staticmethod
    def latentheat_m(tk):
        """
        latentheat_m = latentheat_m(tk)
        
        
        Defined at suews_util_meteo.fpp lines 58-63
        
        Parameters
        ----------
        tk : float
        
        Returns
        -------
        latentheat_m : float
        
        """
        latentheat_m = _supy_driver.f90wrap_latentheat_m(tk=tk)
        return latentheat_m
    
    @staticmethod
    def spec_heat_dryair(tk):
        """
        spec_heat_dryair = spec_heat_dryair(tk)
        
        
        Defined at suews_util_meteo.fpp lines 65-69
        
        Parameters
        ----------
        tk : float
        
        Returns
        -------
        spec_heat_dryair : float
        
        """
        spec_heat_dryair = _supy_driver.f90wrap_spec_heat_dryair(tk=tk)
        return spec_heat_dryair
    
    @staticmethod
    def spec_heat_vapor(tk, rh):
        """
        spec_heat_vapor = spec_heat_vapor(tk, rh)
        
        
        Defined at suews_util_meteo.fpp lines 71-75
        
        Parameters
        ----------
        tk : float
        rh : float
        
        Returns
        -------
        spec_heat_vapor : float
        
        """
        spec_heat_vapor = _supy_driver.f90wrap_spec_heat_vapor(tk=tk, rh=rh)
        return spec_heat_vapor
    
    @staticmethod
    def heatcapacity_air(tk, rh, p):
        """
        heatcapacity_air = heatcapacity_air(tk, rh, p)
        
        
        Defined at suews_util_meteo.fpp lines 77-85
        
        Parameters
        ----------
        tk : float
        rh : float
        p : float
        
        Returns
        -------
        heatcapacity_air : float
        
        """
        heatcapacity_air = _supy_driver.f90wrap_heatcapacity_air(tk=tk, rh=rh, p=p)
        return heatcapacity_air
    
    @staticmethod
    def density_moist(tvk, p):
        """
        density_moist = density_moist(tvk, p)
        
        
        Defined at suews_util_meteo.fpp lines 87-92
        
        Parameters
        ----------
        tvk : float
        p : float
        
        Returns
        -------
        density_moist : float
        
        """
        density_moist = _supy_driver.f90wrap_density_moist(tvk=tvk, p=p)
        return density_moist
    
    @staticmethod
    def density_vapor(tk, rh, p):
        """
        density_vapor = density_vapor(tk, rh, p)
        
        
        Defined at suews_util_meteo.fpp lines 94-98
        
        Parameters
        ----------
        tk : float
        rh : float
        p : float
        
        Returns
        -------
        density_vapor : float
        
        """
        density_vapor = _supy_driver.f90wrap_density_vapor(tk=tk, rh=rh, p=p)
        return density_vapor
    
    @staticmethod
    def density_dryair(tk, p):
        """
        density_dryair = density_dryair(tk, p)
        
        
        Defined at suews_util_meteo.fpp lines 100-102
        
        Parameters
        ----------
        tk : float
        p : float
        
        Returns
        -------
        density_dryair : float
        
        """
        density_dryair = _supy_driver.f90wrap_density_dryair(tk=tk, p=p)
        return density_dryair
    
    @staticmethod
    def density_gas(tk, pp, molmass):
        """
        density_gas = density_gas(tk, pp, molmass)
        
        
        Defined at suews_util_meteo.fpp lines 104-107
        
        Parameters
        ----------
        tk : float
        pp : float
        molmass : float
        
        Returns
        -------
        density_gas : float
        
        """
        density_gas = _supy_driver.f90wrap_density_gas(tk=tk, pp=pp, molmass=molmass)
        return density_gas
    
    @staticmethod
    def partial_pressure(tk, n):
        """
        partial_pressure = partial_pressure(tk, n)
        
        
        Defined at suews_util_meteo.fpp lines 109-112
        
        Parameters
        ----------
        tk : float
        n : float
        
        Returns
        -------
        partial_pressure : float
        
        """
        partial_pressure = _supy_driver.f90wrap_partial_pressure(tk=tk, n=n)
        return partial_pressure
    
    @staticmethod
    def scale_height(tk):
        """
        scale_height = scale_height(tk)
        
        
        Defined at suews_util_meteo.fpp lines 114-117
        
        Parameters
        ----------
        tk : float
        
        Returns
        -------
        scale_height : float
        
        """
        scale_height = _supy_driver.f90wrap_scale_height(tk=tk)
        return scale_height
    
    @staticmethod
    def vaisala_brunt_f(tk):
        """
        vaisala_brunt_f = vaisala_brunt_f(tk)
        
        
        Defined at suews_util_meteo.fpp lines 119-122
        
        Parameters
        ----------
        tk : float
        
        Returns
        -------
        vaisala_brunt_f : float
        
        """
        vaisala_brunt_f = _supy_driver.f90wrap_vaisala_brunt_f(tk=tk)
        return vaisala_brunt_f
    
    @staticmethod
    def sat_vap_press_x(temp_c, press_hpa, from_, dectime):
        """
        es_hpa = sat_vap_press_x(temp_c, press_hpa, from_, dectime)
        
        
        Defined at suews_util_meteo.fpp lines 132-165
        
        Parameters
        ----------
        temp_c : float
        press_hpa : float
        from_ : int
        dectime : float
        
        Returns
        -------
        es_hpa : float
        
        """
        es_hpa = _supy_driver.f90wrap_sat_vap_press_x(temp_c=temp_c, \
            press_hpa=press_hpa, from_=from_, dectime=dectime)
        return es_hpa
    
    @staticmethod
    def sat_vap_pressice(temp_c, press_hpa, from_, dectime):
        """
        es_hpa = sat_vap_pressice(temp_c, press_hpa, from_, dectime)
        
        
        Defined at suews_util_meteo.fpp lines 167-192
        
        Parameters
        ----------
        temp_c : float
        press_hpa : float
        from_ : int
        dectime : float
        
        Returns
        -------
        es_hpa : float
        
        """
        es_hpa = _supy_driver.f90wrap_sat_vap_pressice(temp_c=temp_c, \
            press_hpa=press_hpa, from_=from_, dectime=dectime)
        return es_hpa
    
    @staticmethod
    def spec_hum_def(vpd_hpa, press_hpa):
        """
        dq = spec_hum_def(vpd_hpa, press_hpa)
        
        
        Defined at suews_util_meteo.fpp lines 197-202
        
        Parameters
        ----------
        vpd_hpa : float
        press_hpa : float
        
        Returns
        -------
        dq : float
        
        """
        dq = _supy_driver.f90wrap_spec_hum_def(vpd_hpa=vpd_hpa, press_hpa=press_hpa)
        return dq
    
    @staticmethod
    def spec_heat_beer(temp_c, rh, rho_v, rho_d):
        """
        cp = spec_heat_beer(temp_c, rh, rho_v, rho_d)
        
        
        Defined at suews_util_meteo.fpp lines 205-223
        
        Parameters
        ----------
        temp_c : float
        rh : float
        rho_v : float
        rho_d : float
        
        Returns
        -------
        cp : float
        
        -------------------------------------------------------------------------------
         USE defaultnotUsed
        """
        cp = _supy_driver.f90wrap_spec_heat_beer(temp_c=temp_c, rh=rh, rho_v=rho_v, \
            rho_d=rho_d)
        return cp
    
    @staticmethod
    def lat_vap(temp_c, ea_hpa, press_hpa, cp, dectime):
        """
        lv_j_kg = lat_vap(temp_c, ea_hpa, press_hpa, cp, dectime)
        
        
        Defined at suews_util_meteo.fpp lines 229-280
        
        Parameters
        ----------
        temp_c : float
        ea_hpa : float
        press_hpa : float
        cp : float
        dectime : float
        
        Returns
        -------
        lv_j_kg : float
        
        """
        lv_j_kg = _supy_driver.f90wrap_lat_vap(temp_c=temp_c, ea_hpa=ea_hpa, \
            press_hpa=press_hpa, cp=cp, dectime=dectime)
        return lv_j_kg
    
    @staticmethod
    def lat_vapsublim(temp_c, ea_hpa, press_hpa, cp):
        """
        lvs_j_kg = lat_vapsublim(temp_c, ea_hpa, press_hpa, cp)
        
        
        Defined at suews_util_meteo.fpp lines 282-321
        
        Parameters
        ----------
        temp_c : float
        ea_hpa : float
        press_hpa : float
        cp : float
        
        Returns
        -------
        lvs_j_kg : float
        
        """
        lvs_j_kg = _supy_driver.f90wrap_lat_vapsublim(temp_c=temp_c, ea_hpa=ea_hpa, \
            press_hpa=press_hpa, cp=cp)
        return lvs_j_kg
    
    @staticmethod
    def psyc_const(cp, press_hpa, lv_j_kg):
        """
        psyc_hpa = psyc_const(cp, press_hpa, lv_j_kg)
        
        
        Defined at suews_util_meteo.fpp lines 327-343
        
        Parameters
        ----------
        cp : float
        press_hpa : float
        lv_j_kg : float
        
        Returns
        -------
        psyc_hpa : float
        
        """
        psyc_hpa = _supy_driver.f90wrap_psyc_const(cp=cp, press_hpa=press_hpa, \
            lv_j_kg=lv_j_kg)
        return psyc_hpa
    
    @staticmethod
    def dewpoint(ea_hpa):
        """
        temp_c_dew = dewpoint(ea_hpa)
        
        
        Defined at suews_util_meteo.fpp lines 346-353
        
        Parameters
        ----------
        ea_hpa : float
        
        Returns
        -------
        temp_c_dew : float
        
        """
        temp_c_dew = _supy_driver.f90wrap_dewpoint(ea_hpa=ea_hpa)
        return temp_c_dew
    
    @staticmethod
    def slope_svp(temp_c):
        """
        s_hpa = slope_svp(temp_c)
        
        
        Defined at suews_util_meteo.fpp lines 356-376
        
        Parameters
        ----------
        temp_c : float
        
        Returns
        -------
        s_hpa : float
        
        """
        s_hpa = _supy_driver.f90wrap_slope_svp(temp_c=temp_c)
        return s_hpa
    
    @staticmethod
    def slopeice_svp(temp_c):
        """
        s_hpa = slopeice_svp(temp_c)
        
        
        Defined at suews_util_meteo.fpp lines 379-394
        
        Parameters
        ----------
        temp_c : float
        
        Returns
        -------
        s_hpa : float
        
        """
        s_hpa = _supy_driver.f90wrap_slopeice_svp(temp_c=temp_c)
        return s_hpa
    
    @staticmethod
    def qsatf(t, pmb):
        """
        qsat = qsatf(t, pmb)
        
        
        Defined at suews_util_meteo.fpp lines 397-413
        
        Parameters
        ----------
        t : float
        pmb : float
        
        Returns
        -------
        qsat : float
        
        """
        qsat = _supy_driver.f90wrap_qsatf(t=t, pmb=pmb)
        return qsat
    
    @staticmethod
    def rh2qa(rh_dec, pres_hpa, ta_degc):
        """
        qa_gkg = rh2qa(rh_dec, pres_hpa, ta_degc)
        
        
        Defined at suews_util_meteo.fpp lines 415-427
        
        Parameters
        ----------
        rh_dec : float
        pres_hpa : float
        ta_degc : float
        
        Returns
        -------
        qa_gkg : float
        
        """
        qa_gkg = _supy_driver.f90wrap_rh2qa(rh_dec=rh_dec, pres_hpa=pres_hpa, \
            ta_degc=ta_degc)
        return qa_gkg
    
    @staticmethod
    def qa2rh(qa_gkg, pres_hpa, ta_degc):
        """
        rh = qa2rh(qa_gkg, pres_hpa, ta_degc)
        
        
        Defined at suews_util_meteo.fpp lines 429-446
        
        Parameters
        ----------
        qa_gkg : float
        pres_hpa : float
        ta_degc : float
        
        Returns
        -------
        rh : float
        
        """
        rh = _supy_driver.f90wrap_qa2rh(qa_gkg=qa_gkg, pres_hpa=pres_hpa, \
            ta_degc=ta_degc)
        return rh
    
    @property
    def rad2deg(self):
        """
        Element rad2deg ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 10
        
        """
        return _supy_driver.f90wrap_meteo__get__rad2deg()
    
    @property
    def deg2rad(self):
        """
        Element deg2rad ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 11
        
        """
        return _supy_driver.f90wrap_meteo__get__deg2rad()
    
    @property
    def molmass_air(self):
        """
        Element molmass_air ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 12
        
        """
        return _supy_driver.f90wrap_meteo__get__molmass_air()
    
    @property
    def molmass_co2(self):
        """
        Element molmass_co2 ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 13
        
        """
        return _supy_driver.f90wrap_meteo__get__molmass_co2()
    
    @property
    def molmass_h2o(self):
        """
        Element molmass_h2o ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 14
        
        """
        return _supy_driver.f90wrap_meteo__get__molmass_h2o()
    
    @property
    def mu_h2o(self):
        """
        Element mu_h2o ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 15
        
        """
        return _supy_driver.f90wrap_meteo__get__mu_h2o()
    
    @property
    def mu_co2(self):
        """
        Element mu_co2 ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 16
        
        """
        return _supy_driver.f90wrap_meteo__get__mu_co2()
    
    @property
    def r_dry_mol(self):
        """
        Element r_dry_mol ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 17
        
        """
        return _supy_driver.f90wrap_meteo__get__r_dry_mol()
    
    @property
    def r_dry_mass(self):
        """
        Element r_dry_mass ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 18
        
        """
        return _supy_driver.f90wrap_meteo__get__r_dry_mass()
    
    @property
    def epsil(self):
        """
        Element epsil ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 20
        
        """
        return _supy_driver.f90wrap_meteo__get__epsil()
    
    @property
    def kb(self):
        """
        Element kb ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 21
        
        """
        return _supy_driver.f90wrap_meteo__get__kb()
    
    @property
    def avogadro(self):
        """
        Element avogadro ftype=real(kind(1d0) pytype=float
        
        
        Defined at suews_util_meteo.fpp line 22
        
        """
        return _supy_driver.f90wrap_meteo__get__avogadro()
    
    def __str__(self):
        ret = ['<meteo>{\n']
        ret.append('    rad2deg : ')
        ret.append(repr(self.rad2deg))
        ret.append(',\n    deg2rad : ')
        ret.append(repr(self.deg2rad))
        ret.append(',\n    molmass_air : ')
        ret.append(repr(self.molmass_air))
        ret.append(',\n    molmass_co2 : ')
        ret.append(repr(self.molmass_co2))
        ret.append(',\n    molmass_h2o : ')
        ret.append(repr(self.molmass_h2o))
        ret.append(',\n    mu_h2o : ')
        ret.append(repr(self.mu_h2o))
        ret.append(',\n    mu_co2 : ')
        ret.append(repr(self.mu_co2))
        ret.append(',\n    r_dry_mol : ')
        ret.append(repr(self.r_dry_mol))
        ret.append(',\n    r_dry_mass : ')
        ret.append(repr(self.r_dry_mass))
        ret.append(',\n    epsil : ')
        ret.append(repr(self.epsil))
        ret.append(',\n    kb : ')
        ret.append(repr(self.kb))
        ret.append(',\n    avogadro : ')
        ret.append(repr(self.avogadro))
        ret.append('}')
        return ''.join(ret)
    
    _dt_array_initialisers = []
    

meteo = Meteo()

class Spartacus_Module(f90wrap.runtime.FortranModule):
    """
    Module spartacus_module
    
    
    Defined at suews_phys_spartacus.fpp lines 5-622
    
    """
    @staticmethod
    def spartacus_initialise():
        """
        spartacus_initialise()
        
        
        Defined at suews_phys_spartacus.fpp lines 45-80
        
        
        """
        _supy_driver.f90wrap_spartacus_initialise()
    
    @staticmethod
    def spartacus(diagqn, sfr_surf, zenith_deg, nlayer, tsfc_surf, tsfc_roof, \
        tsfc_wall, kdown, ldown, tair_c, alb_surf, emis_surf, lai_id, \
        n_vegetation_region_urban, n_stream_sw_urban, n_stream_lw_urban, \
        sw_dn_direct_frac, air_ext_sw, air_ssa_sw, veg_ssa_sw, air_ext_lw, \
        air_ssa_lw, veg_ssa_lw, veg_fsd_const, veg_contact_fraction_const, \
        ground_albedo_dir_mult_fact, use_sw_direct_albedo, height, building_frac, \
        veg_frac, sfr_roof, sfr_wall, building_scale, veg_scale, alb_roof, \
        emis_roof, alb_wall, emis_wall, roof_albedo_dir_mult_fact, \
        wall_specular_frac, qn_roof, qn_wall, qn_surf, dataoutlinespartacus):
        """
        qn, kup, lup = spartacus(diagqn, sfr_surf, zenith_deg, nlayer, tsfc_surf, \
            tsfc_roof, tsfc_wall, kdown, ldown, tair_c, alb_surf, emis_surf, lai_id, \
            n_vegetation_region_urban, n_stream_sw_urban, n_stream_lw_urban, \
            sw_dn_direct_frac, air_ext_sw, air_ssa_sw, veg_ssa_sw, air_ext_lw, \
            air_ssa_lw, veg_ssa_lw, veg_fsd_const, veg_contact_fraction_const, \
            ground_albedo_dir_mult_fact, use_sw_direct_albedo, height, building_frac, \
            veg_frac, sfr_roof, sfr_wall, building_scale, veg_scale, alb_roof, \
            emis_roof, alb_wall, emis_wall, roof_albedo_dir_mult_fact, \
            wall_specular_frac, qn_roof, qn_wall, qn_surf, dataoutlinespartacus)
        
        
        Defined at suews_phys_spartacus.fpp lines 82-622
        
        Parameters
        ----------
        diagqn : int
        sfr_surf : float array
        zenith_deg : float
        nlayer : int
        tsfc_surf : float array
        tsfc_roof : float array
        tsfc_wall : float array
        kdown : float
        ldown : float
        tair_c : float
        alb_surf : float array
        emis_surf : float array
        lai_id : float array
        n_vegetation_region_urban : int
        n_stream_sw_urban : int
        n_stream_lw_urban : int
        sw_dn_direct_frac : float
        air_ext_sw : float
        air_ssa_sw : float
        veg_ssa_sw : float
        air_ext_lw : float
        air_ssa_lw : float
        veg_ssa_lw : float
        veg_fsd_const : float
        veg_contact_fraction_const : float
        ground_albedo_dir_mult_fact : float
        use_sw_direct_albedo : bool
        height : float array
        building_frac : float array
        veg_frac : float array
        sfr_roof : float array
        sfr_wall : float array
        building_scale : float array
        veg_scale : float array
        alb_roof : float array
        emis_roof : float array
        alb_wall : float array
        emis_wall : float array
        roof_albedo_dir_mult_fact : float array
        wall_specular_frac : float array
        qn_roof : float array
        qn_wall : float array
        qn_surf : float array
        dataoutlinespartacus : float array
        
        Returns
        -------
        qn : float
        kup : float
        lup : float
        
        """
        qn, kup, lup = _supy_driver.f90wrap_spartacus(diagqn=diagqn, sfr_surf=sfr_surf, \
            zenith_deg=zenith_deg, nlayer=nlayer, tsfc_surf=tsfc_surf, \
            tsfc_roof=tsfc_roof, tsfc_wall=tsfc_wall, kdown=kdown, ldown=ldown, \
            tair_c=tair_c, alb_surf=alb_surf, emis_surf=emis_surf, lai_id=lai_id, \
            n_vegetation_region_urban=n_vegetation_region_urban, \
            n_stream_sw_urban=n_stream_sw_urban, n_stream_lw_urban=n_stream_lw_urban, \
            sw_dn_direct_frac=sw_dn_direct_frac, air_ext_sw=air_ext_sw, \
            air_ssa_sw=air_ssa_sw, veg_ssa_sw=veg_ssa_sw, air_ext_lw=air_ext_lw, \
            air_ssa_lw=air_ssa_lw, veg_ssa_lw=veg_ssa_lw, veg_fsd_const=veg_fsd_const, \
            veg_contact_fraction_const=veg_contact_fraction_const, \
            ground_albedo_dir_mult_fact=ground_albedo_dir_mult_fact, \
            use_sw_direct_albedo=use_sw_direct_albedo, height=height, \
            building_frac=building_frac, veg_frac=veg_frac, sfr_roof=sfr_roof, \
            sfr_wall=sfr_wall, building_scale=building_scale, veg_scale=veg_scale, \
            alb_roof=alb_roof, emis_roof=emis_roof, alb_wall=alb_wall, \
            emis_wall=emis_wall, roof_albedo_dir_mult_fact=roof_albedo_dir_mult_fact, \
            wall_specular_frac=wall_specular_frac, qn_roof=qn_roof, qn_wall=qn_wall, \
            qn_surf=qn_surf, dataoutlinespartacus=dataoutlinespartacus)
        return qn, kup, lup
    
    _dt_array_initialisers = []
    

spartacus_module = Spartacus_Module()

