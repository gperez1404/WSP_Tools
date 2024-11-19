# TUFLOW python tools tutorial

#%%
import pytuflow

res = pytuflow.ResData()  # initialising as an empty object

#res = pytuflow.ResData('M01_5m_001.tpc')  # initialising with results

# load .tpc result file
path = r'C:\GPM_CD\07-Python\inputs\TUFLOW\results\plot\E1_DR_PMP_1440m_TP01_004.tpc'
err, message = res.load(path)

# this code returns a list of the channels connected to a given node
# Node = Main_Channel
if not err:
    node = 'Main_Channel'
    conn_count = res.channelConnectionCount(node)
    # print to console    
    print('{0} channels connected to {1}'.format(conn_count, node))
else:
    # did not load correctly, print error message to console
    print(message)

#%%