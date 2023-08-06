from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
from typing import Union
from urllib.request import urlopen
from zipfile import ZipFile


FIELD_TYPES = { 
    # This is a type lookup for all QCEW data fields. For more information see:
    # https://www.bls.gov/cew/about-data/downloadable-file-layouts/quarterly/naics-based-quarterly-layout.htm
    # https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm
    "annual_avg_emplvl": int,
    "annual_avg_estabs_count": int,
    "annual_avg_wkly_wage": int,
    "annual_contributions": int,
    "agglvl_code": str,
    "agglvl_title": str,
    "area_fips": str,
    "area_title": str,
    "avg_annual_pay": int,
    "avg_wkly_wage": int,
    "disclosure_code": str,
    "industry_code": str,
    "industry_title": str,
    "lq_annual_avg_emplvl": float,
    "lq_annual_avg_estabs_count": float,
    "lq_annual_avg_wkly_wage": float,
    "lq_annual_contributions": float,
    "lq_avg_annual_pay": float,
    "lq_avg_wkly_wage": float,
    "lq_disclosure_code": str,
    "lq_month1_emplvl": float,
    "lq_month2_emplvl": float,
    "lq_month3_emplvl": float,
    "lq_qtrly_contributions": float,
    "lq_qtrly_estabs": float,
    "lq_qtrly_estabs_count": float,
    "lq_taxable_annual_wages": float,
    "lq_taxable_qtrly_wages": float,
    "lq_total_annual_wages": float,
    "lq_total_qtrly_wages": float,
    "month1_emplvl": int,
    "month2_emplvl": int,
    "month3_emplvl": int,
    "oty_annual_avg_emplvl_chg": int,
    "oty_annual_avg_emplvl_pct_chg": float,
    "oty_annual_avg_estabs_count_chg": int,
    "oty_annual_avg_estabs_count_pct_chg": float,
    "oty_annual_avg_wkly_wage_chg": int,
    "oty_annual_avg_wkly_wage_pct_chg": float,
    "oty_annual_contributions_chg": int,
    "oty_annual_contributions_pct_chg": float,
    "oty_avg_annual_pay_chg": int,
    "oty_avg_annual_pay_pct_chg": float,
    "oty_avg_wkly_wage_chg": int,
    "oty_avg_wkly_wage_pct": float,
    "oty_avg_wkly_wage_pct_chg": float,
    "oty_disclosure_code": str,
    "oty_month1_emplvl_chg": int,
    "oty_month1_emplvl_pct": float,
    "oty_month1_emplvl_pct_chg": float,
    "oty_month2_emplvl_chg": int,
    "oty_month2_emplvl_pct": float,
    "oty_month2_emplvl_pct_chg": float,
    "oty_month3_emplvl_chg": int,
    "oty_month3_emplvl_pct": float,
    "oty_month3_emplvl_pct_chg": float,
    "oty_qtrly_contributions_chg": int,
    "oty_qtrly_contributions_pct": float,
    "oty_qtrly_contributions_pct_chg": float,
    "oty_qtrly_estabs_chg": int,
    "oty_qtrly_estabs_pct_chg": float,
    "oty_qtrly_estabs_count_chg": int,
    "oty_qtrly_estabs_count_pct_chg": float,
    "oty_taxable_annual_wages_chg": int,
    "oty_taxable_annual_wages_pct_chg": float,
    "oty_taxable_qtrly_wages_chg": int,
    "oty_taxable_qtrly_wages_pct": float,
    "oty_taxable_qtrly_wages_pct_chg": float,
    "oty_total_annual_wages_chg": int,
    "oty_total_annual_wages_pct_chg": float,
    "oty_total_qtrly_wages_chg": int,
    "oty_total_qtrly_wages_pct": float,
    "oty_total_qtrly_wages_pct_chg": float,
    "own_code": str,
    "own_title": str,
    "qtr": str,
    "qtrly_contributions": int,
    "qtrly_estabs": int,
    "qtrly_estabs_count": int,
    "size_code": str,
    "size_title": str,
    "taxable_annual_wages": int,
    "taxable_qtrly_wages": int,
    "total_annual_wages": int,
    "total_qtrly_wages": int,
    "year": str,
    }


