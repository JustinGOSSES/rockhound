"""
Load the Mannville Group Well Logs dataset from Alberta, Canada.
"""
# import tarfile
from pooch import Unzip
import pandas as pd

# from pooch import Untar
from .registry import REGISTRY


def fetch_mcmurray_facies(abbreviations_only=True, load=True):
    r"""
    This is a preprocessed dataframe of well log information focused on facies prediction.

    The preprocessed data is coming from here:
    https://github.com/JustinGOSSES/McMurray-Wabiskaw-preprocessed-datasets

    The original dataset, unprocessed, comes from a collection of over 2000 wells made public
    by the Alberta Geological Survey’s Alberta Energy Regulator. To quote their webpage, “In 1986,
    Alberta Geological Survey began a project to map the McMurray Formation and the overlying
    Wabiskaw Member of the Clearwater Formation in the Athabasca Oil Sands Area. The data that
    accompany this report are one of the most significant products of the project and will hopefully
     facilitate future development of the oil sands.” It includes well log curves as LAS
     files and tops in txt files and xls files. There is a word doc and a text file that
     describes the files and associated metadata.

    [Wynne1995]_
    _Wynne, D.A., Attalla, M., Berezniuk, T., Brulotte, M., Cotterill, D.K., Strobl, R.
    and Wightman, D. (1995): Athabasca Oil Sands data McMurray/Wabiskaw oil sands deposit
     - electronic data; Alberta Research Council, ARC/AGS Special Report 6._

    Please go to the links below for more information and the dataset:

    Report for Athabasca Oil Sands Data McMurray/Wabiskaw Oil Sands Deposit
    http://ags.aer.ca/document/OFR/OFR_1994_14.PDF

    Electronic data for Athabasca Oil Sands Data McMurray/Wabiskaw Oil Sands Deposit
    http://ags.aer.ca/publications/SPE_006.html

    In the metadata file
    https://github.com/JustinGOSSES/MannvilleGroup_Strat_Hackathon/blob/master/
    SPE_006_originalData/Metadata/SPE_006.txt -> SPE_006.txt.
    the dataset is described as Access Constraints: Public and Use Constraints:
    Credit to originator/source required. Commercial reproduction not allowed.

    _The Latitude and longitude of the wells is not in the original dataset.
    https://github.com/dalide -> @dalide used the Alberta Geological Society’s UWI
    conversion tool to find lat/longs for each of the well UWIs. A CSV with the
    coordinates of each well’s location can be found
    https://github.com/JustinGOSSES/MannvilleGroup_Strat_Hackathon/blob/master/well_lat_lng.csv.
    These were then used to find each well’s nearest neighbors.

    Please note that there are a few misformed .LAS files in the full dataset, so the code
    in this repository skips those.

    If for some reason the well data is not found at the links above, you should
    be able to find it
    https://github.com/JustinGOSSES/MannvilleGroup_Strat_Hackathon/tree/master/SPE_006_originalData

    If the file isn't already in your data directory, it will be downloaded
    automatically.

    Parameters
    ----------
    load : bool
        Wether to load the data into a :class:`pandas.DataFrame` or just return the
        path to the downloaded data.

    Returns
    -------
    mcmurray_facies : :class:`pandas.DataFrame` or str
        The loaded data or the file path to the downloaded data.
        The :class:`pandas.DataFrame` contains the following data:

        - columns of dataframe if abbreviationsOnly=True : ['CALI', 'COND', 'DELT', 'DEPT',
        'DPHI', 'DT', 'GR', 'ILD', 'ILM', 'NPHI', 'PHID', 'RHOB', 'SFL', 'SFLU', 'SN', 'SP',
         'UWI', 'SitID','lat', 'lng', 'Depth', 'LithID', 'W_Tar', 'SW', 'VSH', 'PHI', 'RW',
         'lithName']

        - columns of dataframe if abbreviationsOnly=False : ['CALI=Caliper',
         'COND=Fluid Conductivity', 'DELT=Travel Time Interval between Successive Shots',
        'DEPT=Depth', 'DPHI=Density Porosity',
        'DT=Delta-T also called Slowness or Interval Transit Time',
        'GR=Gamma Ray', 'ILD=Induction Deep Resistivity', 'ILM=Induction Medium Resistivity',
      'NPHI=Thermal Neutron Porosity (original Ratio Method) in Selected Lithology',
       'PHID=Porosity-LDT NGT Tools', 'RHOB=Bulk Density',
       'SFL=Spherically Focused Log Resitivity',
        'SFLU=SFL Resistivity Unaveraged', 'SN=Short Normal Resistivity (16 inch spacing)',
         'SP=Spontaneous Potential', 'UWI=Unique Well Identifier',
         'SitID=Site Identification Number',
         'lat=latitude', 'lng=longitude','Depth=Depth', 'LithID=Lithology Identity Number',
        'W_Tar=Weight Percent Tar', 'SW=Water Saturation', 'VSH=Volume of Shale', 'PHI=Porosity',
         'RW=Connate Water Resistivity','lithName=Lithology Name']

Continue adding in optionally from here: https://www.apps.slb.com/cmd/ChannelItem.aspx?code=SN
    """
    spelled_out_columns = ["Unnamed: 0", 'CALI=Caliper', 'COND=Fluid Conductivity',
    'DELT=Travel Time Interval between Successive Shots',
     'DEPT=Depth', 'DPHI=Density Porosity',
     'DT=Delta-T also called Slowness or Interval Transit Time',
      'GR=Gamma Ray', 'ILD=Induction Deep Resistivity', 'ILM=Induction Medium Resistivity',
      'NPHI=Thermal Neutron Porosity (original Ratio Method) in Selected Lithology',
       'PHID=Porosity-LDT NGT Tools', 'RHOB=Bulk Density',
       'SFL=Spherically Focused Log Resitivity',
        'SFLU=SFL Resistivity Unaveraged', 'SN=Short Normal Resistivity (16 inch spacing)',
         'SP=Spontaneous Potential', 'UWI=Unique Well Identifier',
          'SitID=Site Identification Number',
         'lat=latitude', 'lng=longitude', 'Depth=Depth', 'LithID=Lithology Identity Number',
        'W_Tar=Weight Percent Tar', 'SW=Water Saturation', 'VSH=Volume of Shale',
         'PHI=Porosity',
         'RW=Connate Water Resistivity', 'lithName=Lithology Name']
    abbreviated_columns = ["Unnamed: 0", 'CALI', 'COND', 'DELT', 'DEPT', 'DPHI', 'DT', 'GR',
     'ILD', 'ILM', 'NPHI', 'PHID', 'RHOB', 'SFL', 'SFLU', 'SN', 'SP', 'UWI', 'SitID', 'lat',
     'lng', 'Depth', 'LithID', 'W_Tar', 'SW', 'VSH', 'PHI', 'RW', 'lithName']

    # fname = REGISTRY.fetch("mcmurray_facies_v1.tar.gz")
    fname = REGISTRY.fetch("mcmurray_facies_v1.tar.gz", processor=Unzip())
    if not load:
        return fname

    try:
        # test_test = tarfile.open(fname, "r:xz")
        # test_test.extractall("mcmurray_facies_v1")
        data = pd.read_csv("mcmurray_facies_v1/mcmurray_facies_v1.csv", engine="python")
    except NotImplementedError:
        try:
            data = pd.read_csv(str(fname[0]))
        except NotImplementedError:
            data = "could not read hdf as the conversion of fname to a stringified version \
                 didn't work well. Oops."
            print(data)

    if abbreviations_only:
        data.rename(columns=abbreviated_columns)
    else:
        data.rename(columns=spelled_out_columns)
    return data
