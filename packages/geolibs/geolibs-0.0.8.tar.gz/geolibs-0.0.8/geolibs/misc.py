from mmengine.config import Config
import importlib

def add_classes_to_package(package_name, cls_list):
    package = importlib.import_module(package_name)
    for cls in cls_list:
        class_name = cls.__name__
        
        setattr(package, class_name, cls)
        if '__all__' in package.__dict__:
            package.__dict__['__all__'].append(class_name)
        else:
            package.__dict__['__all__'] = [class_name]

def add_file_name_in_engine_tags(cfg, logger=None):
    """If engine logging is present, update tags with
        the config file name.
    """
    assert isinstance(cfg, Config), \
        f'cfg got wrong type: {type(cfg)}, expected Config'
    if 'custom_hooks' in cfg:
        assert len(cfg.custom_hooks), "Print cannot find logger hooks"
        for hook in cfg.custom_hooks:
            if hook['type'] == 'EngineLoggerHook':
                if 'init_kwargs' in hook:
                    if 'tags' in hook['init_kwargs']:
                        fname = cfg.filename.split('/')[-1].split('.')[0]
                        hook['init_kwargs']['tags'].append(fname)
    return cfg

