
import struct
import ctypes
import binascii 
import player
import math
from Backend import Backend
import os

class GuppiBackend(Backend):
    """
    A class which implements some of the GUPPI specific parameter calculations.
    This class is specific to the Incoherent BOF designs.
    """
    def __init__(self, theBank):
        """
        Creates an instance of the vegas internals.
        GuppiBackend( bank )
        Where bank is the instance of the player's Bank.
        """
        Backend.__init__(self, theBank)
        # The default switching in the Backend ctor is a static SIG, NOCAL, and no blanking
        
        # defaults
        self.obs_mode = 'SEARCH' 
        self.max_databuf_size = 128 # in MBytes
        self.nchan = 64 # Needs to be a config value?
        self.integration_time = 1 # TBD JJB
        
        self.scale_i = 1
        self.scale_q = 1
        self.scale_u = 1
        self.scale_v = 1
        self.offset_i = 0
        self.offset_q = 0
        self.offset_u = 0
        self.offset_v = 0
        self.setBandwidth(100)
        self.dm = 0.0
        self.rf_frequency = 350.0
        dibas_dir = os.getenv("DIBAS_DIR")
        if dibas_dir is not None:
           self.pardir = dibas_dir + '/etc/config'
        else:
            self.pardir = '/tmp'
        self.parfile = 'example.par' 
        self.datadir = '/lustre/gbtdata/JUNK' # Needs integration with projectid
        
        self.params["acc_len"]        = self.setAccLen
        self.params["bandwidth"]      = self.setBandwidth
        self.params["dm"]             = self.setDM
        self.params["rf_frequency"]   = self.setRFfrequency
        self.params["obs_mode"]       = self.setObsMode
        self.params["num_channels"]   = self.set_nchannels
        self.params["scale_i"     ]   = self.setScale_I
        self.params["scale_q"     ]   = self.setScale_Q
        self.params["scale_u"     ]   = self.setScale_U
        self.params["scale_v"     ]   = self.setScale_V
        self.params["offset_i"    ]   = self.setOffset_I
        self.params["offset_q"    ]   = self.setOffset_Q
        self.params["offset_u"    ]   = self.setOffset_U
        self.params["offset_v"    ]   = self.setOffset_V
        
    ### Methods to set user or mode specified parameters
    ### Not sure how these map for GUPPI
                
    def setAccLen(self, acclen):
        self.acc_len = acclen
        
    def setBandwidth(self, bw):
        self.bandwidth = bw
        
    def setDM(self, dm):
        self.dm = dm
        
    def setObsMode(self, mode):
        # only incoherent modes. Coherent modes handled by GuppiCODDBackend class.
        legalmodes = ["SEARCH", "FOLD", "CAL", "RAW"]
        m = mode.upper()
        if m in legalmodes: 
            self.obs_mode = m
        else:
            raise Exception("setObsMode: mode must be one of %s" % str(legalmodes))
        
    def setRFfrequency(self, f):
        self.rf_frequency = f
                                  
    def set_nchannels(self, nchan):
        """
        This probably comes from config file, via the Bank
        """
        self.nchan = nchan        
        
    def setBandwidth(self, bandwidth):
        legal_bandwidths = [100, 200, 400, 800]
        if  abs(bandwidth) in legal_bandwidths:
            self.bandwidth = bandwidth
        else:
            raise Exception("Bandwidth of %d is not a legal bandwidth setting" % (bandwidth))
        
    def setIntegrationTime(self, int_time):
        """
        Sets the integration time
        """
        self.integration_time = int_time

    def setScale_I(self, v):
        self.scale_i = v
        
    def setScale_Q(self, v):
        self.scale_q = v

    def setScale_U(self, v):
        self.scale_u = v

    def setScale_V(self, v):
        self.scale_v = v
        
    def setOffset_I(self, v):
        self.offset_i = v

    def setOffset_Q(self, v):
        self.offset_q = v

    def setOffset_U(self, v):
        self.offset_u = v

    def setOffset_V(self, v):
        self.offset_v = v

    def prepare(self):
        """
        A place to hang the dependency methods.
        """

        self.hw_nchan_dep()
        self.acc_len_dep()
        self.chan_bw_dep()
        self.ds_time_dep()
        self.pfb_overlap_dep()
        self.pol_type_dep()
        self.tbin_dep()
        self.only_I_dep()
        self.tfold_dep()
    
                
    # Algorithmic dependency methods, not normally called by users
    
    def acc_len_dep(self):
        """
        Calculates the ACC_LEN status keyword
        (as opposed to the similarly named ACC_LENGTH in the old guppi bofs)
        """
        if 'COHERENT' in self.obs_mode:
            raise Exception("BUG: GuppiBackend vs. GuppiCODDBackend mixup")
        else:
            self.acc_len = int(self.integration_time * self.bandwidth / self.hw_nchan - 1 + 0.5) + 1
        # ACC_LENGTH register is 0...65535 in powers of 2 minus 1
        self.acc_length = self.acc_len-1
            
    def chan_bw_dep(self):
        """
        Calculates the CHAN_BW status keyword
        Result is bandwidth of each PFM channel in MHz
        """
        self.obsnchan = self.hw_nchan
        
        chan_bw = self.bandwidth / self.hw_nchan
        if self.bandwidth < 800:
            chan_bw = -1.0 * chan_bw
        self.chan_bw = chan_bw
        
    def ds_time_dep(self):
        """
        Calculate the down-sampling time status keyword
        """
        
        if 'SEARCH' in self.obs_mode:
            dst = self.integration_time * self.bandwidth / self.nchan
            power_of_two = 2 ** int(math.log(dst)/math.log(2))
            self.ds_time = power_of_two
        else:
            self.ds_time = 1
            
    def ds_freq_dep(self):
        """
        Calculate the DS_FREQ status keyword
        """
        self.ds_freq = self.hw_nchan / self.nchan
        
    def hw_nchan_dep(self):
        """
        Can't find direct evidence for this, but seemed logical ...
        """
        if 'COHERENT' in self.obs_mode:
            self.hw_nchan = self.nchan / 8 # number of nodes
        else:
            self.hw_nchan = self.nchan
                
    def pfb_overlap_dep(self):
        """
        Paul's guppi document does not list this parameter, however
        the Guppi manager calculates PFB_OVER which is used in the HPC server.
        Also see fft_params_dep
        """
        if 'COHERENT' in self.obs_mode and self.nchan in [128, 512]:
            self.overlap = 12
        else:
            self.overlap = 4
            
    def pol_type_dep(self):
        """
        Calculates the POL_TYPE status keyword.
        Depends upon a synthetic parameter 'obs_mode' TBD
        """
        
        if 'COHERENT' in self.obs_mode:
            self.pol_type = 'AABBCRCI'
        elif 'FAST4K' in self.obs_mode:
            self.pol_type = 'AA+BB'
        else:
            self.pol_type = 'IQUV'
            
    def node_bandwidth_dep(self):
        """
        Calculations the bandwidth seen by this HPC node
        """
        if 'COHERENT' in self.obs_mode:
            self.node_bandwidth = self.bandwidth / 8
        else:
            self.node_bandwidth = self.bandwidth
            
    def tbin_dep(self):
        """ 
        Calculates the TBIN status keyword
        """
        self.tbin = self.acc_len * self.hw_nchan / self.bandwidth
        
    def tfold_dep(self):
        if 'COHERENT' == self.obs_mode:
            self.fold_time = 1
            
    
        
    def only_I_dep(self):
        """
        Calculates the ONLY_I and PKTFMT status keywords
        """
        # Not the best way to handle this, but if the mode name has 'FAST4K'
        # in the name, assume FAST4K mode ...
        if 'FAST4K' in self.bank.current_mode:
            self.only_I = 1
            self.packet_format = 'FAST4K'
        else:
            self.only_I = 0
            self.packet_format = '1SFA'

    def set_status_keys(self):
        """
        Collect the status keywords
        """
        statusdata = {}
        statusdata['PKTFMT'  ] = self.packet_format
        statusdata['ACC_LEN' ] = self.acc_len
        
        node_rf = rf - bw/2.0 - chan_bw/2.0 + (i-1.0+0.5)*node_bw
        
        statusdata['OBSFREQ' ] = self.rf_frequency
        statusdata['OBSBW'   ] = self.node_bandwidth
        statusdata['OBSNCHAN'] = repr(self.node_nchan)
        statusdata['OBS_MODE'] = self.obs_mode
        statusdata['TBIN'    ] = self.tbin
        statusdata['DATADIR' ] = self.datadir
        statusdata['POL_TYPE'] = self.pol_type
        statusdata['SCALE0'  ] = '1.0'
        statusdata['SCALE1'  ] = '1.0'
        statusdata['SCALE2'  ] = '1.0'
        statusdata['SCALE3'  ] = '1.0'
        statusdata['OFFSET0' ] = '0.0'
        statusdata['OFFSET1' ] = '0.0'
        statusdata['OFFSET2' ] = '0.0'
        statusdata['OFFSET3' ] = '0.0'
        if self.parfile is not None:
            statuskeys['PARFILE'] = '%s/%s' % (self.pardir, self.parfile)
            
        statusdata['CHAN_DM' ] = self.dm
        statusdata['FFTLEN'  ] = self.fft_len
        statusdata['OVERLAP' ] = self.overlap
        statusdata['BLOCSIZE'] = self.blocsize
        
        self.bank.set_status(**statusdata)
        
    def set_registers(self):
        regs = {}
        
        regs['ACC_LENGTH'] = self.acc_length
        regs['SCALE_I']    = int(self.scale_i*65536)
        regs['SCALE_Q']    = int(self.scale_q*65536)
        regs['SCALE_U']    = int(self.scale_u*65536)
        regs['SCALE_V']    = int(self.scale_v*65536)
        regs['OFFSET_I']   = int(self.offset_i*65536)
        regs['OFFSET_Q']   = int(self.offset_q*65536)
        regs['OFFSET_U']   = int(self.offset_u*65536)
        regs['OFFSET_V']   = int(self.offset_v*65536)
        self.bank.set_register(**regs)
                
    def fft_params_dep(self):
        """
        Calculate the PFB_OVERLAP, FFTLEN, and BLOCSIZE status keywords
        """
        self.fft_len = 16384
        self.pfb_overlap = 512
        self.blocsize = 33554432 # defaults
        
        
    def net_config(self):
        """
        Configure the network interface, DEST_IP and DEST_PORT registers.
        """
        pass      
      
      
if __name__ == "__main__":
    testCase1()
    
def testCase1():
    g = GuppiBackend(None)
    g.setRFcenterFrequency(350.0)
    g.set_nchannels(64)                                          
