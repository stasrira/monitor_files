import yaml
from utils import common as cm


class ConfigData:

    """
    def __init__(self, study_cfg_path):
        self.loaded = False
        with open(study_cfg_path, 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)
        self.loaded = True
    """

    def __init__(self, cfg_path = None, cfg_content_dict = None):
        self.loaded = False
        self.cfg_path = cfg_path
        self.cfg = None

        if cfg_path and cm.file_exists(cfg_path):
            with open(cfg_path, 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)
            # self.prj_wrkdir = os.path.dirname(os.path.abspath(study_cfg_path))
            self.loaded = True
        else:
            if cfg_content_dict:
                self.cfg = cfg_content_dict
                self.loaded = True
            else:
                self.cfg = None
            # self.prj_wrkdir = None

    def get_value(self, yaml_path, delim=None):
        if not delim:
            delim = '/'

        path_elems = yaml_path.split(delim)

        # loop through the path to get the required key
        val = self.cfg
        for el in path_elems:
            # make sure "val" is not None and continue checking if "el" is part of "val"
            if val and el in val:
                try:
                    val = val[el]
                except Exception:
                    val = None
                    break
            else:
                val = None

        return val

    def get_item_by_key(self, key_name):
        # return str(self.get_value(key_name))
        v = self.get_value(key_name)
        if v is not None:
            return str(self.get_value(key_name))
        else:
            return v

    def get_all_data(self):
        return self.cfg

    def set_value(self, value, yaml_path, delim=None):
        if not delim:
            delim = '/'

        out = False

        path_elems = yaml_path.split(delim)
        if not self.cfg:
            self.cfg = {}
        upd_item = self.cfg
        num_items = len(path_elems)
        cnt = 0

        for el in path_elems:
            cnt += 1
            if upd_item and el in upd_item:
                try:
                    if cnt < num_items:
                        if not upd_item[el]:
                            upd_item[el] = {}
                        upd_item = upd_item[el]
                    else:
                        upd_item[el] = value
                        out = True
                except Exception:
                    out = False
                    break
            else:
                if cnt < num_items:
                    upd_item[el] = {}
                    upd_item = upd_item[el]
                else:
                    upd_item[el] = value
                    out = True

        # self.cfg = upd_item
        if cm.file_exists(self.cfg_path):
            with open(self.cfg_path, 'w') as yaml_file:
                yaml_file.write(yaml.dump(self.cfg, default_flow_style=False))

        return out