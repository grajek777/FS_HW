'''
Created on 8 May 2018

@author: Szymon Grajewski
@brief   This file uses asyncio and pysnmp libraries.
The following sources were used as a base for the implementation:
http://snmplabs.com/pysnmp/examples/hlapi/asyncio/contents.html
http://snmplabs.com/pysnmp/examples/hlapi/asyncio/manager/cmdgen/advanced-topics.html
'''

import asyncio
from pysnmp.hlapi.asyncio import *

async def getSNMPv1(hostname, vBinds):
    '''
    @brief Simple implementation of SNMP(v1) get command
    Args:
    @param hostname: tuple of FQDN, port where FQDN is a string representing either 
                     hostname or IPv4 address in quad-dotted form, port is an integer
    @param vBinds:   list of one or more class instances representing MIB variables to 
                     place into SNMP request.
    @return varBinds sequence of ObjectType class instances representing MIB
            variables returned in SNMP response
    '''
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        CommunityData('public', mpModel=0),
        UdpTransportTarget(hostname),
        ContextData(),
        *vBinds
    )
    
    print("get")
    
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
        )
              )
    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))
    
    snmpEngine.transportDispatcher.closeDispatcher()
    
    return varBinds


async def setSNMPv1(hostname, vBinds):
    '''
    @brief Simple implementation of SNMP(v1) set command
    Args:
    @param hostname: tuple of FQDN, port where FQDN is a string representing either 
                     hostname or IPv4 address in quad-dotted form, port is an integer
    @param vBinds:   list of one or more class instances representing MIB variables to 
                     place into SNMP request.
    @return varBinds sequence of ObjectType class instances representing MIB
            variables returned in SNMP response
    '''
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
        snmpEngine,
        CommunityData('public', mpModel=0),
        UdpTransportTarget(hostname),
        ContextData(),
        *vBinds
    )
    
    print("set")
    
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
        )
              )
    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))
    
    snmpEngine.transportDispatcher.closeDispatcher()
    
    return varBinds


async def execConcOpSNMP(hostname, ops):
    '''
    @brief Create a group of coroutines and executes them in a concurrent manner
    Args:
    @param hostname: tuple of FQDN, port where FQDN is a string representing either 
                     hostname or IPv4 address in quad-dotted form, port is an integer
    @param ops:      list of tuples of requested SNMP operation (string "get" or "set") 
                     and class instances representing MIB variables to place into SNMP 
                     request.
    '''
    coroutines = []
    for op in ops:
        if op[0] == "get":
            coroutines.append(getSNMPv1(hostname, [op[1]]))
        elif op[0] == "set":
            coroutines.append(setSNMPv1(hostname, [op[1]]))
    
    completed, pending = await asyncio.wait(coroutines)


async def execSeqOpSNMP(hostname, ops):
    '''
    @brief Executes a group of coroutines in a sequential manner
    Args:
    @param hostname: tuple of FQDN, port where FQDN is a string representing either 
                     hostname or IPv4 address in quad-dotted form, port is an integer
    @param ops:      list of tuples of requested SNMP operation (string "get" or "set") 
                     and class instances representing MIB variables to place into SNMP 
                     request.
    '''
    for op in ops:
        if op[0] == "get":
            await getSNMPv1(hostname, [op[1]])
        elif op[0] == "set":
            await setSNMPv1(hostname, [op[1]])

if __name__ == '__main__':
    ###########################################
    # Example of use
    ###########################################
    loop = asyncio.get_event_loop()
    hostname = ('demo.snmplabs.com', 161)
    
    getObject1 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0))
    getObject2 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0))
    setObject1 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0), 
                            'SunOS zeus.snmplabs.com 4.1.3_U1 1 sun4m')
    setObject2 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0), 
                            'Linux v2.0')
    
    try:
        loop.run_until_complete(setSNMPv1(hostname, [setObject1]))
        loop.run_until_complete(getSNMPv1(hostname, [getObject1]))
        loop.run_until_complete(setSNMPv1(hostname, [setObject2]))
        loop.run_until_complete(getSNMPv1(hostname, [getObject1]))
        loop.run_until_complete(getSNMPv1(hostname, [getObject1, getObject2]))
        print("--------------------------------------")
        
        loop.run_until_complete(execConcOpSNMP(hostname, 
                                              [("set", setObject1),
                                               ("get", getObject1),
                                               ("set", setObject2),
                                               ("get", getObject1)]
                                              )
                                )
        print("--------------------------------------")
        loop.run_until_complete(execSeqOpSNMP(hostname, 
                                             [("set", setObject1),
                                              ("get", getObject1),
                                              ("set", setObject2),
                                              ("get", getObject1)]
                                             )
                                )
    finally:
        loop.close()
    