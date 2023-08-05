import pandas as pd


class ParametersArray:
    """Parsing of the parameters resulting from the optimizer"""

    def __init__(self, path):
        self.path = path
        self.id = 0
        self.score = ''
        self.struct = []
        self.data = []

    def load(self):
        file_struct = self._parse_headers()
        # Check for duplicates
        seen = set()
        dupes = [x for x in file_struct[1] if x in seen or seen.add(x)]
        if len(dupes) > 0:
            raise Exception(f'Duplicates found in the column names: {dupes}')
        self.data = pd.read_csv(self.path, sep='\t', skiprows=1, usecols=file_struct[0],
                                names=file_struct[1])
        self._remove_failed()

    def load_scores_only(self):
        file_struct = self._parse_headers_scores_only()
        self.data = pd.read_csv(self.path, sep='\t', skiprows=1, usecols=file_struct[0],
                                names=file_struct[1])
        self._remove_failed()

    def _parse_headers(self):
        fid = open(self.path)
        fid.readline()
        line = fid.readline().split('\t')
        self.id = line[1]

        headers = []
        cols = []
        step = 0
        ptor = 0
        for idx, chars in enumerate(line):
            append = False
            if chars[0:10] == '|||| Step(':
                step = int(chars[10:-1])
                self.struct.append(0)
            elif chars[0:8] == '|| Ptor(':
                ptor = int(chars[8:-1])
                self.struct[step] = ptor + 1
            elif chars == 'Anb':
                label = f'Anb_{step}'
                headers.append(label)
                cols.append(idx + 1)
            elif chars == 'Level':
                append = True
                label = f'Variable_{step}_{ptor}'
                if label in headers:
                    label += 'b'
                headers.append(label)
                cols.append(idx-1)
            elif chars == 'Time':
                append = True
            elif chars == 'xMin':
                append = True
            elif chars == 'xPtsNb':
                append = True
            elif chars == 'xStep':
                append = True
            elif chars == 'yMin':
                append = True
            elif chars == 'yPtsNb':
                append = True
            elif chars == 'yStep':
                append = True
            elif chars == 'Weight':
                append = True
            elif chars == 'Criteria':
                append = True
            elif chars == 'Calib':
                headers.append(chars)
                cols.append(idx + 1)
            elif chars == 'Valid':
                headers.append(chars)
                cols.append(idx + 1)
            elif "Score" in chars:
                self.score = line[idx + 1]

            if append:
                label = f'{chars}_{step}_{ptor}'
                if label in headers:
                    label += 'b'
                headers.append(label)
                cols.append(idx + 1)

        fid.close()

        return [cols, headers]

    def _parse_headers_scores_only(self):
        fid = open(self.path)
        fid.readline()
        line = fid.readline().split('\t')
        self.id = line[1]

        headers = []
        cols = []
        for idx, chars in enumerate(line):
            if chars == 'Calib':
                headers.append(chars)
                cols.append(idx + 1)
            elif chars == 'Valid':
                headers.append(chars)
                cols.append(idx + 1)
            elif "Score" in chars:
                self.score = line[idx + 1]

        fid.close()

        return [cols, headers]

    def _remove_failed(self):
        if self.score == 'CRPS':
            # Remove 0s
            self.data.drop(self.data[self.data.Calib == 0].index, inplace=True)

    def get_station(self):
        return self.id

    def get_station_int(self):
        return int(self.id)

    def get_steps_nb(self):
        return len(self.struct)

    def get_ptors_nb(self, step):
        return self.struct[step]

    def get_anbs(self, step):
        return int(self.data[f'Anb_{step}'])

    def get_variables(self, step, ptor):
        return self.data[f'Variable_{step}_{ptor}']

    def get_variable(self, step, ptor, index=0):
        var = str(self.data[f'Variable_{step}_{ptor}'].iloc[index])
        # Remove prefixes
        if 'GenericNetcdf 100/' in var:
            var = var.replace('GenericNetcdf 100/', '')

        # Map levels
        if 'pressure/' in var:
            var = var.replace('pressure/', 'pl/')
        if 'press/' in var:
            var = var.replace('press/', 'pl/')
        if 'sff/' in var:
            var = var.replace('sff/', 'surf/')
        if 'sfa/' in var:
            var = var.replace('sfa/', 'surf/')

        # Check if composed variable
        if f'Variable_{step}_{ptor}b' in self.data:
            var2 = str(self.data[f'Variable_{step}_{ptor}b'].iloc[index])
            if 'pl/r' in var and 'tcw' in var2:
                return 'MI'
            else:
                return 'unknown'

        # Rename variables
        if 'hgt' in var:
            return 'Z'
        if var == 'z':
            return 'Z'
        elif 'pl/z' in var:
            return 'Z'
        elif 'pl/gpa' in var:
            return 'ZA'
        elif 'pl/w' in var:
            return 'W'
        elif 'pl/vvel' in var:
            return 'W'
        elif 'pl/vo' in var:  # Vorticity (relative) (ERA-int)
            return 'VO'
        elif 'pl/vpot' in var:  # Velocity potential (JRA55)
            return 'VPOT'
        elif 'pl/vgrd' in var:
            return 'V'
        elif 'pl/v' in var:
            return 'V'
        elif 'pl/u' in var:
            return 'U'
        elif 'pl/depr' in var:  # Dew-point depression (JRA55)
            return 'DEPR'
        elif 'surf/depr' in var:  # Dew-point depression (JRA55)
            return 'DEPR'
        elif 'pl/reld' in var:  # Relative divergence (JRA55)
            return 'RD'
        elif 'pl/d' in var:
            return 'D'
        elif 'pt/d' in var:
            return 'PT/D'
        elif 'pl/t' in var:
            return 'T'
        elif 'pl/pv' in var:
            return 'PV'
        elif 'pt/pv' in var:
            return 'PT/PV'
        elif 'pl/rh' in var:
            return 'RH'
        elif 'pl/r' in var:
            return 'RH'
        elif 'pv/z' in var:
            return 'PV/Z'
        elif 'pv/v' in var:
            return 'PV/V'
        elif 'pv/u' in var:
            return 'PV/U'
        elif 'pt/v' in var:
            return 'PT/V'
        elif 'pt/u' in var:
            return 'PT/U'
        elif 'pv/pres' in var:
            return 'PV/PRES'
        elif 'pt/pres' in var:
            return 'PT/PRES'
        elif 'pv/pt' in var:
            return 'PV/PT'
        elif 'pt/q' in var:
            return 'PT/SH'
        elif 'pl/q' in var:
            return 'SH'
        elif 'pt/mont' in var:
            return 'PT/MONT'
        elif 'surf/strd' in var:
            return 'STRD'
        elif 'single/strd' in var:
            return 'STRD'
        elif 'surf/str' in var:
            return 'STR'
        elif 'single/str' in var:
            return 'STR'
        elif 'surf/ssrd' in var:
            return 'SSRD'
        elif 'single/ssrd' in var:
            return 'SSRD'
        elif 'surf/ssr' in var:
            return 'SSR'
        elif 'single/ssr' in var:
            return 'SSR'
        elif 'surf/cape' in var:
            return 'CAPE'
        elif 'single/cape' in var:
            return 'CAPE'
        elif 'surf/ie' in var:
            return 'IE'
        elif 'surf/v10' in var:
            return 'V10m'
        elif 'single/v10' in var:
            return 'V10m'
        elif 'surf/u10' in var:
            return 'U10m'
        elif 'surf/msl' in var:
            return 'SLP'
        elif 'surf/rh' in var:
            return 'RH'
        elif 'surf/t2m' in var:
            return 'T2m'
        elif 'single/t2m' in var:
            return 'T2m'
        elif 'surf/sst' in var:
            return 'SST'
        elif 'surf/d2m' in var:
            return 'D2m'
        elif 'surf/sd' in var:
            return 'SD'
        elif 'surf/prmsl' in var:
            return 'SLP'
        elif 'single/tsr' in var:
            return 'TSR'
        elif 'single/ttr' in var:
            return 'TTR'
        elif 'single/sshf' in var:
            return 'SSHF'
        elif 'single/slhf' in var:
            return 'SLHF'
        elif 'msl/pres' in var:
            return 'SLP'
        elif 'single/lcc' in var:
            return 'LCC'
        elif 'pl/cc' in var:
            return 'CC'
        elif 'single/tcc' in var:
            return 'TCC'
        elif 'single/deg0l' in var:
            return 'DEG0L'
        elif 'plf/cwat' in var:
            return 'CWAT'
        elif 'ea/cwat' in var:
            return 'CWAT'
        elif 'tcf/cw' in var:
            return 'CWAT'
        elif 'tc/vwv' in var:
            return 'VWV'
        elif 'tcw' in var:
            return 'TCW'
        elif 'omega' in var:
            return 'W'
        return var

    def get_variable_and_level(self, step, ptor, index=0):
        var = self.get_variable(step, ptor, index)
        level = self.get_level(step, ptor, index)
        if level != 0:
            var += str(level)
        return var

    def get_levels(self, step, ptor):
        return self.data[f'Level_{step}_{ptor}']

    def get_level(self, step, ptor, index=0):
        return self.data[f'Level_{step}_{ptor}'].iloc[index]

    def get_times(self, step, ptor):
        return self.data[f'Time_{step}_{ptor}']

    def get_time(self, step, ptor, index=0):
        return self.data[f'Time_{step}_{ptor}'].iloc[index]

    def get_xmins(self, step, ptor):
        return self.data[f'xMin_{step}_{ptor}']

    def get_xmin(self, step, ptor, index=0):
        return self.data[f'xMin_{step}_{ptor}'].iloc[index]

    def get_xmaxs(self, step, ptor):
        return self.data[f'xMin_{step}_{ptor}'] + \
               (self.data[f'xPtsNb_{step}_{ptor}'] - 1) * self.data[
                   f'xStep_{step}_{ptor}']

    def get_xmax(self, step, ptor, index=0):
        return self.data[f'xMin_{step}_{ptor}'].iloc[index] + \
               (self.data[f'xPtsNb_{step}_{ptor}'].iloc[index] - 1) * \
               self.data[f'xStep_{step}_{ptor}'].iloc[index]

    def get_xptsnbs(self, step, ptor):
        return self.data[f'xPtsNb_{step}_{ptor}']

    def get_ymins(self, step, ptor):
        return self.data[f'yMin_{step}_{ptor}']

    def get_ymin(self, step, ptor, index=0):
        return self.data[f'yMin_{step}_{ptor}'].iloc[index]

    def get_ymaxs(self, step, ptor):
        return self.data[f'yMin_{step}_{ptor}'] + \
               (self.data[f'yPtsNb_{step}_{ptor}'] - 1) * self.data[
                   f'yStep_{step}_{ptor}']

    def get_ymax(self, step, ptor, index=0):
        return self.data[f'yMin_{step}_{ptor}'].iloc[index] + \
               (self.data[f'yPtsNb_{step}_{ptor}'].iloc[index] - 1) * \
               self.data[f'yStep_{step}_{ptor}'].iloc[index]

    def get_yptsnbs(self, step, ptor):
        return self.data[f'yPtsNb_{step}_{ptor}']

    def get_weight(self, step, ptor, index=0):
        return self.data[f'Weight_{step}_{ptor}'].iloc[index]

    def get_weights(self, step, ptor):
        return self.data[f'Weight_{step}_{ptor}']

    def get_criterion(self, step, ptor, index=0):
        criterion = self.data[f'Criteria_{step}_{ptor}'].iloc[index]
        if 'grads' in criterion:
            criterion = criterion[0:-5]
        return criterion

    def get_criteria(self, step, ptor):
        return self.data[f'Criteria_{step}_{ptor}']

    def get_calib_scores(self):
        return self.data['Calib']

    def get_calib_score(self, index=0):
        return self.data['Calib'].iloc[index]

    def get_valid_scores(self):
        return self.data['Valid']

    def get_valid_score(self, index=0):
        return self.data['Valid'].iloc[index]
