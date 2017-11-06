import ddpaper.data

def test_units():
    print(ddpaper.data.DynUnitDict({'keV':1.})['erg'])

    print(ddpaper.data.DynUnitDict({'m/s': 10.})['km/hour'])