import copy
import warnings
from itertools import permutations
from typing import Union

from waveforms.baseconfig import _flattenDictIter, _foldDict, _query, _update
from waveforms.namespace import DictDriver
from waveforms.qlisp import (ABCCompileConfigMixin, ADChannel, AWGChannel,
                             ConfigProxy, GateConfig, MultADChannel,
                             MultAWGChannel)


def _getSharedCoupler(qubitsDict: dict) -> set[str]:
    s = set(qubitsDict[0]['couplers'])
    for qubit in qubitsDict[1:]:
        s = s & set(qubit['couplers'])
    return s


def _makeAWGChannelInfo(section: str, cfgDict: dict,
                        name: str) -> Union[str, dict]:
    ret = {}
    if name == 'RF':
        if cfgDict['channel']['DDS'] is not None:
            assert cfgDict['waveform'][
                'DDS_LO'] is not None, 'error in config `DDS_LO.'
            return {
                'I': f"{section}.waveform.DDS",
                'lofreq': cfgDict['waveform']['DDS_LO']
            }
        if cfgDict['channel']['I'] is not None:
            ret['I'] = f"{section}.waveform.RF.I"
        if cfgDict['channel']['Q'] is not None:
            ret['Q'] = f"{section}.waveform.RF.Q"
        ret['lofreq'] = cfgDict['setting']['LO']
        return ret
    elif name == 'AD.trigger':
        return f"{section}.waveform.TRIG"
    else:
        return f"{section}.waveform.{name}"


class CompileConfigMixin(ABCCompileConfigMixin):

    def _getAWGChannel(self, name,
                       *qubits) -> Union[AWGChannel, MultAWGChannel]:

        qubitsDict = [self.getQubit(q) for q in qubits]

        if name.startswith('readoutLine.'):
            name = name.removeprefix('readoutLine.')
            section = qubitsDict[0]['probe']
            cfgDict = self.getReadout(section)
        elif name.startswith('coupler.'):
            name = name.removeprefix('coupler.')
            section = _getSharedCoupler(qubitsDict).pop()
            cfgDict = self.getCoupler(section)
        else:
            section = qubits[0]
            cfgDict = qubitsDict[0]

        chInfo = _makeAWGChannelInfo(section, cfgDict, name)

        if isinstance(chInfo, str):
            return AWGChannel(chInfo, -1)
        else:
            info = {'lo_freq': chInfo['lofreq']}
            if 'I' in chInfo:
                info['I'] = AWGChannel(chInfo['I'], -1)
            if 'Q' in chInfo:
                info['Q'] = AWGChannel(chInfo['Q'], -1)
            return MultAWGChannel(**info)

    def _getADChannel(self, qubit) -> Union[ADChannel, MultADChannel]:
        rl = self.getQubit(qubit)['probe']
        rlDict = self.getReadout(rl)
        chInfo = {
            'IQ': rlDict['channel']['ADC'],
            'LO': rlDict['channel']['LO'],
            'TRIG': rlDict['channel']['TRIG'],
            'lofreq': rlDict['setting']['LO'],
            'trigger':
            f'{rl}.waveform.TRIG' if rlDict['channel']['TRIG'] else '',
            'sampleRate': rlDict['adcsr'],
            'triggerDelay': rlDict['setting']['TRIGD'],
            'triggerClockCycle': rlDict['setting'].get('triggerClockCycle',
                                                       8e-9),
            'triggerDelayAddress': rlDict['channel'].get('DATRIGD', '')
        }

        return MultADChannel(
            IQ=ADChannel(
                chInfo['IQ'], chInfo['sampleRate'], chInfo['trigger'],
                chInfo['triggerDelay'], chInfo['triggerClockCycle'],
                (('triggerDelayAddress', chInfo['triggerDelayAddress']), )),
            LO=chInfo['LO'],
            lo_freq=chInfo['lofreq'],
        )

    def _getGateConfig(self, name, *qubits, type=None) -> GateConfig:
        try:
            gate = self.getGate(name, *qubits)
            if not isinstance(gate, dict):
                return None
            qubits = gate['qubits']
            if type is None:
                type = gate.get('default_type', 'default')
            if type not in gate:
                params = gate['params']
            else:
                params = gate[type]
        except:
            type = 'default'
            params = {}
        return GateConfig(name, qubits, type, params)

    def _getAllQubitLabels(self) -> list[str]:
        return self.keys('Q*')


class LocalConfig(ConfigProxy, CompileConfigMixin):

    def __init__(self, data) -> None:
        self._history = None
        self.__driver = DictDriver(copy.deepcopy(data))

    def query(self, q):
        return self.__driver.query(q)

    def keys(self, pattern='*'):
        return self.__driver.keys(pattern)

    def update(self, q, v, cache=False):
        self.__driver.update_many({q: v})

    def getQubit(self, name):
        return self.query(name)

    def getCoupler(self, name):
        return self.query(name)

    def getReadout(self, name):
        return self.query(name)

    def getReadoutLine(self, name):
        return self.query(name)

    def getGate(self, name, *qubits):
        order_senstive = self.query(f"gate.{name}.__order_senstive__")
        if order_senstive is None:
            order_senstive = True
        if len(qubits) == 1 or order_senstive:
            ret = self.query(f"gate.{name}.{'_'.join(qubits)}")
            if isinstance(ret, dict):
                ret['qubits'] = tuple(qubits)
                return ret
            else:
                raise Exception(f"gate {name} of {qubits} not calibrated.")
        else:
            for qlist in permutations(qubits):
                try:
                    ret = self.query(f"gate.{name}.{'_'.join(qlist)}")
                    if isinstance(ret, dict):
                        ret['qubits'] = tuple(qlist)
                        return ret
                except:
                    break
            raise Exception(f"gate {name} of {qubits} not calibrated.")

    def clear_buffer(self):
        pass

    def export(self):
        return copy.deepcopy(self.__driver.dct)