def get_qcew_data(year: str, annual: bool=False, fields: Union[list, None]=None) -> list:
    '''
    Returns all annual or quarterly QCEW data for a given `year`.

    ### Parameters
    `year` : str
        Reference year. NOTE: QCEW data are only available from 1990 onward.
    `annual` : bool (default: False)
        True for annual data. False for quarterly data. Defaults to False.
    `fields`: str or None (default: None)
        Names of fields to keep. Use None if keeping all fields. Defaults to None. NOTE: Specifying 
        fields will decrease memory usage and improve performance. Quarterly fields can be found at:
        https://www.bls.gov/cew/about-data/downloadable-file-layouts/quarterly/naics-based-quarterly-layout.htm
        Annual fields can be found at: https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm

    ### Returns
    list[dict] : Annual or quarterly QCEW data for a single year.
    '''
    if int(year) < 1990:
        raise ValueError('Invalid year arg. Data are only accessible from 1990 onward.')
    
    interval = "annual" if annual else "qtrly"
    url = f"https://data.bls.gov/cew/data/files/{year}/csv/{year}_{interval}_singlefile.zip"
    
    try:
        response = urlopen(url)
    except:
        raise ValueError((
            f'Cannot find URL: "{url}". These data may have not yet been published by BLS. For more'
            ' information, please see: https://www.bls.gov/cew/downloadable-data-files.htm.'
        ))
    else:
        zip = ZipFile(BytesIO(response.read()), "r")
        qcew_data = []
        with zip.open(zip.namelist()[0]) as input:
            field_names = parse_line(input.readline()) # Parse first line, which contains field names.
            keep_fields = fields if fields else field_names # Get the list of fields to keep
            field_types = { # Get the types of each kept field as well as their row index.
                f: {"type": FIELD_TYPES[f], "index": field_names.index(f)} for f in keep_fields
            }
            for line in input.readlines():
                row = parse_line(line)
                qcew_data.append({k: v["type"](row[v["index"]]) for k, v in field_types.items()})
        return(qcew_data)


def get_qcew_data_slice(slice_type: str, qcew_codes: list, years: list, annual_data: bool=False, 
                        fields: Union[list, None]=None) -> list:
    '''
    Returns a slice of QCEW data for a given area/industry/establishment size, for a range of years.
    
    NOTE: Yearly data slices are wrangled in parallel processes and then concatenated in order to 
    boost performance.
    
    ### Parameters
    `slice_type` : str
        Type of QCEW data, either: "area", "industry", or "size". Use "area" to get QCEW data for
        one or more areas. Use "industry" to get QCEW data for one or more industries. Use "size" to 
        get QCEW data for one or more establishment sizes.
    `qcew_codes` : list[str]
        The QCEW area/industry/establishment size code(s) of interest. Valid codes can be found at: 
        https://www.bls.gov/cew/classifications/.
    `years` : list[str]
        Reference year(s). NOTE: QCEW data are only available from 1975 onward, and data for 
        1975-1989 are only available for industry "10" (total, all industries).
    `annual_data` : bool (default: False)
        True for annual-interval data. False for quarterly-interval data. Defaults to False. NOTE: 
        QCEW data by establishment size are only available at the quarterly-interval.
    `fields`: str or None (default: None)
        Names of fields to keep. Use None if keeping all fields. Defaults to None. NOTE: Specifying 
        fields will decrease memory usage and improve performance. Quarterly fields can be found at:
        https://www.bls.gov/cew/about-data/downloadable-file-layouts/quarterly/naics-based-quarterly-layout.htm
        Annual fields can be found at: https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm

    ### Returns
    list[dict] : A slice of QCEW data.
    '''
    check_args(slice_type, qcew_codes, years, annual_data, fields)

    processes = [(slice_qcew, slice_type, qcew_codes, y, annual_data, fields) for y in years]
    with ProcessPoolExecutor() as multiprocessor:
        futures = [multiprocessor.submit(*process) for process in processes]
    
    qcew_data = []
    for future in futures:
        qcew_data += future.result()
    
    return(qcew_data)


