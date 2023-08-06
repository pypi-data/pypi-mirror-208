from inspect import trace
from .abc import TypeOPM, TypeVOA
from .models import BaseModelAQ63xx, BaseModelVSA89600
from .utils import deprecated


class DeprecatedTypeOPM:

    @property
    @deprecated
    def min_cal(self):
        return self.min_pow_cal

    @property
    @deprecated
    def max_cal(self):
        return self.max_pow_cal

    @deprecated
    def get_cal(self):
        return self.get_pow_cal()

    @deprecated
    def set_cal(self, value):
        self.set_pow_cal(value)


class DeprecatedTypeVOA:

    @property
    @deprecated
    def min_offset(self):
        return self.min_att_offset

    @property
    @deprecated
    def max_offset(self):
        return self.max_att_offset

    @deprecated
    def get_offset(self):
        return self.get_att_offset()

    @deprecated
    def set_offset(self, value):
        self.set_att_offset(value)


class DeprecatedVSA89600:

    @deprecated
    def get_trace_item_names(self, trace):
        return self.get_data_table_names(trace)

    @deprecated
    def get_trace_values(self, trace):
        return self.get_trace_values(trace)

    @deprecated
    def get_trace_units(self, trace):
        return self.get_trace_units(trace)

    @deprecated
    def get_trace_data(self, trace):
        return self.get_data_table(trace)


