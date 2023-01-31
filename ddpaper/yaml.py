from astropy.io.misc import yaml

def setup_yaml():
    return yaml

    # def quantity_constructor(loader, node):
    #     value = loader.construct_scalar(node)
    #     value, unit = re.search("(.*?)__(.*)", value).groups()
    #     return u.Quantity(value, unit=u.Unit(unit))

    # def quantity_representer(dumper, data):
    #     return dumper.represent_scalar(u'!Quantity', u'%.5lg__%s' % (data.value, data.unit.to_string()))

    # def unit_representer(dumper, data):
    #     return quantity_representer(dumper, 1.*data)
    
    # yaml.add_representer(u.Quantity, quantity_representer)
    # yaml.add_representer(const.Constant, quantity_representer)
    # yaml.add_representer(u.Unit, unit_representer)
    # yaml.add_representer(u.core.CompositeUnit, unit_representer)    
    # yaml.add_constructor('!Quantity', quantity_constructor)

    # yaml.add_representer(coord.sky_coordinate.SkyCoord, skycoord_representer)        
    # yaml.add_constructor('!SkyCoord', skycoord_constructor)

    # yaml.add_representer(np.core.multiarray, array_representer)        
    # # yaml.add_constructor('!SkyCoord', skycoord_constructor)