def slice_qcew(slice_type: str, qcew_codes: list, year: str, annual_data: bool=False, 
               fields: Union[list, None]=None) -> list:
    '''
    Returns a slice of QCEW data for a given area/industry/establishment size, for a given `year`. 
    Data are read into memory from the web, without being stored on disk.

    ### Parameters
    `slice_type` : str
        Type of QCEW data, either: "area", "industry", or "size". Use "area" to get QCEW data for
        one or more areas. Use "industry" to get QCEW data for one or more industries. Use "size" to 
        get QCEW data for one or more establishment sizes.
    `qcew_codes` : list[str]
        The QCEW area/industry/establishment size code(s) of interest. Valid codes can be found at: 
        https://www.bls.gov/cew/classifications/.
    `year` : str
        Reference year. NOTE: QCEW data are only available from 1975 onward, and data for 1975-1989 
        are only available for industry "10" (total, all industries).
    `annual_data` : bool (default: False)
        True for annual-interval data. False for quarterly-interval data. Defaults to False. NOTE: 
        QCEW data by establishment size are only available at the quarterly-interval.
    `fields`: str or None (default: None)
        Names of fields to keep. Use None if keeping all fields. Defaults to None. NOTE: Specifying 
        fields will decrease memory usage and improve performance. Quarterly fields can be found at:
        https://www.bls.gov/cew/about-data/downloadable-file-layouts/quarterly/naics-based-quarterly-layout.htm
        Annual fields can be found at: https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm

    ### Returns
    list[dict] : A slice of QCEW data.
    '''
    check_args(slice_type, qcew_codes, [year], annual_data, fields)
    
    interval = "annual" if annual_data else "qtrly"
    if int(year) in range(1975, 1990):
        url = f"https://data.bls.gov/cew/data/files/{year}/csv/{year}_{interval}_naics10_totals.zip"
    else:
        if slice_type == "size":
            url = f"https://data.bls.gov/cew/data/files/{year}/csv/{year}_q1_by_size.zip"
        else:
            url = f"https://data.bls.gov/cew/data/files/{year}/csv/{year}_{interval}_by_{slice_type}.zip"

    try:
        response = urlopen(url)
    except:
        raise ValueError((
            f'Cannot find URL: "{url}". These data may have not yet been published by BLS. For more'
            ' information, please see: https://www.bls.gov/cew/downloadable-data-files.htm.'
        ))
    else:
        zip = ZipFile(BytesIO(response.read()), "r")
        
        files, codes_without_data = [], []
        if slice_type == "size":
            for file in zip.namelist():
                files.append(file)
        else:
            for qcew_code in qcew_codes:
                code_not_found = True
                for file in zip.namelist():
                    if f" {qcew_code} " in file:
                        files.append(file)
                        code_not_found = False
                if code_not_found:
                    codes_without_data.append(qcew_code)

        qcew_slice = []
        for file in files:
            with zip.open(file) as input:
                field_names = parse_line(input.readline()) # Parse first line, which contains field names.
                keep_fields = fields if fields else field_names # Get the list of fields to keep
                field_types = { # Get the types of each kept field as well as their row index.
                    f: {"type": FIELD_TYPES[f], "index": field_names.index(f)} for f in keep_fields
                }
                for line in input.readlines():
                    row = parse_line(line)
                    qcew_slice.append({k: v["type"](row[v["index"]]) for k, v in field_types.items()})
        
        if slice_type == "size":
            qcew_slice = [d for d in qcew_slice if d["size_code"] in qcew_codes]
        
        for qcew_code in codes_without_data:
            print(f"No {interval} data for {slice_type} {qcew_code} in {year}.")

        return(qcew_slice)


