'''
Created on 8 May 2018

@author: Szymon Grajewski
This file uses asyncio and pysnmp libraries.
The following sources were used as a base for the implementation:
http://snmplabs.com/pysnmp/examples/hlapi/asyncio/contents.html
http://snmplabs.com/pysnmp/examples/hlapi/asyncio/manager/cmdgen/advanced-topics.html
'''

import asyncio
from pysnmp.hlapi.asyncio import *

@asyncio.coroutine
def getSNMPv1(hostname, vBinds):
    '''
    Simple implementation of SNMP(v1) get command
    Args:
    hostname: tuple of FQDN, port where FQDN is a string representing either 
              hostname or IPv4 address in quad-dotted form, port is an integer
    vBinds:   list of one or more class instances representing MIB variables to 
              place into SNMP request.
    '''
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = yield from getCmd(
        snmpEngine,
        CommunityData('public', mpModel=0),
        UdpTransportTarget(hostname),
        ContextData(),
        *vBinds
    )
    
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

@asyncio.coroutine
def setSNMPv1(hostname, vBinds):
    '''
    Simple implementation of SNMP(v1) set command
    Args:
    hostname: tuple of FQDN, port where FQDN is a string representing either 
              hostname or IPv4 address in quad-dotted form, port is an integer
    vBinds:   list of one or more class instances representing MIB variables to 
              place into SNMP request.
    '''
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = yield from setCmd(
        snmpEngine,
        CommunityData('public', mpModel=0),
        UdpTransportTarget(hostname),
        ContextData(),
        *vBinds
    )
    
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

if __name__ == '__main__':
    ###########################################
    # Example of use
    ###########################################
    loop = asyncio.get_event_loop()
    hostname = ('demo.snmplabs.com', 161)
    
    getObject1 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0))
    # set init values for chosen read-write object
    setObject1 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0), 
                            'SunOS zeus.snmplabs.com 4.1.3_U1 1 sun4m')
    loop.run_until_complete(setSNMPv1(hostname, [setObject1]))
    loop.run_until_complete(getSNMPv1(hostname, [getObject1]))
    # change values for chosen read-write object
    setObject1 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0), 
                            'Linux v2.0')
    loop.run_until_complete(setSNMPv1(hostname, [setObject1]))
    loop.run_until_complete(getSNMPv1(hostname, [getObject1]))
    
    getObject2 = ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0))
    loop.run_until_complete(getSNMPv1(hostname, [getObject1, getObject2]))
    