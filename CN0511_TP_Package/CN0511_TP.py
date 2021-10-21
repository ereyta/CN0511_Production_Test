#!/usr/bin/python
# Copyright (C) 2019 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import time
import adi
from iio import scan_contexts
from pluto import pluto_sdr #cloned from git clone https://github.com/radiosd/PlutoSdr.git
from pluto import pluto_dds

def Test_case(mydac,DAC_Sample_Rate, DAC_NCO_Scale, DAC_RF_Out, DAC_Switch):

    #SETUP CN0511
    #time.sleep(2)  
    mydac.sample_rate = DAC_Sample_Rate # set the DAC Clock sampling frequency
    mydac.raw = DAC_NCO_Scale #set the DAC NCO Scale
    mydac.frequency = DAC_RF_Out # set the DAC RFout Center frequency 
    mydac.tx_enable = DAC_Switch # disable(False)/Enable(True) the DAC Amp output


def Pluto_Reading(mypluto,RF_Out):

    #Set Pluto RX Center Frequency
    mypluto.rx_lo_freq = RF_Out/1000000
    
    #Read Pluto RX RF Signal Received and convert to RSSI in dB
    RSSI = mypluto.phy.channels[5].attrs['rssi'].value
    new_RSSI = RSSI.replace(' dB', '')
    new_RSSI_float = float(new_RSSI)
    return(new_RSSI_float)


def Test_Range(RSSI,Min,Max):
    if (RSSI >= Min and RSSI <= Max):
        result = "Pass"
    else:
        result = "Fail"
    return(result)
    
def main():
    try:
        context_list = scan_contexts()
        #print(context_list)
        pluto_context = ''
        for context in context_list.keys():
            if context[0:3] == 'usb':
                pluto_context = context
        #print(pluto_context)
        mypluto = pluto_sdr.PlutoSdr(uri = pluto_context)
        #mypluto_dds_1 = pluto_dds.DdsTone(uri = pluto_context1)
        mydac = adi.ad916x.ad9166(uri="ip:analog.local") # REMEMBER TO VERIFY POWERDOWN/UP BEHAVIOR
    except Exception as e:
        print(str(e))
        print("No device found")
        sys.exit(0)

    Min_FS = [15,17,28,30] #Minimum RSSI at NCO Full Scale 
    Max_FS = [20,21,32,34] #Maximum RSSI at NCO Full Scale
    Min_MidS = [19,25,33,38] #Minimum RSSI at NCO Mid Scale
    Max_MidS = [23,28,37,44] ##Maximum RSSI at NCO Mid Scale   
    DAC_Sample_Rate = [5000000000,6000000000]
    DAC_NCO_Scale = [32767,16384] #[Max Scale, Mid Scale]
    NCO_Scale = ["Full Scale","Mid Scale"]
    DAC_RF_Out = [1000000000,2000000000,4000000000,4500000000] #RF Out at [1GHz, 2GHz, 4GHz, 4.5GHz]
    result = "Pass"
    final_remark = "Passed"

    #Initialize DAC Settings
    mydac.FIR85_enable = True
    mydac.nco_enable = True #disable(False)/Enable(True) the DAC FIR85 Filter 
    mydac.sample_rate = DAC_Sample_Rate[0] # set the DAC Clock sampling frequency
    mydac.raw = DAC_NCO_Scale[0] #set the DAC NCO Scale
    mydac.frequency = DAC_RF_Out[0] # set the DAC RFout Center frequency 
    mydac.tx_enable = True # disable(False)/Enable(True) the DAC Amp output
    
    #Initialize ADALM_Pluto BW to 6MHz 
    mypluto.rx_bandwidth = 6
    #print ("Pluto BW(MHz): ", mypluto.rx_bandwidth )

    
    print ("\n====================")  
    print ("Test Started!!!")   
    print ("====================\n")  

    for NCO_scale in range(len(DAC_NCO_Scale)):
        #print("_________________________________________________")
        print("NCO Scale: " + str(NCO_Scale[NCO_scale])+"("+str(DAC_NCO_Scale[NCO_scale])+")")
        print("-------------------")
        mydac.raw = DAC_NCO_Scale[NCO_scale]
        if (NCO_scale == 0):
            Min = Min_FS 
            Max = Max_FS 
        else:
            Min = Min_MidS 
            Max = Max_MidS 

        for dac_clk in range(len(DAC_Sample_Rate)):
            mydac.sample_rate = DAC_Sample_Rate[dac_clk]
            
            print("DAC Clock Sampling Frequency(GHz): ",DAC_Sample_Rate[dac_clk]/1000000000)
            for rf_out in range(len(DAC_RF_Out)):
                if (dac_clk == 1 and rf_out == 3):
                    mydac.frequency = 5500000000
                    #mypluto.rx_lo_freq = mydac.frequency/1000000 
                    
                else:
                    mydac.frequency = DAC_RF_Out[rf_out]
                mypluto.rx_lo_freq = mydac.frequency/1000000 
                time.sleep(1)
                RSSI_main = Pluto_Reading(mypluto,DAC_RF_Out[rf_out])   
                Result = Test_Range(RSSI_main,Min[rf_out],Max[rf_out])    
                if (Result == "Fail"):
                    final_remark = "Failed"
                    print(str(mydac.frequency/1000000)+"MHz/ ["+str(Min[rf_out])+" < ("+str(RSSI_main)+") < "+str(Max[rf_out])+"] (RSSI in Abs) = " + Result)
                else:
                    print(str(mydac.frequency/1000000)+"MHz/ ["+str(Min[rf_out])+" < ("+str(RSSI_main)+") < "+str(Max[rf_out])+"] (RSSI in Abs) = " + Result)
            print("************************")
        print(" ") 
        
    print("Final Remark: ", final_remark)
    print(" ")

    print ("\n====================")  
    print ("Test Ended!!!")   
    print ("====================\n")  

main()