def parse_line(line: bytes) -> list:
    '''
    Returns a parsed list of values from a given `line` of bytes.

    ### Parameters
    `line` : bytes
        A byte object.

    ### Returns
    list[str] : A list of strings.
    '''
    row = line.decode('utf-8') # Decode the bytes using UTF-8.
    row = row.replace(', ', '| ') # Replace commas inside quotes with pipes.
    row = row.replace('"', '') # Remove double quotes.
    row = row.replace('\r\n','') # Remove escape characters.
    row = row.split(',') # Split the row at commas into a list of values.
    row = [v.replace('|', ',') for v in row] # Replace pipes back with commas.
    return(row)


def check_args(slice_type: str, qcew_codes: list, years: list, annual_data: bool, 
               fields: Union[list, None]) -> None:
    '''
    Runs a check on passed arguments.

    ### Parameters
    `slice_type` : str
        Type of QCEW data, either: "area", "industry", or "size". Use "area" to get QCEW data for
        one or more areas. Use "industry" to get QCEW data for one or more industries. Use "size" to 
        get QCEW data for one or more establishment sizes.
    `qcew_codes` : list[str]
        The QCEW area/industry/establishment size code(s) of interest. Valid codes can be found at: 
        https://www.bls.gov/cew/classifications/.
    `years` : list[str]
        Reference year(s). NOTE: QCEW data are only available from 1975 onward, and data for 
        1975-1989 are only available for industry "10" (total, all industries).
    `annual_data` : bool (default: True)
        True for annual-interval data. False for quarterly-interval data. Defaults to True. NOTE: 
        QCEW data by establishment size are only available at the quarterly-interval.
    `fields`: str or None (default: None)
        Names of fields to keep. Use None if keeping all fields. Specifying fields will improve
        performance. Defaults to None.

    ### Raises
    ValueError if:
        - `slice_type` requested is not one of: ["area", "industry", "size"].
        - Any year in `years` precedes 1975.
        - Area data are requested for any year between 1975 and 1989.
        - Size data are requested for any year between 1975 and 1989.
        - Industry data for any industry other than industry "10" are requested for any year between 1975 and 1989.
        - Annual-interval size data are requested.
        - If size data are requested for any size code other than "1", "2", "3", "4", "5", "6", "7", "8", and/or "9".

    ### Returns
    None
    '''
    if slice_type not in ['area', 'industry', 'size']:
        raise ValueError(
            'Invalid slice_type arg. Expected one of: ["area", "industry", "size"].'
        )
    for year in years:
        if int(year) < 1975:
            raise ValueError('Invalid years arg. QCEW data are only available from 1975 onward.')
        if int(year) in range(1975, 1990) and (slice_type != "industry" or qcew_codes != ["10"]):
            raise ValueError((
                'Invalid slice_type and/or qcew_codes arg(s). QCEW data from 1975 to 1989 are only'
                ' available for industry "10" (total, all industries). Try slice_type = "industry"'
                ' and qcew_codes = ["10"].'
            ))
    if slice_type == "size":
        if annual_data:
            raise ValueError((
                'Invalid annual_data arg. QCEW data by establishment size are only available at the'
                ' quarterly interval. Try annual_data = False.'
            ))
        for qcew_code in qcew_codes:
            if qcew_code not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                raise ValueError((
                    'Invalid qcew_codes arg. QCEW size codes allowable include: ["1", "2", "3",'
                    ' "4", "5", "6", "7", "8", "9"].'
                ))
        if fields and "size_code" not in fields:
            raise ValueError((
                'Invalid fields arg. The "size_code" field is needed in order to slice QCEW data'
                ' by establishment size. Specify the fields argument as a list with "size_code"'
                ' included or try fields = None.'
            ))