class DeprecatedModelAQ63xx(BaseModelAQ63xx):

    _analysis_cat = ["WDM", "DFBLD", "FPLD", "SMSR"]
    
    _analysis_setting_map = {
        "WDM": ["TH", "MDIFF", "DMASK", "NALGO", "NAREA", "MAREA", "FALGO", "NBW"],
        "DFBLD": {
            "SWIDTH": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
            "SMSR": ["SMODE", "SMASK", "MDIFF"],
            "RMS": ["ALGO", "TH", "K", "MDIFF"],
            "POWER": ["SPAN"],
            "OSNR": ["MDIFF", "NALGO", "NAREA", "MAREA", "FALGO", "NBW", "SPOWER", "IRANGE"],
        },
        "FPLD": {
            "SWIDTH": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
            "MWAVE": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
            "TPOWER": ["OFFSET"],
            "MNUMBER": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
        },
        "SMSR": ["MASK", "MODE"]
    }
    
    _setup_map = ["BWIDTH:RES"]

    @deprecated
    def auto_analysis(self, enable):
        self.set_auto_analysis(enable)

    @deprecated
    def set_analysis_cat(self, item):
        self.set_analysis_category(item)

    @deprecated
    def get_analysis_cat(self):
        return self.get_analysis_category()

    @deprecated
    def analysis_setting(self, cat, param, value, subcat=None):
        if cat not in self._analysis_cat:
            raise ValueError('Invalid analysis category: %r' % cat)
        if subcat:
            if subcat not in tuple(self._analysis_setting_map[cat].keys()):
                raise ValueError('Invalid subcat: %r' % subcat)
            if param not in self._analysis_setting_map[cat][subcat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = " %s,%s," % (subcat, param)
        else:
            if param not in self._analysis_setting_map[cat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = ":%s " % param
        value = str(value)
        cmd_str = ":CALC:PAR:%s%s%s" % (cat, route_str, value)
        return self.command(cmd_str)

    @deprecated
    def get_analysis_setting(self, cat, param, subcat=None):
        if cat not in self._analysis_cat:
            raise ValueError('Invalid analysis category: %r' % cat)
        if subcat:
            if subcat not in tuple(self._analysis_setting_map[cat].keys()):
                raise ValueError('Invalid subcat: %r' % subcat)
            if param not in self._analysis_setting_map[cat][subcat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = "? %s,%s" % (subcat, param)
        else:
            if param not in self._analysis_setting_map[cat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = ":%s?" % param
        cmd_str = ":CALC:PAR:%s%s" % (cat, route_str)
        return self.query(cmd_str)

    @deprecated
    def get_analysis_setting_map(self):
        return self._analysis_setting_map

    @deprecated
    def set_start_stop_wavelength(self, start, stop):
        self.set_start_wavelength(start)
        self.set_stop_wavelength(stop)

    @deprecated
    def set_start_stop_frequency(self, start, stop):
        self.set_start_frequency(stop)
        self.set_stop_frequency(start)

    @deprecated
    def setup(self, param, value):
        """
        Set setup settings.
        :param param: (str) param
        :param value: (str) setting value
        """
        if not isinstance(param, str):
            raise TypeError('param should be str')
        if not isinstance(value, str):
            raise TypeError('value should be str')
        return self.command(':SENS:%s %s' % (param, value))

    @deprecated
    def get_setup(self, param):
        return self.query(':SENS:%s?' % param)

    @deprecated
    def format_data(self, cat, data):
        """
        Format data into dict, depends on calculate category (Anasis Category)
        :param cat: (str) "DFB"|"FP"|"WDM"
        :param data: (str) data retruned by method: get_analysis_data
        :return: (dict) a dict of test_item=>value
        """
        if cat not in self._analysis_cat:
            raise ValueError('Invalid cat: %r' % cat)
        data_list = data.split(',')
        r_data = None
        if cat == 'DFBLD':
            r_data = {
                "spec_wd": data_list[0],
                "peak_wl": data_list[1],
                "peak_lvl": data_list[2],
                "mode_ofst": data_list[3],
                "smsr": data_list[4]
            }
        elif cat == 'FPLD':
            r_data = {
                "spec_wd": data_list[0],
                "peak_wl": data_list[1],
                "peak_lvl": data_list[2],
                "center_wl": data_list[3],
                "total_pow": data_list[4],
                "mode_num": data_list[5]
            }
        elif cat == 'WDM':
            #  <display type> = ABSolute|0, RELative|1, MDRift|2, GDRift|3
            d_type = int(self.query(':CALC:PAR:WDM:DTYP?'))
            # 0 = OFFSET, 1 = SPACING
            relation = int(self.query(':CALC:PAR:WDM:REL?'))
            if d_type == 0:
                if relation == 0:
                    r_data = {
                        "ch_num": data_list[0],
                        "center_wl": data_list[1],
                        "peak_lvl": data_list[2],
                        "offset_wl": data_list[3],
                        "offset_lvl": data_list[4],
                        "noise": data_list[5],
                        "snr": data_list[6]
                    }
                elif relation == 1:
                    r_data = {
                        "ch_num": data_list[0],
                        "center_wl": data_list[1],
                        "peak_lvl": data_list[2],
                        "spacing": data_list[3],
                        "lvl_diff": data_list[4],
                        "noise": data_list[5],
                        "snr": data_list[6]
                    }
            elif d_type == 1:
                r_data = {
                    "ch_num": data_list[0],
                    "grid_wl": data_list[1],
                    "center_wl": data_list[2],
                    "rel_wl": data_list[3],
                    "peak_lvl": data_list[4],
                    "noise": data_list[5],
                    "snr": data_list[6]
                }
            elif d_type == 2:
                r_data = {
                    "ch_num": data_list[0],
                    "grid_wl": data_list[1],
                    "center_wl": data_list[2],
                    "wl_diff_max": data_list[3],
                    "wl_diff_min": data_list[4],
                    "ref_lvl": data_list[5],
                    "peak_lvl": data_list[6],
                    "lvl_diff_max": data_list[7],
                    "lvl_diff_min": data_list[8]
                }
            elif d_type == 3:
                r_data = {
                    "ch_num": data_list[0],
                    "ref_wl": data_list[1],
                    "center_wl": data_list[2],
                    "wl_diff_max": data_list[3],
                    "wl_diff_min": data_list[4],
                    "ref_lvl": data_list[5],
                    "peak_lvl": data_list[6],
                    "lvl_diff_max": data_list[7],
                    "lvl_diff_min": data_list[8]
                }
        return r_data

    @deprecated
    def set_trace_display(self, trace_name, state) -> None:
        return self.set_trace_display_status(trace_name, state)


def deprecated_monkey_patch():

    TypeOPM.__bases__ += (DeprecatedTypeOPM,)
 
    TypeVOA.__bases__ += (DeprecatedTypeVOA,)

    BaseModelVSA89600.__bases__ += (DeprecatedVSA89600,)

    BaseModelAQ63xx.__bases__ += (DeprecatedModelAQ63xx,)